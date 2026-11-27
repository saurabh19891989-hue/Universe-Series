"""THE UNSCHEDULED: bridge, cargo hold, engine, power, coffee machine, PIP, bank, comms."""
from sfxlib import *


def relay(R, hf=3500, lf=190, d=0.14):
    a = click(R, hf, 2, 0.0025, d)
    b = modal([lf, lf * 1.93], [0.7, 0.3], [0.03, 0.015], d, R, True)
    return a + b * 0.8


# ------------------------------------------------------------------ room tones
@sfx("ship_bridge_roomtone_loop",
     "Bridge room tone: worn courier cockpit. 60 Hz mains hum with a slightly sick beating partner, "
     "tired fan, thin electrical crackle and a few failing-ballast buzzes. Exact 24 s loop, stereo.",
     "0, 2, 17, 27, 30, 31 (bridge)", loop=True, review=True, bed=-38, group="ship")
def bridge_tone(R):
    L = 24.0
    n = N(L)
    t = np.arange(n) / SR
    # noise parts: fan + air, crossfaded loop, then periodic slow modulation
    def noisy(R, d):
        fan = bp(pink(R, d), 180, 1100, 2)
        fan2 = bp(pink(R, d), 180, 1100, 2)
        air = hp(white(R, d), 3500, 2) * 0.015
        air2 = hp(white(R, d), 3500, 2) * 0.015
        return np.stack([fan + air, fan2 + air2], axis=1)
    x = noise_loop(noisy, R, L, 0.6)
    x /= np.abs(x).max()
    lfo = 1 + 0.25 * np.sin(2 * np.pi * pf(0.25, L) * t + 1.0)
    x = x * lfo[:, None] * 0.55
    # tonal hum: all frequencies have integer cycles in L -> exact loop
    hum = np.zeros(n)
    for k, a in zip((1, 2, 3, 4, 6), (.5, .45, .25, .12, .05)):
        hum += a * np.sin(2 * np.pi * 60 * k * t + k)
    sick = 0.22 * np.sin(2 * np.pi * pf(61.5, L) * t)       # slow 1.5 Hz beat = unhealthy throb
    sick += 0.08 * np.sin(2 * np.pi * pf(183.0, L) * t + 2)
    hum = (hum + sick) * 0.35
    whine = 0.006 * np.sin(2 * np.pi * pf(7820, L) * t) * (1 + 0.5 * np.sin(2 * np.pi * pf(0.125, L) * t))
    x += (hum + whine)[:, None] * np.array([1.0, 0.92])
    # electrical crackle and failing-ballast buzz events (wrapped)
    ev = np.zeros((n, 2))
    for tt in R.uniform(0, L, 38):
        c = lp(click(R, R.uniform(2000, 6000), 2, 0.0008, 0.01), 7000, 2)
        place(ev, c, tt, R.uniform(0.02, 0.08), R.uniform(-1, 1), wrap=True)
    for tt in (3.4, 11.8, 17.9):
        d = R.uniform(0.12, 0.3)
        b = bp(white(R, d), 600, 3000, 2) * np.sign(np.sin(2 * np.pi * 120 * T(d))) * 0.25 * ad(d, 0.01, d / 2)
        place(ev, b, tt, 0.18, R.uniform(-.5, .5), wrap=True)
    x += ev
    return x


@sfx("ship_cargohold_tone_loop",
     "Cargo hold tone: big, empty, cold-ish metal volume; sub rumble from the reactor housing, "
     "vent air, a faint ringing panel and the odd far creak. Exact 24 s loop, stereo.",
     "1, 20, 31 (cargo hold)", loop=True, review=True, bed=-38, group="ship")
