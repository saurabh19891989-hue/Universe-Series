"""THE SILVER HATCHET (inn) and ACTION: grapple, line, trunk, ramp/airlock, lift-off.

Vacuum rule applies to the action items: grapple, line-parting and lift-off are what the
hull and seats carry (low-passed, conducted); trunk, ramp and airlock are inside the ship (air)."""
from sfxlib import *
from sfx_rover_suits import _creak


def room(x, R, wet=0.15, rt=0.7):
    return reverb(x, R, rt60=rt, wet=wet, damp=5000, pre=0.008)


# ------------------------------------------------------------------ inn
@sfx("inn_stove_ignite_whup",
     "The squat iron stove lights: three piezo ticks, a small blue-flame 'whup' (soft sub thump with a "
     "burst of gas hiss) and a low flickering burn that settles. 2.2 s, stereo.",
     "10, 15, 31 (tag: the cold stove lights)", review=True, peak=-10, group="inn")
def stove(R):
    d = 2.2
    out = np.zeros(N(d))
    for tt, g in ((0.0, 0.7), (0.16, 0.8), (0.31, 0.9)):
        place(out, click(R, 4200, 2, 0.0015, 0.03) * g, tt)
        place(out, modal([2600], [0.3], [0.01], 0.04, R, True) * g, tt)
    t0 = 0.55
    place(out, thud(R, 85, 38, 0.09, 0.45, 0.5, 300) * 1.0, t0)
    place(out, np.sin(phase_of(np.linspace(90, 45, N(0.3)))) * ex(N(0.3), 0.07) * 0.6, t0)
    place(out, bp(white(R, 0.7), 1200, 6000, 2) * ad(0.7, 0.02, 0.12) * 0.35, t0 - 0.01)
    t = T(1.5)
    flame = lp(white(R, 1.5), 500, 2) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t + 1)) * np.exp(-t / 0.9)
    flame += bp(white(R, 1.5), 1500, 5000, 2) * 0.06 * np.exp(-t / 0.7)
    place(out, flame * 0.35, t0 + 0.1)
    return room(out, R, 0.1, 0.5)[:N(d)]


@sfx("inn_stove_burn_loop", "Small stove pilot-and-flame burn, soft flutter and gas hiss. Exact 8 s loop, mono.",
     "10, 11, 14, 15", loop=True, bed=-46, group="inn")
def stove_burn(R):
    L = 8.0
    t = np.arange(N(L)) / SR
    a = noise_loop(lambda R, d: lp(white(R, d), 500, 2), R, L, 0.4)
    b = noise_loop(lambda R, d: bp(white(R, d), 1500, 5500, 2), R, L, 0.4)
    a /= np.abs(a).max()
    b /= np.abs(b).max()
    return (a * (0.6 + 0.4 * np.sin(2 * np.pi * pf(7, L) * t) * np.sin(2 * np.pi * pf(0.3, L) * t + 1)) * 0.5 + b * 0.12)


@sfx("inn_quiet_room_metal_ticks_loop",
     "The parlour in quiet: faint rock-room air, a barely-there hum, and the odd tiny tick or three-tick "
     "run of metal warming (stove iron, brass). Exact 24 s loop, stereo.",
     "10, 11, 13, 14, 16", loop=True, review=True, bed=-46, group="inn")
def inn_quiet(R):
    L = 24.0
    n = N(L)
    t = np.arange(n) / SR
    x = noise_loop(lambda R, d: np.stack([lp(pink(R, d), 500, 2), lp(pink(R, d), 500, 2)], axis=1), R, L, 0.8)
    x = x / np.abs(x).max() * 0.18
    x += (0.03 * np.sin(2 * np.pi * pf(55, L) * t))[:, None]
    ev = np.zeros((n, 2))
    times = [2.0, 5.3, 5.55, 5.9, 9.4, 12.2, 12.5, 15.8, 18.7, 18.95, 19.2, 19.45, 22.1]
    for tt in times:
        place(ev, modal([R.uniform(900, 2200), R.uniform(2600, 3800)], [0.5, 0.2], [0.02, 0.01], 0.1, R, True) * R.uniform(0.2, 0.5),
              tt, 1.0, R.uniform(-.7, .7), wrap=True)
    return x + ev


