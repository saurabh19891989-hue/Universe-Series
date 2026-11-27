"""RIM PORT CUSTOMS HALL: hall tone, steps, stamps, gate and locks, scale, flip-board, klaxon,
clock, hold tone, console key, clamp."""
from sfxlib import *


def hall(x, R, wet=0.5, rt=4.5):
    return reverb(x, R, rt60=rt, wet=wet, damp=4500, pre=0.03)


# ------------------------------------------------------------------ tones and tails
@sfx("customs_hall_roomtone_loop",
     "Vast empty customs hall: faint low ventilation, huge air volume, distant far-off creaks and "
     "ticks each with a long reverb tail. Exact 30 s loop, stereo.",
     "3, 4, 6, 12, 18, 22, 25, 28, 31", loop=True, review=True, bed=-40, group="customs")
def hall_tone(R):
    L = 30.0
    n = N(L)
    t = np.arange(n) / SR

    def noisy(R, d):
        a = lp(brown(R, d), 110, 3) * 2.5 + bp(pink(R, d), 120, 900, 2) * 0.35
        b = lp(brown(R, d), 110, 3) * 2.5 + bp(pink(R, d), 120, 900, 2) * 0.35
        return np.stack([a, b], axis=1)
    x = noise_loop(noisy, R, L, 1.0)
    x /= np.abs(x).max()
    x *= (1 + 0.35 * np.sin(2 * np.pi * pf(0.1, L) * t + 0.3))[:, None] * 0.7
    x += (0.1 * np.sin(2 * np.pi * pf(50, L) * t) + 0.05 * np.sin(2 * np.pi * pf(100, L) * t + 1))[:, None]
    ev = np.zeros(n + N(8))
    for tt in R.uniform(1, L - 1, 7):
        kind = R.integers(0, 3)
        if kind == 0:
            e = modal([R.uniform(700, 1600)], [0.6], [0.015], 0.1, R, True)
        elif kind == 1:
            d = 0.9
            e = bp(white(R, d), 200, 700, 2) * np.abs(np.sin(2 * np.pi * (25 + 15 * T(d)) * T(d))) * np.sin(np.pi * T(d) / d)
        else:
            e = thud(R, 60, 38, 0.1, 0.4, 0.3, 300)
        place(ev, e, tt, R.uniform(0.3, 0.7))
    rv = reverb(ev, R, rt60=5.5, wet=1.0, damp=3500, pre=0.04)
    x += fold(rv[:n + N(7)], n) * 0.35
    return x


@sfx("customs_hall_reverb_tail_ir",
     "A synthetic hall impulse response (RT60 ~4.8 s, dark tail, stereo) the dialogue editor can "
     "convolve onto Mira, Jax or Noakes in the hall. 5.5 s. Not a sound effect; an IR.",
     "3, 4, 6, 12, 18, 22, 25, 28 (any hall dialogue)", peak=-12, fade_out=0.3, group="customs")
def hall_ir(R):
    ir = make_ir(R, 4.8, damp=5500, pre=0.025, d=5.5)
    ir[0] = 0
    ir[N(0.025)] += 4.0 * np.array([1, 0.8]) / 4          # direct-ish tick so it is usable as a one-shot
    return ir


@sfx("footsteps_lowg_distant_pattern",
     "Far-off footsteps across the empty hall in one-sixth gravity: slow, soft, long stride, each step "
     "a muffled pad with a light scuff, heavy hall reverb, walking slowly across the stereo field. 15 s.",
     "3, 18, 28", review=True, peak=-14, fade_out=0.8, group="customs")
def steps_lowg(R):
    d = 15.0
    dry = np.zeros(N(d))
    t0 = 0.4
    k = 0
    while t0 < 11.5:
        s = thud(R, 85, 50, 0.07, 0.35, 0.5, 450) * 0.8
        place(s, lp(white(R, 0.18), 1800, 2) * ad(0.18, 0.04, 0.05) * 0.18, 0.0)          # scuff
        place(dry, s, t0, R.uniform(0.75, 1.0))
        t0 += R.uniform(1.05, 1.45) + (0.3 if k % 5 == 4 else 0)       # slow, a pause now and then
        k += 1
    out = hall(dry, R, wet=0.72, rt=4.5)
    n = len(out)
    pan = np.linspace(0.3, 0.9, n)                                   # drifts to one side as it walks away
    out[:, 0] *= 1 - 0.5 * pan
    out[:, 1] *= 0.5 + 0.5 * pan
    return out[:N(d + 1.5)]