def cargo_tone(R):
    L = 24.0
    n = N(L)
    t = np.arange(n) / SR

    def noisy(R, d):
        rum = lp(brown(R, d), 130, 3) * 1.5
        rum2 = lp(brown(R, d), 130, 3) * 1.5
        vent = bp(pink(R, d), 300, 2600, 2) * 3.0
        vent2 = bp(pink(R, d), 300, 2600, 2) * 3.0
        return np.stack([rum + vent, rum2 + vent2], axis=1)
    x = noise_loop(noisy, R, L, 0.8)
    x /= np.abs(x).max()
    x *= (1 + 0.3 * np.sin(2 * np.pi * pf(0.083, L) * t + 0.5))[:, None] * 0.6
    ton = 0.25 * np.sin(2 * np.pi * pf(43, L) * t) + 0.12 * np.sin(2 * np.pi * pf(86.5, L) * t + 1)
    ton += 0.025 * np.sin(2 * np.pi * pf(312, L) * t) * (1 + np.sin(2 * np.pi * pf(0.17, L) * t))  # ringing panel
    x += ton[:, None] * 0.6
    ev = np.zeros((n + N(3), 2))
    for tt in (4.1, 13.7, 20.3):                          # far creaks
        d = 1.3
        g = bp(white(R, d), 150, 500, 2) * np.abs(np.sin(2 * np.pi * (30 + 10 * T(d)) * T(d)))
        g = g * np.sin(np.pi * T(d) / d) ** 2
        place(ev, g, tt, 0.28, R.uniform(-1, 1))
    ev = reverb(ev.mean(axis=1), R, rt60=2.2, wet=0.9, damp=2500)[:n + N(3)]
    x += fold(ev, n) * 0.5
    return x


# ------------------------------------------------------------------ engine
def engine_wave(f, amp, R, nh=14, rough=0.0, whine=0.0):
    """harmonic engine hum that follows pitch and amplitude curves"""
    ph = phase_of(f)
    x = np.zeros_like(ph)
    for h in range(1, nh + 1):
        x += np.sin(h * ph + h * 0.7) / h ** 0.9
    x = lp(x, 900, 2)
    nz = lp(white(R, len(f) / SR), 500, 2)
    x = x + nz * 0.35 * (f / max(f.max(), 1))
    if whine:
        x += whine * np.sin(18 * ph)
    return x * amp


@sfx("ship_engine_idle_loop",
     "Left-engine idle: low harmonic hum conducted through the ship (48 Hz fundamental, soft turbine "
     "whine). Exact 8 s loop; the engine comes back into this after the cough.",
     "0 (after restart), 1", loop=True, bed=-36, conducted=True, group="ship")
def engine_idle(R):
    L = 8.0
    n = N(L)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for h in range(1, 13):
        x += np.sin(2 * np.pi * 48 * h * t + h * 0.7) / h ** 0.9
    x *= 1 + 0.12 * np.sin(2 * np.pi * pf(6, L) * t)                  # firing flutter
    x *= 1 + 0.06 * np.sin(2 * np.pi * pf(0.5, L) * t)
    x = circ(lambda y: lp(y, 700, 2), x)
    nz = noise_loop(lambda R, d: lp(white(R, d), 450, 2), R, L, 0.4)
    x = x + 0.25 * nz + 0.03 * np.sin(2 * np.pi * pf(864, L) * t)
    return x


def _spindown(R, d=4.6):
    t = T(d)
    f = 48 * np.exp(-t / 1.15) + 3
    amp = np.exp(-t / 1.6) * (1 - 0.8 * np.clip((t - 1.4) / 2.2, 0, 1) ** 1.5)
    stut = 1 - 0.45 * (np.sin(2 * np.pi * (2.5 + t * 1.2) * t) > 0.2) * np.clip((t - 0.8) / 2.0, 0, 1)
    x = engine_wave(f, amp * stut, R, whine=0.01)
    wh = np.sin(phase_of(1200 * np.exp(-t / 0.9) + 60)) * np.exp(-t / 0.7) * 0.07   # turbine whine falls
    x = x + wh
    # mechanical last ticks and a hull ping as it stops
    for tt, g in ((2.05, 0.4), (2.75, 0.5), (3.5, 0.6)):
        place(x, relay(R, 1500, 120, 0.1) * g, tt)
    place(x, modal([95, 175, 410], [0.4, 0.25, 0.1], [0.5, 0.35, 0.2], 1.2, R, True) * 0.3, 3.55)
    return lp(x, 1800, 2)


@sfx("ship_engine_spindown",
     "The bank takes the left engine: hum sags in pitch and level with failing firing stutters, "
     "turbine whine falling, last mechanical ticks. ~4.6 s, low-passed (heard through the hull).",
     "0", conducted=True, peak=-10, group="ship")