@sfx("pen_scratch_long_signature",
     "A quill-or-nib pen writing a very long, magnificent signature: 17 strokes with lifts, a "
     "flourish and a long underline. Light paper texture. 6 s, mono.",
     "11 (the signature), 22 (the contract)", review=True, peak=-14, group="inn")
def pen(R):
    d = 6.0
    out = np.zeros(N(d))
    place(out, thud(R, 160, 110, 0.015, 0.05, 0.3, 700) * 0.4, 0.05)        # nib touches down
    tt = 0.2
    k = 0
    while tt < 5.1:
        dd = R.uniform(0.12, 0.45) * (1.9 if k == 14 else 1.0)
        n = N(dd)
        v = np.sin(np.pi * np.arange(n) / n) ** 1.2 * (0.6 + 0.4 * np.sin(2 * np.pi * R.uniform(5, 15) * np.arange(n) / SR + R.uniform(0, 6)))
        s = bp(white(R, dd), 2200, 7000, 2) * v * R.uniform(0.5, 1.0)
        s += bp(white(R, dd), 400, 1400, 2) * v * 0.25
        place(out, s, tt)
        tt += dd + R.uniform(0.02, 0.12)
        k += 1
    place(out, bp(white(R, 0.12), 3000, 8000, 2) * ad(0.12, 0.005, 0.03) * 0.2, tt)    # lift-off flick
    return out


@sfx("paper_slip_rustle", "A delivery slip slid and smoothed on a table: soft paper hush and small crinkle ticks. 1.8 s, mono.",
     "11", peak=-14, group="inn")
def paper(R):
    d = 1.8
    out = np.zeros(N(d))
    e = np.sin(np.pi * T(1.2) / 1.2) ** 1.5 * (0.5 + 0.5 * smooth_noise(R, 1.2, 8))
    place(out, bp(white(R, 1.2), 1500, 8000, 2) * e * 0.3, 0.05)
    for tt in R.uniform(0.1, 1.2, 12):
        place(out, click(R, R.uniform(3000, 6500), 2, 0.002, 0.02) * R.uniform(0.2, 0.6), tt)
    place(out, thud(R, 120, 80, 0.02, 0.08, 0.5, 900) * 0.3, 1.35)
    return out


@sfx("paper_card_slide_and_tap", "A card pushed across a table and left with a small tap (Chichikov's card/number). 1.0 s, mono.",
     "5, 16", peak=-14, group="inn")
def card(R):
    out = np.zeros(N(1.0))
    e = np.sin(np.pi * T(0.5) / 0.5) ** 0.8
    place(out, lp(white(R, 0.5), 3500, 2) * e * 0.22, 0.02)
    place(out, hp(white(R, 0.5), 1500, 2) * e * 0.06, 0.02)
    place(out, click(R, 1800, 2, 0.003, 0.04) * 0.5 + modal([900], [0.3], [0.02], 0.04, R, True), 0.55)
    return out


@sfx("frost_crack_ice_small",
     "A small crack of ice (the post horn's frost letting go): a sharp 'tk', a short glassy ring and "
     "a faint falling fracture. 0.7 s, mono. Music dept: the march comes after this.",
     "15", review=True, peak=-10, group="inn")
def ice_crack(R):
    out = np.zeros(N(0.7))
    place(out, click(R, 5500, 2.5, 0.0015, 0.05) * 1.0, 0.0)
    place(out, modal([3100, 4700, 7300, 9900], [0.5, 0.35, 0.2, 0.1], [0.06, 0.04, 0.03, 0.02], 0.3, R, True), 0.0)
    place(out, bp(white(R, 0.25), 1500, 6000, 2) * ad(0.25, 0.005, 0.05) * 0.15, 0.02)
    place(out, np.sin(phase_of(np.linspace(2800, 1400, N(0.18)))) * ex(N(0.18), 0.04) * 0.1, 0.03)
    return out