# ------------------------------------------------------------------ desk, gate, locks
def _desk_stamp(R, f0, tau, dur=1.0):
    t = T(dur)
    x = np.sin(phase_of(55 + (f0 - 55) * np.exp(-t / 0.025))) * np.exp(-t / tau)
    x += lp(white(R, dur), 450, 3) * ex(N(dur), 0.05) * 0.9          # heavy rubber face
    x += modal([f0 * 1.7, f0 * 2.9, f0 * 4.4], [0.4, 0.25, 0.12], [0.12, 0.08, 0.05], dur, R, True) * 0.5
    x += click(R, 1800, 2, 0.004, dur) * 0.35
    place(x, lp(white(R, 0.25), 600, 2) * ad(0.25, 0.02, 0.07) * 0.2, 0.06)   # squelch as it presses
    return x


@sfx("customs_desk_stamp_heavy_a", "Heavy customs rubber stamp onto a hardwood desk (SEIZED): big thump, squelch, deep desk ring. 1.2 s, stereo with light hall.",
     "3 (SEIZED)", review=False, peak=-8, group="customs")
def stamp_heavy_a(R):
    return hall(_desk_stamp(R, 110, 0.14, 1.2), R, 0.18, 3.5)


@sfx("customs_desk_stamp_heavy_b", "Heavy customs stamp, variant B (ABANDONED): a touch lower and drier. 1.2 s, stereo.",
     "18/19 (the stamp), 22, 28", peak=-8, group="customs")
def stamp_heavy_b(R):
    return hall(_desk_stamp(R, 95, 0.17, 1.2), R, 0.12, 3.5)


@sfx("wire_mesh_gate_rattle",
     "A wire-mesh cage gate rattled and shaken: dense bright little metal ticks, a looser frame clank "
     "underneath, dying away. 2.2 s, stereo.",
     "6 (holding bay)", peak=-10, group="customs")
def mesh_rattle(R):
    d = 2.2
    out = np.zeros(N(d))
    tt = 0.02
    while tt < 1.6:
        dens = 1 - tt / 2.0
        place(out, modal([R.uniform(1500, 5200), R.uniform(3000, 7000)], [0.5, 0.25], [R.uniform(.01, .04)] * 2, 0.15, R, True) * R.uniform(0.2, 0.8) * dens, tt)
        tt += R.uniform(0.004, 0.03)
    for tt2, g in ((0.03, 0.8), (0.27, 0.6), (0.55, 0.4), (0.9, 0.25)):
        place(out, modal([210, 330, 480], [0.5, 0.3, 0.2], [0.18, 0.12, 0.08], 0.5, R, True) * g, tt2)
    return hall(out, R, 0.2, 3.0)


@sfx("gate_latch_clunk_and_key",
     "Mira locks the cage gate behind them: key slides in, bolt thrown, heavy latch clunk. 1.4 s, stereo.",
     "6", peak=-10, group="customs")
def gate_latch(R):
    out = np.zeros(N(1.4))
    place(out, hp(white(R, 0.25), 2000, 2) * ad(0.25, 0.01, 0.06) * 0.25 * (0.6 + 0.4 * np.sin(2 * np.pi * 50 * T(0.25))), 0.0)  # key scrape
    place(out, click(R, 2600, 2, 0.003, 0.05) * 0.8, 0.3)
    place(out, modal([320, 640, 1250], [0.5, 0.3, 0.2], [0.1, 0.07, 0.04], 0.5, R, True), 0.55)
    place(out, thud(R, 90, 55, 0.12, 0.5, 0.4, 700) * 0.9, 0.55)
    return hall(out, R, 0.2, 3.0)


@sfx("padlock_rattle_old",
     "The Riga padlock refuses: old padlock and hasp rattled by hand, six shaken impacts with a dull "
     "iron ring. 1.5 s, mono (add hall).",
     "6 (the lock fails)", peak=-10, group="customs")
