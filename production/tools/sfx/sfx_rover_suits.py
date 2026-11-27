"""THE POST-CHAISE (rover cabin; air inside, structure-borne sounds) and SUITS / RADIO.

Vacuum rule: nothing from outside.  Cabin sounds are what the cabin air and body carry."""
from sfxlib import *
from scipy import signal as sg


# ------------------------------------------------------------------ rover
def _cabin(R, L, power=1.0, rattle=1.0):
    n = N(L)
    t = np.arange(n) / SR

    def noisy(R, d):
        c = []
        for _ in range(2):
            c.append(lp(brown(R, d), 160, 3) * 2.2 * power + bp(pink(R, d), 250, 1200, 2) * 0.9 * power
                     + bp(pink(R, d), 600, 3000, 2) * 0.12)
        return np.stack(c, axis=1)
    x = noise_loop(noisy, R, L, 0.7)
    x /= np.abs(x).max()
    x *= (1 + 0.18 * np.sin(2 * np.pi * pf(1.6, L) * t))[:, None] * 0.6      # wheel / drive wobble
    f0 = pf(135 * (0.55 + 0.45 * power), L)
    mot = np.zeros(n)
    for h, a in ((1, 0.5), (2, 0.28), (3, 0.14), (5, 0.05)):
        mot += a * np.sin(2 * np.pi * f0 * h * t + 4.0 * np.sin(2 * np.pi * pf(0.2, L) * t) * 0.1 + h)
    x += (mot * 0.4 * (0.4 + 0.6 * power))[:, None]
    ev = np.zeros((n, 2))
    if rattle > 0:
        for tt in R.uniform(0, L, int(L * 14)):                           # loose trim rattle
            place(ev, modal([R.uniform(900, 2400)], [0.5], [0.012], 0.05, R, True), tt, R.uniform(0.03, 0.1) * rattle, R.uniform(-1, 1), wrap=True)
        for tt in R.uniform(0, L, int(L / 3)):                            # bumps
            place(ev, thud(R, 70, 45, 0.08, 0.3, 0.3, 300), tt, R.uniform(0.15, 0.4) * rattle, R.uniform(-.4, .4), wrap=True)
    return x + ev


@sfx("rover_cabin_hum_moving_loop",
     "Post-chaise cabin in motion: traction-motor hum (135 Hz stack), regolith rumble, heater-fan whisper, "
     "loose trim rattles and small bumps. Air inside the cab only. Exact 20 s loop, stereo.",
     "8, 17, 24, 26", loop=True, review=True, bed=-34, group="rover")
def cabin_moving(R):
    return _cabin(R, 20.0, 1.0, 1.0)


@sfx("rover_cabin_hum_cold_lowpower_loop",
     "Same cab late in the dark: motor sagging, fewer rattles (frozen mounts), heater only a whisper. "
     "Exact 16 s loop, stereo.",
     "27 (inner wall in the dark)", loop=True, bed=-38, group="rover")
def cabin_cold(R):
    return _cabin(R, 16.0, 0.5, 0.25)


def _creak(R, d, fc, f1=(24, 56), q=7, bright=1.0):
    t = T(d)
    f = np.linspace(f1[0], f1[1], len(t)) * (1 + 0.15 * np.sin(2 * np.pi * 3 * t))
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    y = peakfilt(saw, fc, q) * 3 + peakfilt(saw, fc * 2.1, q) * 1.5 * bright
    e = np.sin(np.pi * t / d) ** 1.5 * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * t))
    return y * e


@sfx("rover_suspension_creaks_conducted",
     "Suspension and body creaks conducted through the chassis (no outside air): five stick-slip "
     "groans and two dull thunks, low-passed at ~1.2 kHz. 7 s, stereo.",
     "8, 17, 24", review=False, conducted=True, peak=-12, group="rover")
def creaks(R):
    d = 7.0
    out = np.zeros((N(d), 2))
    for tt, dd, fc, g, p in ((0.2, 0.9, 260, 0.8, -0.4), (1.6, 0.6, 340, 0.6, 0.3), (2.7, 1.1, 210, 0.9, -0.2),
                             (4.3, 0.7, 380, 0.5, 0.5), (5.4, 1.0, 240, 0.8, 0.0)):
        place(out, _creak(R, dd, fc), tt, g, p)
    for tt, p in ((1.1, -0.2), (3.9, 0.2)):
        place(out, thud(R, 75, 45, 0.08, 0.35, 0.3, 300), tt, 0.7, p)
    return lp(out, 1200, 4)