def _brass_drip(R, f, big=1.0):
    d = 1.4
    out = np.zeros(N(d))
    n = N(0.045)
    place(out, np.sin(phase_of(np.linspace(1300, 2900, n))) * ex(n, 0.012) * 0.45, 0.0)       # the drop
    place(out, click(R, 3000, 2, 0.002, 0.02) * 0.2, 0.0)
    place(out, modal([f, f * 2.0, f * 2.98, f * 4.1, f * 5.4], [0.35, 0.28, 0.2, 0.1, 0.06], [0.7, 0.45, 0.3, 0.2, 0.1], d, R, True) * big * 0.5, 0.012)
    return out


@sfx("brass_frost_drip_a", "One drop of thawed frost runs off the post horn's bell onto brass: plip and a faint brass ring (~620 Hz). 1.4 s.",
     "15", review=True, peak=-14, group="inn")
def drip_a(R):
    return _brass_drip(R, 620)


@sfx("brass_frost_drip_b", "A second drop, a little lower and wetter. 1.4 s.", "15", peak=-14, group="inn")
def drip_b(R):
    return _brass_drip(R, 585, 0.8)


@sfx("brass_thaw_metal_ticks", "Brass and iron ticking as they warm: seven small ticks, spacing stretching. 5 s, mono.",
     "15", peak=-16, group="inn")
def thaw_ticks(R):
    out = np.zeros(N(5.0))
    for tt in (0.2, 0.55, 1.1, 1.5, 2.4, 3.3, 4.4):
        place(out, modal([R.uniform(1000, 1900), R.uniform(2700, 3600)], [0.5, 0.2], [0.03, 0.015], 0.15, R, True) * R.uniform(0.4, 0.8), tt)
    return out


@sfx("post_horn_thaw_sequence",
     "Cue sheet in one file: ticks, a drip, more ticks, drip, and the ice crack at 7.4 s, then 1 s of "
     "room quiet for the music department's march to enter. 9 s, mono.",
     "15", review=False, peak=-12, group="inn")
def horn_seq(R):
    out = np.zeros(N(9.0))
    place(out, thaw_ticks(R) * 0.9, 0.0)
    place(out, _brass_drip(R, 620), 2.3)
    place(out, _brass_drip(R, 585, 0.8), 4.8)
    place(out, _brass_drip(R, 640, 0.9), 6.3)
    place(out, ice_crack(R), 7.4)
    return out


@sfx("cold_store_door_open",
     "A heavy insulated cold-store door opening: lever clunk, gasket peel, slow hinge groan, a rush of "
     "cold air, and a soft rubber bump at the end. 4.5 s, stereo (small cold room).",
     "15", review=True, peak=-8, group="inn")
def cold_door(R):
    d = 4.5
    out = np.zeros(N(d))
    place(out, thud(R, 150, 80, 0.05, 0.3, 0.3, 700) * 0.8, 0.0)
    place(out, modal([210, 430, 910], [0.5, 0.3, 0.2], [0.06, 0.04, 0.02], 0.2, R, True), 0.0)
    place(out, thud(R, 100, 55, 0.04, 0.15, 0.5, 500) * 0.6, 0.35)
    g = bp(white(R, 0.5), 150, 900, 2) * ad(0.5, 0.01, 0.12) * (0.6 + 0.4 * np.sin(2 * np.pi * 60 * T(0.5)))
    place(out, g * 0.6, 0.6)                                                  # gasket peel
    place(out, _creak(R, 2.2, 190, (18, 30)) * 0.7, 0.9)                        # hinge groan
    place(out, bp(pink(R, 2.5), 250, 1900, 2) * ad(2.5, 0.5, 1.2) * 0.4, 1.0)   # cold air out
    place(out, thud(R, 70, 45, 0.1, 0.4, 0.6, 400) * 0.6, 3.2)
    for tt in (3.5, 3.9):
        place(out, modal([R.uniform(2800, 5000)], [0.3], [0.02], 0.1, R, True) * 0.3, tt)   # frost falling
    return room(out, R, 0.22, 0.9)[:N(d)]