def engine_spindown(R):
    return _spindown(R)


def _cough_restart(R, d=5.6):
    t = T(d)
    out = np.zeros(len(t))
    # two failed coughs
    for tt, f0, dur in ((0.15, 17, 0.28), (0.78, 21, 0.34)):
        n = N(dur)
        tc = np.arange(n) / SR
        f = f0 * (1 + 0.8 * tc / dur)
        s = harm(f, 10, 1.0) * ad(dur, 0.01, dur / 3)
        s += lp(white(R, dur), 300, 2) * ad(dur, 0.005, dur / 4) * 0.8
        place(out, lp(s, 800, 2), tt)
        place(out, relay(R, 1400, 140, 0.1) * 0.3, tt + dur)
    # third catches and runs up
    t0 = 1.5
    m = d - t0
    tc = T(m)
    f = 14 + 34 * (1 - np.exp(-tc / 0.9))
    f *= 1 + 0.06 * np.sin(2 * np.pi * 9 * tc) * np.exp(-tc / 1.0)         # roughness decaying
    amp = (1 - np.exp(-tc / 0.45)) * (1 + 0.5 * np.exp(-((tc - 0.9) / 0.25) ** 2))   # surge
    seg = engine_wave(f, amp, R, whine=0.01)
    seg += np.sin(phase_of(150 + 700 * (1 - np.exp(-tc / 1.0)))) * 0.05 * amp
    place(out, seg, t0)
    return lp(out, 1800, 2)


@sfx("ship_engine_cough_restart",
     "The left engine coughs back to life: two failed coughs, then it catches, surges and settles "
     "at idle. ~5.6 s, low-passed; fades into ship_engine_idle_loop. Place 1.3 s after the spin-down.",
     "0", conducted=True, peak=-10, group="ship")
def engine_cough(R):
    return _cough_restart(R)


@sfx("ship_engine_dies_and_returns",
     "Combined cold-open cue: spin-down, exactly 1.3 s of near-silence (faint hull tick), then "
     "the cough-restart. One file for the editor to drop under 'The one that has stopped' ... 'coughs back'.",
     "0", review=True, conducted=True, peak=-10, group="ship")
def engine_dies_returns(R):
    a = _spindown(R)
    gap = np.zeros(N(1.3))
    place(gap, relay(R, 1200, 100, 0.1) * 0.08, 0.6)
    b = _cough_restart(R)
    return np.concatenate([a, gap, b])


# ------------------------------------------------------------------ power
@sfx("ship_systems_powerdown_sequence",
     "Systems powering down one by one: five relay clicks, each cutting a layer (mains hum, buzz, "
     "whine, heater tick-hum), then the fan spins down to silence. ~8 s, mono.",
     "0 (nav lights, heating, coffee)", review=True, peak=-10, group="ship")
def powerdown(R):
    d = 8.0
    t = T(d)
    cut = [0.6, 1.7, 2.9, 4.0, 5.1]
    layers = [
        np.sin(2 * np.pi * 60 * t) + 0.5 * np.sin(2 * np.pi * 120 * t),
        bp(white(R, d), 900, 2600, 2) * 0.5 * (1 + np.sign(np.sin(2 * np.pi * 100 * t))),
        np.sin(2 * np.pi * 3100 * t) * 0.15,
        np.sin(2 * np.pi * 180 * t) * 0.4 * (1 + 0.5 * np.sin(2 * np.pi * 1.3 * t)),
    ]
    out = np.zeros(len(t))
    for i, lay in enumerate(layers):
        k = (t < cut[i]).astype(float)
        k = lp(k, 400, 1)
        out += lay * k * 0.45
    for c in cut:
        place(out, relay(R, 3200, 170) * 0.9, c - 0.003)
    # fan: blade tone + airflow, spinning down after last click
    ts = t - cut[-1]
    fan_f = np.where(ts < 0, 205, 205 * np.exp(-np.clip(ts, 0, None) / 1.1) + 4)
    fan_a = np.where(ts < 0, 1.0, np.exp(-np.clip(ts, 0, None) / 1.4))
    fan = np.sin(phase_of(fan_f)) * 0.4 + np.sin(phase_of(fan_f * 7)) * 0.1
    fan += bp(white(R, d), 300, 2500, 2) * 0.3 * (fan_f / 205)
    out += fan * fan_a * 0.5
    place(out, relay(R, 900, 90, 0.12) * 0.5, 6.7)                    # last blade tick
    out[N(7.3):] *= 0
    return out