@sfx("rover_airborne_dropout",
     "The leap over the gully: motor hum drops in pitch and dies, rattle and rumble cut at once, then a "
     "soft hushed 'weightless' swell. 3.2 s, stereo. Cabin air sounds only.",
     "24 (airborne beat)", review=True, peak=-12, group="rover")
def airborne_dropout(R):
    d = 3.2
    t = T(d)
    out = np.zeros((N(d), 2))
    f = 135 * np.exp(-t / 0.18) + 18
    mot = (np.sin(phase_of(f)) + 0.5 * np.sin(phase_of(2 * f))) * np.exp(-t / 0.2)
    rum = lp(brown(R, d), 160, 3) * 2.0 * np.exp(-t / 0.05)
    rat = np.zeros(len(t))
    for tt in R.uniform(0, 0.12, 6):
        place(rat, modal([R.uniform(900, 2400)], [0.5], [0.012], 0.05, R, True), tt, 0.15)
    base = (mot * 0.5 + rum * 0.6 + rat)
    out += base[:, None]
    # weightless hush: slow airy swell, detuned soft pad, lacking any rattle
    sw = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5 * np.clip((t - 0.2) / 0.5, 0, 1)
    pad = (np.sin(2 * np.pi * 196 * t) + 0.7 * np.sin(2 * np.pi * 196.8 * t) + 0.4 * np.sin(2 * np.pi * 293.7 * t)) * 0.06
    air = lp(pink(R, d), 700, 2) * 0.05
    st = np.stack([pad + air, np.roll(pad, 300) + np.roll(air, 700)], axis=1)
    out += st * sw[:, None]
    return out


@sfx("rover_airborne_hang_bed_loop",
     "Hanging in one-sixth gravity: cabin almost silent; a very faint body hum, soft hush of air, and "
     "a slow detuned pad that makes the quiet feel weightless. No rattle. Exact 8 s loop, stereo.",
     "24 (inside the cab while airborne)", loop=True, bed=-46, group="rover")
def airborne_hang(R):
    L = 8.0
    n = N(L)
    t = np.arange(n) / SR
    x = noise_loop(lambda R, d: np.stack([lp(pink(R, d), 600, 2), lp(pink(R, d), 600, 2)], axis=1), R, L, 0.5)
    x = x / np.abs(x).max() * 0.12
    pad = (np.sin(2 * np.pi * pf(196, L) * t) + 0.7 * np.sin(2 * np.pi * pf(196.75, L) * t) + 0.4 * np.sin(2 * np.pi * pf(293.75, L) * t))
    pad *= 0.1 * (0.6 + 0.4 * np.sin(2 * np.pi * pf(0.25, L) * t))
    hum = 0.05 * np.sin(2 * np.pi * pf(135, L) * t)
    x += (pad + hum)[:, None] * np.array([1, 0.9])
    return x


@sfx("rover_landing_thud_felt",
     "Wheels meet the dust: a thump FELT in the seat rather than heard: sub-bass hit at ~45 Hz, body "
     "boom, two suspension groans and small loose-item thumps (everyone drops an inch). All "
     "conducted/low-passed. 1.8 s, stereo.",
     "24 (landing)", review=True, conducted=True, peak=-8, group="rover")
def landing(R):
    d = 1.8
    out = np.zeros((N(d), 2))
    place(out, thud(R, 90, 42, 0.16, 0.8, 0.3, 200) * 1.0, 0.0, 1.0, 0.0)
    place(out, np.sin(2 * np.pi * 47 * T(0.9)) * ex(N(0.9), 0.17) * 0.6, 0.0)
    place(out, thud(R, 80, 45, 0.1, 0.5, 0.3, 200) * 0.5, 0.33, 1.0, 0.2)
    place(out, _creak(R, 0.5, 220), 0.1, 0.5, -0.3)
    place(out, _creak(R, 0.6, 300), 0.5, 0.35, 0.3)
    for tt in (0.12, 0.2, 0.28, 0.4):
        place(out, thud(R, 110, 70, 0.04, 0.15, 0.4, 400) * 0.25, tt, 1.0, R.uniform(-.6, .6))
    return lp(out, 800, 4)