@sfx("breath_in_cold",
     "Breaths in cold air, two cycles of out-and-in; soft, slightly smoky exhale, a shivering inhale. "
     "Heard close, no voice. 5.5 s, mono.",
     "15", peak=-14, group="inn")
def breath_cold(R):
    out = np.zeros(N(5.5))
    for t0 in (0.2, 2.9):
        d1 = 1.5
        e1 = np.sin(np.pi * T(d1) / d1) ** 1.6
        place(out, (bp(pink(R, d1), 400, 4500, 2) * 0.8 + bp(white(R, d1), 4500, 9000, 2) * 0.05) * e1 * 0.5, t0)
        d2 = 1.0
        e2 = np.sin(np.pi * T(d2) / d2) ** 1.3 * (1 + 0.25 * np.sin(2 * np.pi * 9 * T(d2)))
        place(out, bp(pink(R, d2), 600, 3800, 2) * e2 * 0.5, t0 + 1.6)
    return out


@sfx("inlaid_box_lid_open",
     "Chichikov's little inlaid travelling box opens: tiny hinge creak and a soft wooden click. 1.1 s, mono.",
     "5, 12, 22", peak=-14, group="inn")
def box_open(R):
    out = np.zeros(N(1.1))
    place(out, _creak(R, 0.5, 900, (50, 90), 8) * 0.25, 0.05)
    place(out, click(R, 2000, 2, 0.003, 0.05) * 0.6 + modal([620, 1300], [0.4, 0.2], [0.04, 0.02], 0.05, R, True), 0.0)
    place(out, thud(R, 200, 130, 0.025, 0.1, 0.4, 900) * 0.5, 0.6)
    return out


@sfx("brass_recorder_click_and_tap",
     "Chichikov's small brass recorder: thumb click-off, and a tap on the brass device (two short events 0.7 s apart). 1.2 s.",
     "25 (brass device), 31 (recorder)", peak=-14, group="inn")
def recorder(R):
    out = np.zeros(N(1.2))
    place(out, click(R, 2400, 2, 0.003, 0.05) * 0.7 + modal([1500, 3000], [0.3, 0.12], [0.03, 0.02], 0.05, R, True), 0.0)
    place(out, modal([880, 1760, 2640], [0.5, 0.25, 0.1], [0.15, 0.1, 0.06], 0.4, R, True) * 0.5, 0.7)
    place(out, click(R, 2000, 2, 0.002, 0.03) * 0.3, 0.7)
    return out


# ------------------------------------------------------------------ action (hull-conducted)
@sfx("grapple_fire_hull_thunk",
     "A grapple line fired by the customs crawler, FELT in the rover: a dull launcher thump through the "
     "body, low rumble of cable paying out, fixtures buzzing faintly. No outside sound. All < 1 kHz. 2 s, stereo.",
     "29", review=True, conducted=True, peak=-8, group="action")
def grapple_fire(R):
    d = 2.0
    out = np.zeros((N(d), 2))
    place(out, thud(R, 120, 52, 0.11, 0.7, 0.35, 260), 0.0, 1.0, -0.1)
    place(out, modal([92, 140, 215, 340], [0.5, 0.35, 0.2, 0.1], [0.3, 0.2, 0.14, 0.1], 0.9, R, True) * 0.6, 0.0)
    pay = bp(white(R, 0.8), 70, 320, 2) * (0.5 + 0.5 * np.sin(2 * np.pi * 34 * T(0.8))) * np.sin(np.pi * T(0.8) / 0.8) ** 0.5
    place(out, pay * 0.4, 0.15, 1.0, 0.2)
    for tt in (0.45, 0.62, 0.8):
        place(out, thud(R, 100, 60, 0.03, 0.1, 0.4, 400) * 0.25, tt, 1.0, R.uniform(-.5, .5))
    return lp(out, 900, 4)


@sfx("grapple_cable_tension_groan",
     "The grapple line comes taut and the rover is dragged: a long stick-slip groan rising in pitch through "
     "the chassis, strands ticking faster, wheels' rumble. All < 1 kHz, conducted. 6 s, stereo.",
     "29", review=True, conducted=True, peak=-10, group="action")