@sfx("ship_systems_powerup_sequence",
     "Lights and heating return after the restart (not the coffee): three relay clicks, mains hum "
     "swelling back, metal ticking as the heater warms. ~4 s, mono.",
     "0", peak=-10, group="ship")
def powerup(R):
    d = 4.2
    t = T(d)
    out = np.zeros(len(t))
    for i, c in enumerate((0.15, 0.7, 1.25)):
        place(out, relay(R, 3000, 175) * 0.9, c)
        k = lp((t > c).astype(float), 300, 1)
        out += np.sin(2 * np.pi * (60 * (1 + i * 0.0)) * t) * 0.18 * k * (1 if i == 0 else 0.5)
        out += np.sin(2 * np.pi * 180 * (1 + i) * t) * 0.05 * k
    out += lp(pink(R, d), 600, 2) * 0.08 * lp((t > 1.4).astype(float), 3, 1)
    for tt in (1.9, 2.15, 2.6, 2.95, 3.5):
        place(out, modal([R.uniform(900, 1700), R.uniform(2400, 3300)], [0.5, 0.2], [0.02, 0.01], 0.1, R, True) * 0.5, tt)
    return out


@sfx("ship_relay_click_a", "Single small relay click, bright. 0.15 s.", "0, 30 (any switch)", peak=-12, group="ship")
def relay_a(R):
    return relay(R, 3800, 200)


@sfx("ship_relay_click_b", "Single relay click, duller and heavier. 0.17 s.", "0, 30 (any switch)", peak=-12, group="ship")
def relay_b(R):
    return relay(R, 2200, 130, 0.17)


@sfx("ship_fan_stop", "One cabin fan spinning down to a stop, with two last blade ticks. 3 s.", "0", peak=-14, group="ship")
def fan_stop(R):
    d = 3.0
    t = T(d)
    f = 210 * np.exp(-t / 0.9) + 3
    x = np.sin(phase_of(f)) * 0.4 + bp(white(R, d), 300, 2200, 2) * 0.3 * (f / 210)
    x *= np.exp(-t / 1.3)
    for tt in (1.9, 2.4):
        place(x, relay(R, 900, 90, 0.1) * 0.4, tt)
    return x


# ------------------------------------------------------------------ coffee
def _bubble(R, f0, d=0.05):
    t = T(d)
    f = f0 * (1 + 2.0 * t / d)
    return np.sin(phase_of(f)) * np.exp(-t / (d / 3)) * np.sin(np.pi * np.minimum(t / d, 1)) ** 0.5


@sfx("coffee_machine_last_gurgle",
     "The coffee machine's last gurgle: pump motor winding down, bubbles thinning out, steam hiss "
     "fading, final spit and one drip. ~3.2 s, mono.",
     "0", review=True, peak=-10, group="ship")
def coffee_last(R):
    d = 3.2
    t = T(d)
    out = np.zeros(len(t))
    mf = 105 * np.exp(-np.clip(t - 0.6, 0, None) / 0.9)
    out += np.sin(phase_of(mf)) * 0.4 * np.exp(-np.clip(t - 0.6, 0, None) / 0.8)
    out += hp(lp(white(R, d), 3500, 2), 1500, 2) * 0.12 * np.exp(-t / 0.9)       # steam
    tt = 0.05
    gap = 0.045
    while tt < 2.1:
        place(out, _bubble(R, R.uniform(280, 520), R.uniform(0.04, 0.09)) * R.uniform(0.3, 0.8), tt)
        tt += gap * R.uniform(0.6, 1.4)
        gap *= 1.07
    place(out, hp(white(R, 0.18), 600, 2) * ad(0.18, 0.005, 0.05) * 0.2, 2.2)       # final spit
    for tt2, g in ((2.65, 0.5),):
        drip = np.sin(phase_of(900 + 1500 * T(0.05) / 0.05)) * ex(N(0.05), 0.012)
        place(out, drip * g, tt2)
        place(out, modal([1300, 2600], [0.2, 0.1], [0.04, 0.02], 0.2, R, True), tt2 + 0.02)
    return lp(out, 8000, 2)