def padlock_rattle(R):
    out = np.zeros(N(1.5))
    for i, tt in enumerate((0.03, 0.2, 0.34, 0.5, 0.62, 0.8)):
        g = 1.0 - 0.1 * i
        place(out, modal([R.uniform(900, 1300), R.uniform(2200, 3200), 5400], [0.5, 0.3, 0.1], [0.05, 0.03, 0.015], 0.2, R, True) * g, tt)
        place(out, click(R, 1800, 2, 0.003, 0.04) * 0.6 * g, tt)
    place(out, modal([480, 710], [0.2, 0.1], [0.3, 0.2], 0.8, R, True), 0.8)
    return out


@sfx("padlock_click_open_clean",
     "The Riga padlock finally opens (tag, empty cage): one clean small spring 'tk', the shackle "
     "pops up with a light ring. Silent-grace-note: play dry, no reverb. 0.6 s, mono.",
     "31", review=True, peak=-12, group="customs")
def padlock_open(R):
    out = np.zeros(N(0.6))
    place(out, click(R, 4200, 2, 0.0015, 0.04) * 0.9, 0.02)
    place(out, modal([1900, 3300], [0.4, 0.2], [0.02, 0.01], 0.12, R, True), 0.02)
    place(out, modal([2350, 4700, 6900], [0.5, 0.2, 0.1], [0.22, 0.12, 0.07], 0.5, R, True) * 0.7, 0.11)
    place(out, click(R, 3000, 2, 0.002, 0.03) * 0.3, 0.11)
    return out


# ------------------------------------------------------------------ scale, board, clock
@sfx("cargo_scale_beep", "Cargo scale settles: one short, clean, slightly cheap beep (1.9 kHz). 0.4 s.",
     "3 (the Baron weighed)", peak=-12, group="customs")
def scale_beep(R):
    x = tone_burst(1900, 0.4, 0.004, 0.01) * np.where(T(0.4) < 0.28, 1, 0)
    x = np.sign(x) * 0.15 + x
    return lp(x, 5200, 2)


@sfx("cargo_scale_settle_beeps", "Cargo scale: a rising 'reading' tick-tick then the settled double beep. 1.4 s.",
     "3", peak=-12, group="customs")
def scale_settle(R):
    out = np.zeros(N(1.4))
    for i, tt in enumerate((0.0, 0.12, 0.25, 0.36, 0.46)):
        place(out, tone_burst(1100 + 150 * i, 0.05, 0.002, 0.01) * 0.5, tt)
    for tt in (0.75, 0.97):
        place(out, lp(tone_burst(1900, 0.18, 0.004, 0.01) * 1.0, 5200, 2), tt)
    return out


def _flap(R, big=1.0):
    d = 0.09
    x = click(R, R.uniform(2500, 3600), 2, 0.0025, d) * 0.8
    x += modal([R.uniform(900, 1300)], [0.35], [0.02], d, R, True)
    place(x, click(R, 3000, 2, 0.002, 0.04) * 0.5, 0.028)            # leaf lands
    return x * big


@sfx("flipboard_flap_single_a", "One split-flap leaf falls on the DAYS WITHOUT INCIDENT board: double click, hall tail. 1.2 s.",
     "4, 22, 31 (1,094 -> 0 starts)", review=False, peak=-12, group="customs")
def flap_a(R):
    return hall(_flap(R), R, 0.45, 3.5)[:N(1.2)]


@sfx("flipboard_flap_single_b", "One split-flap leaf, variant B (softer). 1.2 s.", "31", peak=-12, group="customs")
def flap_b(R):
    return hall(_flap(R, 0.7), R, 0.45, 3.5)[:N(1.2)]


@sfx("flipboard_run_down_to_zero",
     "The board runs down to zero: four digit drums riffle at ~18 flaps/s each and stop one after "
     "another (last to settle is the units), final clack, hall tail. ~6.5 s, stereo.",
     "31 (DAYS WITHOUT INCIDENT: 0)", review=True, peak=-9, group="customs")
def flap_run(R):
    d = 6.5
    out = np.zeros((N(d), 2))
    stops = [2.2, 3.3, 4.2, 5.1]
    pans = [-0.6, -0.2, 0.2, 0.6]
    for s, p in zip(stops, pans):
        tt = 0.15
        while tt < s:
            rate = 0.055 * (1 + 0.8 * max(0, (tt - (s - 0.6))) / 0.6)     # slows as it settles
            place(out, _flap(R, R.uniform(0.5, 0.9)), tt, 1.0, p)
            tt += rate * R.uniform(0.85, 1.15)
        place(out, _flap(R, 1.1), s, 1.2, p)                            # final clack
        place(out, modal([R.uniform(420, 520)], [0.4], [0.04], 0.15, R, True), s, 1.0, p)
    return hall(out, R, 0.35, 3.8)