@sfx("rover_heater_fan_failing",
     "The cab heater fan dies: blade whirr slows through a bent-blade tick, stutters, stalls, two last "
     "ticks and a relay click. 7 s, mono (cab air).",
     "27 (heater's dying)", review=True, peak=-12, group="rover")
def heater_fan(R):
    d = 7.0
    t = T(d)
    f = 190 * np.exp(-np.clip(t - 0.6, 0, None) / 2.0) + 5
    f = np.where(t > 5.0, f * np.exp(-(t - 5.0) / 0.25), f)
    stut = 1 - 0.7 * (np.sin(2 * np.pi * (1.2 + 0.9 * t) * t) > 0.5) * np.clip((t - 1.5) / 2.0, 0, 1)
    amp = np.where(t < 5.0, 1.0, np.exp(-(t - 5.0) / 0.5)) * stut
    x = np.sin(phase_of(f)) * 0.3 + np.sin(phase_of(f * 2.1)) * 0.1 + np.sign(np.sin(phase_of(f * 0.5))) * 0.04
    x += bp(white(R, d), 300, 2500, 2) * 0.25 * (f / 190)
    x *= amp
    # bent blade tick, once per revolution (10 blades -> f/10 rev/s)
    ph = phase_of(f / 10)
    rev = np.where(np.diff(np.floor(ph / (2 * np.pi)), prepend=0) > 0)[0]
    for i in rev:
        if i / SR < 5.3:
            place(x, click(R, 1800, 2, 0.002, 0.03) * 0.5 * (1 - 0.5 * (f[i] / 190)), i / SR)
    for tt, g in ((5.45, 0.5), (5.9, 0.35)):
        place(x, thud(R, 120, 70, 0.04, 0.12, 0.4, 500) * g, tt)
    place(x, click(R, 1800, 2, 0.003, 0.05) * 0.4, 6.4)
    return lp(x, 6000, 2)


def _frost(R, d, dens, squeal):
    out = np.zeros(N(d))
    tt = 0.05
    while tt < d - 0.3:
        place(out, modal([R.uniform(2800, 7500), R.uniform(4000, 9000)], [0.5, 0.3], [R.uniform(.004, .02)] * 2, 0.1, R, True) * R.uniform(0.1, 0.6), tt)
        tt += R.exponential(1 / dens)
    # tiny stick-slip squeal of ice sliding on the pane
    for ts in squeal:
        dd = 0.5
        f = np.linspace(2100, 3300, N(dd)) * (1 + 0.04 * np.sin(2 * np.pi * 14 * T(dd)))
        s = np.sin(phase_of(f)) * (np.sin(2 * np.pi * 38 * T(dd)) > 0.3) * np.sin(np.pi * T(dd) / dd) ** 2
        place(out, lp(s, 4500, 2) * 0.18, ts)
    return out


@sfx("frost_creak_on_glass_a", "Frost on the windscreen, first stage: sparse tiny ice ticks. 2.5 s, mono.", "27 (frost still 1)", peak=-14, group="rover")
def frost_a(R):
    return _frost(R, 2.5, 6, [])


@sfx("frost_creak_on_glass_b", "Frost on the windscreen, second stage: more ticks and one slow squeal of ice sliding. 2.8 s.",
     "27 (frost still 2)", review=True, peak=-14, group="rover")
def frost_b(R):
    return _frost(R, 2.8, 14, [0.9])


@sfx("frost_creak_on_glass_c", "Frost on the windscreen, third stage: dense crackle and two squeals. 3.2 s.", "27 (frost still 3)", peak=-14, group="rover")
def frost_c(R):
    return _frost(R, 3.2, 28, [0.4, 1.7])


@sfx("rover_headlamp_switch",
     "Headlamp switch: rocker click, relay clunk and a brief 100 Hz lamp-driver buzz. 0.6 s, mono.",
     "26 (Lights.)", peak=-10, group="rover")
def headlamp(R):
    out = np.zeros(N(0.6))
    place(out, click(R, 2600, 2, 0.003, 0.05) * 0.8, 0.0)
    place(out, modal([1200, 2300], [0.4, 0.2], [0.03, 0.015], 0.1, R, True), 0.0)
    place(out, thud(R, 160, 90, 0.04, 0.12, 0.4, 700) * 0.7, 0.07)
    t = T(0.3)
    place(out, np.sin(2 * np.pi * 100 * t) * np.sign(np.sin(2 * np.pi * 100 * t) + 0.3) * 0.05 * ex(N(0.3), 0.1), 0.1)
    return out