def cable_groan(R):
    d = 6.0
    t = T(d)
    out = np.zeros((N(d), 2))
    f = 22 + 38 * (t / d) ** 1.4
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    k = t / d
    y = peakfilt(saw, 160, 6) * (1 - k) + peakfilt(saw, 290, 6) * k
    y *= (0.3 + 0.7 * (t / d) ** 0.8) * (1 + 0.25 * np.sin(2 * np.pi * 5.5 * t))
    y /= np.abs(y).max()
    out += (y * 0.8)[:, None]
    tt = 0.3
    while tt < d - 0.3:
        place(out, modal([R.uniform(300, 700)], [0.5], [0.02], 0.08, R, True) * (0.15 + 0.5 * tt / d), tt, 1.0, R.uniform(-.7, .7))
        tt += max(0.04, 0.45 * (1 - tt / d) ** 1.5 + 0.03) * R.uniform(0.6, 1.4)
    out += (lp(brown(R, d), 130, 3) * 1.5 * (0.3 + 0.7 * t / d))[:, None]
    return lp(out, 1000, 4)


@sfx("line_parting_snap_hull",
     "The line parts: a sharp conducted CRACK through the hull, the groan cut dead, a low recoil 'twang' "
     "and body ring-down. Felt, not heard outside (everything < 1.2 kHz). 2.4 s, stereo.",
     "29 (hatchet cuts the line)", review=True, conducted=True, peak=-8, group="action")
def line_snap(R):
    d = 2.4
    out = np.zeros((N(d), 2))
    place(out, bp(white(R, 0.04), 100, 1200, 2) * ex(N(0.04), 0.007) * 3.0, 0.0)
    place(out, thud(R, 100, 48, 0.12, 0.8, 0.4, 300) * 1.0, 0.005, 1.0, 0.0)
    place(out, modal([64, 118, 176, 240], [0.7, 0.5, 0.3, 0.15], [0.55, 0.4, 0.3, 0.2], 1.8, R, True) * 0.6, 0.005, 1.0, -0.2)
    f = 70 * (1 + 0.1 * np.exp(-T(1.2) / 0.1))
    place(out, np.sin(phase_of(f)) * ex(N(1.2), 0.35) * 0.4, 0.03, 1.0, 0.2)
    place(out, thud(R, 90, 55, 0.06, 0.25, 0.4, 300) * 0.4, 0.5, 1.0, 0.3)               # rover jumps free
    return lp(out, 1200, 4)


# ------------------------------------------------------------------ action (inside the ship)
@sfx("trunk_drag_up_metal_ramp",
     "Lucía heaves the LOT 14 trunk up the steel ramp inside the ship (air): wood scraping over a "
     "grated ramp, three heavier bumps over seams, one wood creak, a final settle. 6.5 s, stereo.",
     "29", review=False, peak=-9, group="action")
def trunk_drag(R):
    d = 6.5
    t = T(d)
    out = np.zeros((N(d), 2))
    heave = (0.35 + 0.65 * (np.sin(2 * np.pi * 0.9 * t) > -0.2).astype(float))
    heave = lp(heave, 6, 1)
    rung = 7 + 5 * t / d
    ph = np.cumsum(rung) / SR
    ridge = (np.abs(np.sin(np.pi * ph)) ** 6) * 0.9 + 0.1
    sc = bp(white(R, d), 180, 2800, 2) * ridge * heave
    sc += bp(white(R, d), 1000, 4500, 2) * 0.2 * ridge * heave
    out += (sc * 0.5)[:, None] * np.array([1.0, 0.85])
    for tt, g in ((1.4, 1.0), (3.1, 0.85), (4.7, 1.0)):
        place(out, thud(R, 90, 55, 0.07, 0.35, 0.4, 500) * g, tt, 1.0, -0.2)
        place(out, modal([310, 520, 780], [0.4, 0.3, 0.2], [0.15, 0.1, 0.07], 0.5, R, True) * 0.4 * g, tt, 1.0, 0.1)
    place(out, _creak(R, 0.9, 420, (30, 60), 7), 2.1, 0.5, 0.3)
    place(out, thud(R, 70, 45, 0.1, 0.5, 0.5, 400) * 1.0, 5.6)
    place(out, modal([150, 270, 410], [0.3, 0.2, 0.1], [0.3, 0.2, 0.1], 0.8, R, True) * 0.4, 5.6)
    for tt in (5.75, 5.85, 5.98):
        place(out, click(R, 3200, 2, 0.002, 0.03) * 0.2, tt, 1.0, R.uniform(-.8, .8))    # strap buckles
    return room(out, R, 0.2, 0.6)[:N(d)]