@sfx("klaxon_seal_the_port_loop",
     "'Seal the port' klaxon: two alternating warning tones (G4 / D4) in a soft-edged pulse, "
     "low-passed at ~1.8 kHz so it is alarming but not painful; hall reverb baked in. Exact 6 s loop (6 cycles), stereo.",
     "22 (end), 23", loop=True, review=True, bed=-30, group="customs", pulsed=True)
def klaxon(R):
    L = 6.0
    n = N(L)
    cyc = 1.0
    seg = np.zeros(n)
    for k in range(6):
        for j, f in enumerate((392.0, 293.66)):
            dd = 0.48
            t = T(dd)
            ph = phase_of(np.full(len(t), f))
            s = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.33 * np.sin(3 * ph) + 0.2 * np.sin(5 * ph)
            e = np.minimum(t / 0.03, 1) * np.minimum((dd - t) / 0.05, 1)
            place(seg, s * e, k * cyc + j * 0.5, 1.0, wrap=True)
    seg = circ(lambda y: lp(y, 1800, 2), seg)
    return periodic_reverb(seg, R, 2.4, 0.28, 3500)


@sfx("wall_clock_tick", "One wall-clock tick (wooden/brass clock, dry). 0.15 s.", "22 (17:45), 25, 30", peak=-14, group="customs")
def clock_tick(R):
    return click(R, 2400, 2, 0.003, 0.15) * 0.8 + modal([1250, 2500], [0.5, 0.25], [0.03, 0.018], 0.15, R, True)


@sfx("wall_clock_tock", "One wall-clock tock (lower partner of the tick). 0.15 s.", "22, 25", peak=-14, group="customs")
def clock_tock(R):
    return click(R, 1700, 2, 0.003, 0.15) * 0.8 + modal([900, 1800], [0.5, 0.25], [0.04, 0.02], 0.15, R, True)


@sfx("wall_clock_ticking_loop", "Hall wall clock ticking, tick-tock once a second with a little room. Exact 8 s loop, stereo.",
     "22, 25, 28", loop=True, review=True, bed=-38, group="customs")
def clock_loop(R):
    L = 8.0
    out = np.zeros(N(L))
    for k in range(8):
        e = (clock_tick(R) if k % 2 == 0 else clock_tock(R)) * (0.9 + 0.1 * R.uniform())
        place(out, e, k * 1.0 + 0.5, wrap=True)
    return periodic_reverb(out, R, 2.5, 0.3, 4500)


# ------------------------------------------------------------------ headset, console, clamp
@sfx("headset_hold_tone_loop",
     "Earth-line headset on hold: low line hiss, faint hum, and a polite two-beep (A4 / E5) every 4 s "
     "(no melody). Narrow-band 'phone' filter. Exact 8 s loop, mono.",
     "25 (Noakes holds)", loop=True, review=False, bed=-40, group="customs")
def hold_tone(R):
    L = 8.0
    n = N(L)
    t = np.arange(n) / SR
    x = noise_loop(lambda R, d: bp(pink(R, d), 300, 3200, 2), R, L, 0.4) * 0.08
    x += 0.012 * np.sin(2 * np.pi * pf(50, L) * t) + 0.01 * np.sin(2 * np.pi * pf(150, L) * t)
    for k in (0, 1):
        place(x, tone_burst(440, 0.22, 0.01, 0.03) * 0.25, k * 4.0 + 0.3, wrap=True)
        place(x, tone_burst(659.3, 0.22, 0.01, 0.03) * 0.25, k * 4.0 + 0.6, wrap=True)
    place(x, click(R, 2500, 2, 0.001, 0.01) * 0.06, 2.1, wrap=True)
    place(x, click(R, 2000, 2, 0.001, 0.01) * 0.05, 6.4, wrap=True)
    return circ(lambda y: bp(y, 300, 3400, 2), x)