@sfx("coffee_machine_triumph_click_drip",
     "The coffee machine comes back: switch click and bright little 'ting', pump spins up, a short "
     "burst of bubbles, then slow satisfied drips into a cup. ~4 s, mono.",
     "30 (Lucía raps it with the spanner)", review=True, peak=-10, group="ship")
def coffee_triumph(R):
    d = 4.2
    t = T(d)
    out = np.zeros(len(t))
    place(out, relay(R, 2800, 210, 0.15) * 0.9, 0.05)
    place(out, modal([2400, 4800, 6300], [0.3, 0.14, 0.08], [0.18, 0.1, 0.06], 0.6, R, True), 0.08)
    ts = np.clip(t - 0.3, 0, None)
    mf = 105 * (1 - np.exp(-ts / 0.25))
    out += np.sin(phase_of(mf)) * 0.3 * lp((t > 0.3).astype(float), 20, 1) * np.exp(-np.clip(t - 1.8, 0, None) / 0.5)
    out += hp(lp(white(R, d), 3500, 2), 1500, 2) * 0.1 * np.clip((t - 0.4) / 0.3, 0, 1) * np.exp(-np.clip(t - 1.4, 0, None) / 0.5)
    tt = 0.5
    while tt < 1.8:
        place(out, _bubble(R, R.uniform(260, 520), R.uniform(0.04, 0.08)) * R.uniform(0.3, 0.7), tt)
        tt += R.uniform(0.03, 0.09)
    for tt, g, f in ((2.0, 0.8, 1100), (2.45, 0.7, 1250), (3.0, 0.8, 1150), (3.7, 0.7, 1300)):
        drip = np.sin(phase_of(f * 0.7 + f * 1.4 * T(0.06) / 0.06)) * ex(N(0.06), 0.014)
        place(out, drip * g * 0.6, tt)
        place(out, modal([R.uniform(1100, 1500), R.uniform(2300, 3000)], [0.2, 0.1], [0.05, 0.025], 0.25, R, True) * g, tt + 0.03)
        place(out, lp(white(R, 0.05), 3000, 2) * ex(N(0.05), 0.01) * 0.1, tt + 0.03)
    return lp(out, 9000, 2)


# ------------------------------------------------------------------ PIP
@sfx("pip_servo_swivel",
     "PIP's lens turns toward the shop-door chime: small precise servo whirr, pitch rises and falls "
     "with the move, stepper ripple, tiny settle click. ~1 s, mono.",
     "0", review=True, peak=-10, group="pip")
def pip_swivel(R):
    d = 1.0
    t = T(d)
    mv = np.sin(np.pi * np.clip(t / 0.82, 0, 1)) ** 2
    f = 420 + 380 * mv
    x = np.sign(np.sin(phase_of(f))) * 0.35 + np.sin(phase_of(f * 2)) * 0.25
    x *= 1 + 0.3 * np.sin(phase_of(f * 0.12))                # stepper ripple
    x = bp(x, 300, 4500, 2)
    x += bp(white(R, d), 800, 3000, 2) * 0.06
    x *= mv ** 0.7
    place(x, relay(R, 4200, 400, 0.05) * 0.6, 0.86)
    return x


@sfx("pip_servo_nudge", "A tiny two-step servo twitch (PIP re-aims his lens). 0.35 s.", "any PIP beat", peak=-14, group="pip")
def pip_nudge(R):
    d = 0.35
    t = T(d)
    out = np.zeros(len(t))
    for tt, f in ((0.02, 520), (0.17, 640)):
        s = np.sign(np.sin(phase_of(np.full(N(0.12), f) + 80 * T(0.12) / 0.12))) * 0.3 + np.sin(phase_of(np.full(N(0.12), f * 2))) * 0.2
        place(out, bp(s, 300, 4000, 2) * np.sin(np.pi * T(0.12) / 0.12) ** 0.6, tt)
    return out