def _knock(R, f, g=1.0):
    d = 0.3
    x = modal([f, f * 2.05, f * 3.4], [0.8, 0.45, 0.2], [0.05, 0.03, 0.018], d, R, True)
    x += click(R, 1500, 2, 0.003, d) * 0.45
    x += thud(R, f * 0.9, f * 0.6, 0.03, d, 0.3, 500) * 0.5
    return lp(x, 1900, 2) * g


def _knocks(R, times, f, gains):
    out = np.zeros(N(2.0))
    for tt, g in zip(times, gains):
        place(out, _knock(R, f * R.uniform(0.96, 1.04), g), tt)
    return room(out, R, 0.28, 0.45)[:N(2.0)]


@sfx("trunk_knocks_inside_a", "Three small, polite knocks from INSIDE a wooden trunk, evenly spaced (variant A). Muffled by the lid; cargo-hold air. 2 s.",
     "31 (tag), 29", review=True, peak=-12, group="action")
def knock_a(R):
    return _knocks(R, (0.1, 0.55, 1.0), 150, (0.9, 0.85, 0.9))


@sfx("trunk_knocks_inside_b", "Three polite knocks, variant B: knock... knock-knock, a little hopeful. 2 s.", "31", peak=-12, group="action")
def knock_b(R):
    return _knocks(R, (0.1, 0.8, 1.1), 165, (0.9, 0.8, 0.85))


@sfx("trunk_knocks_inside_c", "Three polite knocks, variant C: slow and softer, dwindling, as if embarrassed to ask. 2 s.", "31", peak=-12, group="action")
def knock_c(R):
    return _knocks(R, (0.1, 0.7, 1.35), 140, (0.85, 0.65, 0.5))


@sfx("ramp_motor_conducted_thrum",
     "The ship's cargo ramp moving, heard in the cabin through the deck: gear thrum rising and falling, "
     "a few drive-chain ticks, a dull seat bump. Conducted (< 700 Hz). 3.6 s, mono.",
     "29 (ramp comes down / rises)", conducted=True, peak=-12, group="action")
def ramp_thrum(R):
    d = 3.6
    t = T(d)
    f = 70 + 40 * np.sin(np.pi * t / d)
    x = (np.sin(phase_of(f)) + 0.5 * np.sin(phase_of(2 * f)) + 0.25 * np.sin(phase_of(3 * f))) * np.sin(np.pi * t / d) ** 0.6 * 0.5
    x += lp(brown(R, d), 150, 3) * 1.2 * np.sin(np.pi * t / d)
    for tt in np.arange(0.4, 3.2, 0.31):
        place(x, thud(R, 110, 70, 0.02, 0.08, 0.5, 500) * 0.15, tt)
    place(x, thud(R, 80, 45, 0.08, 0.4, 0.3, 300) * 0.7, 3.2)
    return lp(x, 650, 4)


@sfx("ramp_close_and_airlock_cycle",
     "The ship's ramp closes and the airlock cycles (inside the ship, air): drive whine, heavy seal thump, "
     "three bolts thrown, pump spooling up with a rush of air, pressure equalising with a long 'pssht', "
     "then two soft ready pips. 11 s, stereo.",
     "29 (ramp rises)", review=True, peak=-9, group="action")