def _key(R):
    return click(R, 2800, 2, 0.003, 0.04) * 0.6 + modal([1400, 2900], [0.3, 0.15], [0.02, 0.01], 0.04, R, True)


@sfx("console_key_insert", "A console key slides into its slot: tiny scrape, small seat click. 0.5 s.", "25, 28", peak=-12, group="customs")
def key_insert(R):
    out = np.zeros(N(0.5))
    place(out, hp(white(R, 0.2), 2200, 2) * ad(0.2, 0.02, 0.06) * 0.15, 0.0)
    place(out, _key(R), 0.22)
    place(out, thud(R, 160, 90, 0.03, 0.1, 0.2, 800) * 0.5, 0.22)
    return hall(out, R, 0.1, 3.0)[:N(0.9)]


def _turn(R, final_f, lock):
    d = 1.3
    out = np.zeros(N(d))
    steps = 5
    for i in range(steps):
        place(out, click(R, 3000 - 150 * i, 2, 0.002, 0.03) * 0.5, 0.05 + i * 0.07)
    place(out, thud(R, final_f, final_f * 0.6, 0.06, 0.25, 0.35, 900), 0.45)
    place(out, modal([1100, 2200], [0.4, 0.2], [0.04, 0.02], 0.12, R, True), 0.45)
    if lock:
        place(out, tone_burst(1500, 0.06, 0.002, 0.01) * 0.2, 0.75)
    else:
        place(out, tone_burst(1000, 0.06, 0.002, 0.01) * 0.2, 0.75)
        place(out, tone_burst(1500, 0.08, 0.002, 0.01) * 0.2, 0.83)
    return hall(out, R, 0.12, 3.0)


@sfx("console_key_turn_lock", "Console key turned to LOCK: ratchet ticks, firm seat, one pip. 1.6 s.", "25, 28", peak=-10, group="customs")
def key_lock(R):
    return _turn(R, 120, True)


@sfx("console_key_turn_open", "Console key turned to OPEN (Mira): ratchet ticks, softer seat, two rising pips. 1.6 s.", "28",
     review=True, peak=-10, group="customs")
def key_open(R):
    return _turn(R, 95, False)


@sfx("console_key_withdraw", "Key drawn out of its slot: small scrape and release tick. 0.6 s.", "28", peak=-12, group="customs")
def key_withdraw(R):
    out = np.zeros(N(0.6))
    place(out, hp(white(R, 0.22), 2200, 2) * ad(0.22, 0.01, 0.07) * 0.14, 0.02)
    place(out, _key(R) * 0.7, 0.26)
    return out


@sfx("clamp_release_far_through_structure",
     "Bay-nine clamp opens, heard far away through the building's structure: hydraulic groan, bolts "
     "retracting, one huge 'ka-chunk', long dying rumble. All below ~450 Hz. 5.5 s, stereo.",
     "28 (Mira turns the key), 29", review=True, conducted=True, peak=-8, group="customs")
def clamp(R):
    d = 5.5
    out = np.zeros(N(d))
    t = T(d)
    g = bp(white(R, 2.0), 60, 260, 2) * (0.5 + 0.5 * np.sin(2 * np.pi * (11 + 8 * T(2.0) / 2.0) * T(2.0))) * np.sin(np.pi * T(2.0) / 2.0) ** 1.5
    place(out, g * 0.5, 0.1)
    for k, tt in enumerate((1.3, 1.62, 1.9, 2.25)):
        place(out, thud(R, 90 - 8 * k, 45, 0.1, 0.4, 0.3, 300) * 0.5, tt)
        place(out, modal([120, 190, 290], [0.4, 0.25, 0.12], [0.25, 0.2, 0.12], 0.8, R, True) * 0.35, tt)
    place(out, thud(R, 70, 30, 0.35, 1.8, 0.5, 200), 2.9)
    place(out, modal([54, 96, 150, 230, 340], [0.8, 0.5, 0.35, 0.2, 0.1], [1.4, 0.9, 0.7, 0.5, 0.3], 3.0, R, True) * 0.6, 2.9)
    place(out, lp(brown(R, 3.0), 90, 2) * ad(3.0, 0.1, 1.0) * 6, 2.9)
    out = lp(out, 420, 4)
    out = reverb(out, R, 2.4, 0.4, 600)[:N(d)]
    return lp(out, 450, 2)