def _stamp(R, f0, tau, body, rebound, dur=0.7, lowf=95):
    t = T(dur)
    x = np.sin(phase_of(lowf + (f0 - lowf) * np.exp(-t / 0.02))) * np.exp(-t / tau)
    x += lp(white(R, dur), body, 3) * ex(N(dur), 0.03) * 0.8                               # rubber face
    x += modal([f0 * 1.9, f0 * 3.1, f0 * 4.7], [0.3, 0.18, 0.1], [0.07, 0.05, 0.03], dur, R, True) * 0.6   # desk top
    x += click(R, 2200, 2, 0.003, dur) * 0.4
    if rebound:
        place(x, np.sin(phase_of(np.full(N(0.2), lowf * 1.3))) * ex(N(0.2), 0.04) * 0.25, rebound)
    return x


@sfx("pip_stamp_thunk_a", "PIP's rubber-stamp arm: THUNK, medium weight. 0.7 s.", "0 (Accepted), 2, 16, 30", review=True, peak=-8, group="pip")
def stamp_a(R):
    return _stamp(R, 150, 0.09, 700, 0.09)


@sfx("pip_stamp_thunk_b", "PIP's stamp, THUNK variant B: heavier, longer body. 0.75 s.", "0, 2, 16, 30", peak=-8, group="pip")
def stamp_b(R):
    return _stamp(R, 120, 0.13, 500, 0.12, 0.75, 80)


@sfx("pip_stamp_thunk_c", "PIP's stamp, THUNK variant C: crisp, drier, small desk ring. 0.6 s.", "0, 2, 16, 30", peak=-8, group="pip")
def stamp_c(R):
    return _stamp(R, 190, 0.06, 1100, 0.0, 0.6, 110)


@sfx("pip_lens_glow_bed_loop",
     "PIP's amber lens as a soft tone bed (220/330/440 Hz stack, slow breathing, a quiet 880 shimmer). "
     "Keyable under his voice: duck/raise with his speech. Exact 10 s loop, mono.",
     "every PIP line", loop=True, review=True, bed=-42, group="pip")
def pip_glow(R):
    L = 10.0
    n = N(L)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * pf(220, L) * t) * 0.5 + np.sin(2 * np.pi * pf(330.5, L) * t + 1) * 0.35 +
         np.sin(2 * np.pi * pf(440, L) * t + 2) * 0.3)
    x *= 1 + 0.18 * np.sin(2 * np.pi * pf(0.2, L) * t)
    x += 0.07 * np.sin(2 * np.pi * pf(880, L) * t) * (0.5 + 0.5 * np.sin(2 * np.pi * pf(0.5, L) * t))
    nz = noise_loop(lambda R, d: bp(pink(R, d), 600, 3000, 2), R, L, 0.4)
    return x * 0.5 + nz * 0.03


@sfx("pip_lens_glow_on", "PIP's lens lights: soft rising tone swell into the bed's chord. 1.4 s.", "0 (first frame), any PIP wake-up", peak=-14, group="pip")
def pip_on(R):
    d = 1.4
    t = T(d)
    e = (1 - np.exp(-t / 0.28)) * np.exp(-np.clip(t - 1.0, 0, None) / 0.2)
    f = 180 + 40 * (1 - np.exp(-t / 0.3))
    return (np.sin(phase_of(f)) + 0.7 * np.sin(phase_of(f * 1.5)) + 0.6 * np.sin(phase_of(f * 2))) * e


@sfx("pip_lens_glow_off", "PIP's lens dims: the tone falls away with a faint electrical tick. 0.9 s.", "any PIP sign-off", peak=-14, group="pip")
def pip_off(R):
    d = 0.9
    t = T(d)
    f = 220 * np.exp(-t / 0.5) + 60
    x = (np.sin(phase_of(f)) + 0.7 * np.sin(phase_of(f * 1.5))) * np.exp(-t / 0.22)
    place(x, relay(R, 2600, 200, 0.08) * 0.4, 0.0)
    return x