# ------------------------------------------------------------------ suits
def _suit(R, L, cycles, fan, center, wheeze=0.0, fan_amp=1.0, breath_amp=1.0):
    n = N(L)
    t = np.arange(n) / SR
    u = (t / L * cycles) % 1.0

    def env_in(u):
        return np.where(u < 0.42, np.sin(np.pi * u / 0.42) ** 2, 0.0)

    def env_out(u):
        return np.where((u > 0.5) & (u < 0.94), np.sin(np.pi * (u - 0.5) / 0.44) ** 2, 0.0)
    nin = noise_loop(lambda R, d: bp(pink(R, d), center * 0.5, center * 2.2, 2), R, L, 0.4)
    nout = noise_loop(lambda R, d: bp(pink(R, d), center * 0.35, center * 1.5, 2), R, L, 0.4)
    nin /= np.abs(nin).max()
    nout /= np.abs(nout).max()
    breath = (nin * env_in(u) * 0.55 + nout * env_out(u) * 0.38) * breath_amp
    if wheeze:
        breath += wheeze * np.sin(2 * np.pi * pf(2050, L) * t + 3 * np.sin(2 * np.pi * pf(5, L) * t)) * env_in(u) * 0.05
    af = noise_loop(lambda R, d: bp(pink(R, d), 1800, 5200, 2), R, L, 0.4)
    af = af / np.abs(af).max() * 0.05
    f = pf(fan, L)
    fn = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t + 1) + 0.25 * np.sin(2 * np.pi * pf(fan * 0.37, L) * t)
          + 0.15 * np.sin(2 * np.pi * 3 * f * t)) * 0.1 * fan_amp * (1 + 0.04 * np.sin(2 * np.pi * pf(0.6, L) * t))
    x = breath + af + fn
    ev = np.zeros(n)
    for k in range(cycles):                                  # valve tick between inhale and exhale
        place(ev, click(R, 2200, 2, 0.002, 0.02) * 0.05, (k + 0.46) * L / cycles, wrap=True)
    x = x + ev
    x = circ(lambda y: peakfilt(y, 1500, 1.2) * 0.5 + y * 0.8, x)     # small helmet-cavity bump
    return x


@sfx("suit_fan_breath_jax_loop",
     "Jax inside his helmet: steady suit fan (190 Hz) and calm, even breathing (4 s cycle, three per loop). "
     "The only sound an exterior shot carries. Exact 12 s loop, mono.",
     "9, 21, 29", loop=True, review=True, bed=-38, group="suits")
def suit_jax(R):
    return _suit(R, 12.0, 3, 190, 1500)


@sfx("suit_fan_breath_mira_loop",
     "Mira in her customs suit: higher, quieter fan (232 Hz) and quicker, tighter breathing (3 s cycle). "
     "Exact 12 s loop, mono.",
     "9, 29", loop=True, bed=-38, group="suits")
def suit_mira(R):
    return _suit(R, 12.0, 4, 232, 1700, fan_amp=0.8, breath_amp=0.8)


@sfx("suit_fan_breath_baron_loop",
     "The Baron in a patched old pressure suit: lower, wheezier fan (150 Hz, slightly rough), slow deep "
     "breaths (4.8 s cycle) with a faint whistle on the inhale. Exact 14.4 s loop, mono.",
     "9, 21, 29", loop=True, bed=-38, group="suits")
def suit_baron(R):
    return _suit(R, 14.4, 3, 150, 1200, wheeze=1.0, fan_amp=1.2, breath_amp=1.1)


@sfx("suit_fan_breath_lucia_loop",
     "Lucía in her suit: mid fan (205 Hz), strong, slightly fast breathing (3.4 s cycle). Exact 13.6 s loop, mono.",
     "9, 29", loop=True, bed=-38, group="suits")
def suit_lucia(R):
    return _suit(R, 13.6, 4, 205, 1450, breath_amp=1.1)


# ------------------------------------------------------------------ radio
@sfx("radio_click_on", "Suit radio key-up: small thump, crisp 'tk', 40 ms of hiss. 0.2 s, mono.",
     "9, 21, 26, 27, 29 (every radio line)", review=True, peak=-12, group="radio")