def airlock(R):
    d = 11.0
    out = np.zeros((N(d), 2))
    t = T(2.4)
    f = 85 + 25 * np.sin(np.pi * t / 2.4)
    mot = (np.sign(np.sin(phase_of(f))) * 0.25 + np.sin(phase_of(2 * f)) * 0.2) * np.sin(np.pi * t / 2.4) ** 0.5
    place(out, lp(mot, 1500, 2) * 0.7, 0.0)
    for tt in np.arange(0.3, 2.2, 0.17):
        place(out, click(R, 1800, 2, 0.002, 0.03) * 0.15, tt, 1.0, R.uniform(-.5, .5))
    place(out, thud(R, 80, 40, 0.14, 0.7, 0.5, 300) * 1.0, 2.5)                    # seal
    place(out, modal([160, 290, 560], [0.5, 0.3, 0.2], [0.2, 0.12, 0.07], 0.6, R, True) * 0.5, 2.5)
    for tt in (3.0, 3.35, 3.7):
        place(out, thud(R, 130, 80, 0.04, 0.15, 0.4, 700) * 0.8, tt)
        place(out, modal([320, 780, 1400], [0.4, 0.3, 0.2], [0.05, 0.03, 0.02], 0.2, R, True) * 0.6, tt)
    tp = T(5.2)
    pf_ = 110 + 90 * np.sin(np.pi * tp / 5.2)
    pump = (np.sin(phase_of(pf_)) + 0.4 * np.sin(phase_of(2 * pf_)) + 0.3 * np.sin(phase_of(6 * pf_ + 1))) * np.sin(np.pi * tp / 5.2) ** 0.7 * 0.3
    rush = bp(pink(R, 5.2), 900, 6500, 2) * np.sin(np.pi * np.clip(tp / 5.2, 0, 1)) ** 1.2 * 0.5
    place(out, pump + rush, 4.1)
    place(out, bp(pink(R, 1.8), 1200, 7000, 2) * ad(1.8, 0.03, 0.55) * 0.55, 8.9)       # pssht
    place(out, tone_burst(880, 0.12, 0.004, 0.03) * 0.18, 10.0)
    place(out, tone_burst(1174.7, 0.2, 0.004, 0.06) * 0.18, 10.2)
    return room(out, R, 0.2, 0.7)[:N(d)]


@sfx("liftoff_felt_in_cabin",
     "Lift-off as the cabin feels it (no sound outside): clamps' thump, a rising body tremor with sub sweep, "
     "three structural creaks, loose-item buzz, then acceleration eases into a steady hum. < 800 Hz "
     "conducted. 10 s, stereo.",
     "29 (ship lifts, far side)", review=True, conducted=True, peak=-8, group="action")
def liftoff(R):
    d = 10.0
    t = T(d)
    out = np.zeros((N(d), 2))
    amp = np.clip(t / 3.5, 0, 1) ** 1.5 * np.exp(-np.clip(t - 6.5, 0, None) / 1.8) * 0.9 + 0.12 * np.clip((t - 2) / 3, 0, 1)
    b1 = lp(brown(R, d), 140, 3) * 3.0
    b2 = lp(brown(R, d), 140, 3) * 3.0
    trem = 1 + 0.35 * np.sin(2 * np.pi * (7 + 4 * np.clip(t / 6, 0, 1)) * t) * np.clip(t / 4, 0, 1)
    sub = np.sin(phase_of(26 + 24 * np.clip(t / 6, 0, 1)))
    out[:, 0] = (b1 * trem + sub * 0.6) * amp
    out[:, 1] = (b2 * trem + sub * 0.6) * amp
    place(out, thud(R, 95, 40, 0.14, 0.8, 0.4, 200) * 1.0, 0.8)                      # clamps / ignition
    for tt, fc, p in ((2.2, 190, -0.3), (4.1, 240, 0.3), (6.0, 170, 0.0)):
        place(out, _creak(R, 1.0, fc, (20, 40)) * 0.5, tt, 1.0, p)
    for tt in R.uniform(2.5, 6.5, 24):
        place(out, modal([R.uniform(300, 700)], [0.5], [0.02], 0.08, R, True) * 0.12, tt, 1.0, R.uniform(-.8, .8))
    hum = np.sin(2 * np.pi * 48 * t) * np.clip((t - 5) / 3, 0, 1) * 0.12
    out += hum[:, None]
    return lp(out, 800, 4)