# ------------------------------------------------------------------ bank / door bell
def _mallet(f, d=1.2, tau=0.5, bright=1.0, R=None):
    return modal([f, f * 3.99, f * 9.2], [1, 0.25 * bright, 0.06 * bright], [tau, tau * 0.35, tau * 0.15], d, R, True) * (1 - np.exp(-T(d) / 0.0015))


@sfx("bank_chime",
     "The bank's cheerful chime: three soft mallet notes rising A5-C#6-F#6, last one held. Original "
     "figure, no brand reference. ~1.6 s, stereo.",
     "0 (before Temi)", review=True, peak=-9, group="bank")
def bank_chime(R):
    out = np.zeros((N(2.0), 2))
    for i, (f, g) in enumerate(((880, 0.8), (1108.7, 0.8), (1480, 1.0))):
        place(out, _mallet(f, 1.6 if i == 2 else 0.7, 0.55 if i == 2 else 0.25, 1.0, R) * g, 0.02 + i * 0.17, pan=-0.2 + 0.2 * i)
    return reverb(out.mean(axis=1), R, 0.8, 0.18, 7000)


@sfx("bank_jingle",
     "Bank jingle, original: bouncy 9-note D-major-pentatonic mallet tune over a soft shaker tick "
     "and a bright sparkle at the end. ~4.5 s, stereo. Composed from scratch (not derived from any brand sound).",
     "0 (Temi's call window), 30", review=True, peak=-9, group="bank")
def bank_jingle(R):
    out = np.zeros((N(5.2), 2))
    bpm = 126
    b = 60 / bpm
    notes = [(0, 740), (0.5, 880), (1, 987.8), (1.5, 1174.7), (2, 987.8), (2.5, 880), (3, 740), (3.5, 659.3), (4, 740)]
    for i, (bt, f) in enumerate(notes):
        last = i == len(notes) - 1
        place(out, _mallet(f, 1.8 if last else 0.6, 0.7 if last else 0.22, 1.0, R) * (0.9 if not last else 1.1), bt * b + 0.02, pan=-0.3 + 0.07 * i)
    for k in range(18):                                    # shaker on offbeats
        place(out, hp(white(R, 0.05), 5000, 2) * ad(0.05, 0.003, 0.012) * 0.12, k * b / 2 + b / 4, pan=0.4)
    for j, f in enumerate((2349, 2960, 3520, 4698)):         # sparkle
        place(out, _mallet(f, 0.8, 0.25, 1.0, R) * 0.28, 4 * b + 0.12 + j * 0.06, pan=-0.5 + 0.35 * j)
    # warm bass under the end
    place(out, np.sin(2 * np.pi * 146.8 * T(1.5)) * ex(N(1.5), 0.5) * 0.25, 4 * b)
    return reverb(out, R, 1.0, 0.16, 7000)


@sfx("shop_door_bell",
     "Old-fashioned shop-door bell on a curled spring: two quick clapper strikes, a brass ring-out "
     "with inharmonic partials and a little spring jangle. ~2.4 s, stereo.",
     "0 (the job arrives)", review=True, peak=-9, group="bank")
def shop_bell(R):
    d = 2.6
    out = np.zeros(N(d))
    f = 2310
    for tt, g in ((0.01, 1.0), (0.085, 0.75), (0.31, 0.45)):
        place(out, modal([f, f * 2.4, f * 4.1, f * 5.9, f * 1.18], [1, .45, .22, .12, .3], [0.9, .45, .25, .15, 0.7], 2.4, R, True) * g * 0.7, tt)
        place(out, bp(white(R, 0.12), 3000, 8000, 2) * ad(0.12, 0.002, 0.03) * 0.25 * g, tt)
    place(out, bp(white(R, 0.6), 600, 2500, 2) * ad(0.6, 0.01, 0.2) * 0.04, 0.0)           # spring
    return reverb(out, R, 0.7, 0.14, 6000)


# ------------------------------------------------------------------ comms
@sfx("comm_line_connect",
     "A comm line connects: squelch-open click, double rising two-tone chirp, line hiss blooms and "
     "settles low. ~1.4 s, mono.",
     "0 (Temi), 25, 30", review=False, peak=-12, group="comm")