def radio_on(R):
    out = np.zeros(N(0.2))
    place(out, click(R, 2800, 2, 0.002, 0.04) * 0.8, 0.0)
    place(out, thud(R, 200, 120, 0.015, 0.05, 0.3, 900) * 0.5, 0.0)
    place(out, bp(white(R, 0.06), 600, 3800, 2) * ad(0.06, 0.003, 0.02) * 0.25, 0.01)
    return out


@sfx("radio_click_off", "Suit radio key-down: 'tk' then a short squelch tail of hiss. 0.28 s, mono.",
     "every radio line", review=True, peak=-12, group="radio")
def radio_off(R):
    out = np.zeros(N(0.28))
    place(out, bp(white(R, 0.12), 600, 3800, 2) * ad(0.12, 0.002, 0.035) * 0.3, 0.0)
    place(out, click(R, 2400, 2, 0.002, 0.04) * 0.7, 0.1)
    return out


@sfx("radio_private_channel_click",
     "Private-channel switch (the Baron and Jax): two soft rising pips with a small relay tick, "
     "clearly different from the open-channel click. 0.5 s, mono.",
     "21 ('A click. Private channel.')", review=True, peak=-12, group="radio")
def radio_private(R):
    out = np.zeros(N(0.5))
    place(out, click(R, 2000, 2, 0.002, 0.04) * 0.5, 0.0)
    place(out, tone_burst(1250, 0.07, 0.004, 0.02) * 0.35, 0.06)
    place(out, tone_burst(1700, 0.09, 0.004, 0.04) * 0.35, 0.15)
    place(out, bp(white(R, 0.2), 700, 3000, 2) * ad(0.2, 0.01, 0.05) * 0.08, 0.0)
    return out


@sfx("radio_open_channel_hiss_loop",
     "Open customs-channel hiss bed: wider band (250 Hz - 6.5 kHz), slow flutter, rare crackle pops. "
     "Mira on the open channel and Noakes O.S. sit on this. Exact 10 s loop, mono.",
     "27 (open channel), 28", loop=True, review=True, bed=-44, group="radio")
def open_hiss(R):
    L = 10.0
    n = N(L)
    t = np.arange(n) / SR
    x = noise_loop(lambda R, d: bp(white(R, d) * 0.4 + pink(R, d) * 0.6, 250, 6500, 2), R, L, 0.5)
    x /= np.abs(x).max()
    x = x * (1 + 0.3 * np.sin(2 * np.pi * pf(0.3, L) * t) + 0.15 * np.sin(2 * np.pi * pf(2.1, L) * t + 1)) * 0.5
    for tt in R.uniform(0, L, 14):
        place(x, click(R, R.uniform(1500, 4500), 2, 0.001, 0.012) * R.uniform(0.2, 0.6), tt, wrap=True)
    return x


@sfx("radio_suit_narrow_IR",
     "Impulse response for suit radio: narrow band ~450-2800 Hz with a slight 1.6 kHz presence lift. "
     "Linear-phase FIR (2049 taps, 1024-sample = 21 ms latency). Convolve (ffmpeg afir) or use the "
     "filter chain in radio-voice-presets.json. File peak is -6 dBFS: compensate gain after convolving.",
     "9, 21, 29, 8 (Mira on radio is always filtered)", fade_in=0, fade_out=0, peak=-12, group="radio",
     note="IR, not an effect", trim=False)
def ir_narrow(R):
    fr = [0, 250, 350, 450, 700, 1600, 2400, 2900, 3400, 4500, 24000]
    g = [0, 0, 0.06, 0.4, 1, 1.25, 1.0, 0.35, 0.05, 0, 0]
    return sg.firwin2(2049, fr, g, fs=SR)


@sfx("radio_open_wide_IR",
     "Impulse response for the open customs channel / console: wider ~300-5200 Hz, mild high-mid lift. "
     "Linear-phase FIR, 2049 taps (21 ms latency). Peak -6 dBFS.",
     "27, 28, 25", fade_in=0, fade_out=0, peak=-12, group="radio", note="IR, not an effect", trim=False)
def ir_wide(R):
    fr = [0, 180, 260, 320, 600, 2500, 4200, 5200, 6500, 24000]
    g = [0, 0, 0.1, 0.5, 1, 1.2, 0.9, 0.3, 0.03, 0]
    return sg.firwin2(2049, fr, g, fs=SR)