def comm_connect(R):
    d = 1.4
    t = T(d)
    out = np.zeros(len(t))
    place(out, click(R, 2500, 2, 0.003, 0.06) * 0.7, 0.0)
    for tt, f0, f1 in ((0.08, 1000, 1300), (0.26, 1300, 1700)):
        n = N(0.12)
        ff = np.linspace(f0, f1, n)
        place(out, np.sin(phase_of(ff)) * np.sin(np.pi * np.arange(n) / n) ** 0.5 * 0.4, tt)
    hiss = bp(white(R, d), 400, 4500, 2) * np.clip((t - 0.05) / 0.12, 0, 1) * (0.25 + 0.75 * np.exp(-np.clip(t - 0.45, 0, None) / 0.2)) * 0.12
    return out + hiss


@sfx("comm_line_disconnect",
     "A comm line drops: hiss cuts with a squelch tail, one falling beep, a small click. ~1 s, mono.",
     "0, 5, 30", peak=-12, group="comm")
def comm_disc(R):
    d = 1.0
    t = T(d)
    hiss = bp(white(R, d), 400, 4500, 2) * 0.1 * np.exp(-np.clip(t - 0.04, 0, None) / 0.03) * (t < 0.3)
    n = N(0.22)
    ff = np.linspace(1500, 750, n)
    beep = np.sin(phase_of(ff)) * np.sin(np.pi * np.arange(n) / n) ** 0.5 * 0.4
    out = hiss
    place(out, beep, 0.1)
    place(out, click(R, 2200, 2, 0.003, 0.05) * 0.5, 0.36)
    return out


@sfx("earth_call_dead_air_1p3s",
     "The 1.3 s 'dead air' of an Earth call: not silence but a subtle open line: low band-limited line "
     "noise, a faint carrier hum and two tiny ticks. Exactly 1.3 s with 40 ms edges, mono. Mix very low.",
     "0, 25, 28", review=True, bed=-52, fade_in=0.04, fade_out=0.04, group="comm", trim=False)
def dead_air(R):
    d = 1.3
    x = bp(pink(R, d), 250, 3400, 2) * 0.35
    x += np.sin(2 * np.pi * 50 * T(d)) * 0.03 + np.sin(2 * np.pi * 150 * T(d)) * 0.012
    place(x, click(R, 3000, 2, 0.001, 0.01) * 0.12, 0.38)
    place(x, click(R, 2000, 2, 0.001, 0.01) * 0.1, 0.91)
    return x


@sfx("wristcomm_buzz", "Wrist-comm vibration buzz against bench/table: two pulses of 170 Hz with a rattle. 0.7 s.", "5, 11, 16", peak=-10, group="comm")
def wrist_buzz(R):
    d = 0.7
    t = T(d)
    out = np.zeros(len(t))
    for tt in (0.02, 0.33):
        n = N(0.24)
        tc = np.arange(n) / SR
        e = np.minimum(tc / 0.01, 1) * np.minimum((0.24 - tc) / 0.02, 1)
        s = (np.sign(np.sin(2 * np.pi * 172 * tc)) * 0.4 + np.sin(2 * np.pi * 172 * tc)) * (1 + 0.5 * np.sin(2 * np.pi * 30 * tc)) * e
        s += bp(white(R, 0.24), 1500, 4500, 2) * e * 0.25 * (np.sign(np.sin(2 * np.pi * 172 * tc)) > 0)
        place(out, lp(s, 3500, 2), tt)
    return out


@sfx("wristcomm_click", "Wrist-comm button/hang-up click: small plastic click. 0.12 s.", "5 (Lucía hangs up), 7", peak=-12, group="comm")
def wrist_click(R):
    return click(R, 3000, 2, 0.004, 0.1) + modal([1700], [0.4], [0.012], 0.1, R, True)


@sfx("wristcomm_notice_chime", "Mira's wrist chime (LOT 14 PUBLIC SALE): two soft descending notes. 0.9 s.", "6", peak=-12, group="comm")
def wrist_chime(R):
    out = np.zeros(N(0.9))
    place(out, _mallet(1568, 0.5, 0.2, 0.5, R), 0.0)
    place(out, _mallet(1175, 0.7, 0.3, 0.5, R), 0.2)
    return out
