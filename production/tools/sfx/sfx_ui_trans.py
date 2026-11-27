"""Interface sounds for the data visuals, and transitions."""
from sfxlib import *


def _blip(R, f, d=0.09, tau=0.02, g=1.0):
    t = T(d)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / tau) * g
    x += 0.4 * np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t / (tau * 0.5)) * g
    x[:N(0.0008)] *= np.linspace(0, 1, N(0.0008))
    return x


@sfx("ui_letter_blink_out",
     "One letter of the Atlas label blinks out: a tiny dry blip with a falling edge. 0.15 s, mono.",
     "2 (THE SILVER HATCHET loses letters)", peak=-14, group="ui")
def letter_blink(R):
    out = np.zeros(N(0.15))
    place(out, _blip(R, 2100, 0.1, 0.018), 0.0)
    place(out, np.sin(phase_of(np.linspace(1800, 700, N(0.05)))) * ex(N(0.05), 0.012) * 0.3, 0.01)
    return out


@sfx("ui_letters_blinking_out_run",
     "Letters blinking out from the end, one at a time, each blip a little lower and softer than the last "
     "(12 blips, holds after blips 2, 4 and 7 for the HATCH / HAT / SILVER stills). 4.6 s, mono.",
     "2", review=True, peak=-12, group="ui")
def letters_run(R):
    out = np.zeros(N(4.6))
    t = 0.1
    holds = {1: 0.55, 3: 0.6, 6: 0.7}
    for k in range(12):
        place(out, _blip(R, 2400 * (0.93 ** k), 0.1, 0.018, 1.0 - 0.04 * k), t)
        place(out, np.sin(phase_of(np.linspace(1900, 700, N(0.05)))) * ex(N(0.05), 0.012) * 0.25 * (1 - 0.04 * k), t + 0.01)
        t += 0.16 + holds.get(k, 0.0)
    return out


def _tink(R, f, g=1.0):
    d = 0.7
    out = np.zeros(N(d))
    place(out, modal([f, f * 2.32, f * 4.1], [0.7, 0.3, 0.12], [0.1, 0.05, 0.03], 0.5, R, True) * g, 0.0)
    place(out, click(R, 4500, 2, 0.001, 0.02) * 0.4 * g, 0.0)
    place(out, bp(white(R, 0.15), 3000, 9000, 2) * np.exp(-T(0.15) / 0.04) * 0.08 * g, 0.012)     # fizz of a lamp going out
    place(out, thud(R, 140, 90, 0.02, 0.06, 0.5, 700) * 0.2 * g, 0.015)
    return out


@sfx("ui_streetlamp_tink_out_a", "A tiny street-lamp 'tink' as one map name goes out (higher). 0.7 s.", "2 (HATCHET LANE, BEAN ROW, STRAW STAIRS)",
     peak=-14, group="ui")
def tink_a(R):
    return _tink(R, 3400)


@sfx("ui_streetlamp_tink_out_b", "Street-lamp tink, middle pitch. 0.7 s.", "2", peak=-14, group="ui")
def tink_b(R):
    return _tink(R, 2900)


@sfx("ui_streetlamp_tink_out_c", "Street-lamp tink, lower and duller. 0.7 s.", "2", peak=-14, group="ui")
def tink_c(R):
    return _tink(R, 2450, 0.9)


@sfx("ui_streetlamps_going_out_sequence",
     "The little street names go out like lamps: four tinks stepping down in pitch, then a soft low 'thunk' "
     "as the floor goes fully dark. 4 s, stereo.",
     "2", review=True, peak=-11, group="ui")
def lamps_seq(R):
    out = np.zeros((N(4.0), 2))
    for tt, f, g, p in ((0.1, 3500, 1.0, -0.5), (0.85, 3000, 0.9, 0.4), (1.7, 2600, 0.9, -0.2), (2.4, 2300, 0.8, 0.2)):
        place(out, _tink(R, f, g), tt, 1.0, p)
    place(out, thud(R, 90, 45, 0.12, 0.5, 0.3, 300) * 0.5, 3.1)
    return reverb(out.mean(axis=1), R, 1.0, 0.18, 6000)[:N(4.0)]


@sfx("ui_report_filed_blip",
     "A PIP report is filed: crisp two-tone blip (G5 up to D6) with a small ink-stamp tick under it. 0.7 s, mono.",
     "0, 2, 16, 30 (REPORT #1,204 ... #1,207)", review=True, peak=-12, group="ui")
def report_filed(R):
    out = np.zeros(N(0.7))
    place(out, _blip(R, 784, 0.16, 0.05), 0.02)
    place(out, _blip(R, 1174.7, 0.3, 0.09), 0.14)
    place(out, thud(R, 170, 100, 0.025, 0.1, 0.4, 900) * 0.4, 0.0)
    return out


@sfx("ui_report_read_receipt_tick",
     "The tiny grey 'READ' line appears under the report: one soft, low double-tick, deliberately underplayed. 0.4 s.",
     "30 (READ 00:00:01.3)", peak=-16, group="ui")
def read_receipt(R):
    out = np.zeros(N(0.4))
    place(out, _blip(R, 1320, 0.07, 0.015, 0.6), 0.0)
    place(out, _blip(R, 990, 0.09, 0.02, 0.5), 0.1)
    return out


@sfx("ui_screen_refresh_flicker",
     "A screen field refreshing: three little buzzing flicker bursts (CAPTAIN: VALE, JAX appears) then a "
     "blunt settle with a relay tick and a thin hum that stays. 1.6 s, mono.",
     "31 (the warrant field refreshes)", review=True, peak=-12, group="ui")
def refresh(R):
    out = np.zeros(N(1.6))
    for tt, dd, g in ((0.0, 0.14, 0.9), (0.2, 0.09, 0.6), (0.34, 0.2, 0.9)):
        n = N(dd)
        t = np.arange(n) / SR
        sq = np.sign(np.sin(2 * np.pi * 120 * t)) * 0.5 + 0.5
        s = bp(white(R, dd), 800, 5000, 2) * sq * 0.5 + np.sin(2 * np.pi * 1800 * t) * 0.15 * sq
        s *= np.minimum(np.arange(n) / (0.003 * SR), 1) * np.minimum((n - np.arange(n)) / (0.01 * SR), 1)
        place(out, s * g, tt)
    place(out, thud(R, 180, 100, 0.03, 0.1, 0.5, 900) * 0.5, 0.58)
    place(out, click(R, 2800, 2, 0.002, 0.03) * 0.5, 0.58)
    t = T(0.9)
    place(out, np.sin(2 * np.pi * 120 * t) * 0.07 * ex(N(0.9), 0.5) + np.sin(2 * np.pi * 7000 * t) * 0.01, 0.62)
    return out


@sfx("ui_late_popup_arrival",
     "A pop-up box arrives, too late: a polite rising 'bip-bup' (B5, E6) with a small hollow tail. 1 s, mono.",
     "28 (AUTHORITY TO LOCK -- RECEIVED)", review=True, peak=-12, group="ui")
def popup(R):
    out = np.zeros(N(1.0))
    place(out, _blip(R, 987.8, 0.25, 0.07), 0.0)
    place(out, _blip(R, 1318.5, 0.5, 0.14), 0.16)
    place(out, thud(R, 400, 250, 0.02, 0.05, 0.3, 1500) * 0.2, 0.0)
    return reverb(out, R, 0.5, 0.18, 6000).mean(axis=1)[:N(1.0)]


# ------------------------------------------------------------------ transitions
@sfx("smash_cut_main_title_hit",
     "SMASH TO: MAIN TITLE: instant full-bandwidth hit: noise slam, pitch-falling sub boom, metallic crash "
     "partials and a stamp-like body thump, then a long dark hall tail. Starts on sample 0 (1 ms fade). "
     "3.6 s, stereo.",
     "0 -> title", review=True, peak=-6, fade_in=0.001, fade_out=0.25, group="transition")
def smash(R):
    d = 3.6
    dry = np.zeros(N(d))
    t = T(d)
    place(dry, lp(white(R, 0.5), 9000, 2) * ex(N(0.5), 0.06) * 1.0, 0.0)
    sub = np.sin(phase_of(36 + 100 * np.exp(-t / 0.08))) * np.exp(-t / 0.55)
    place(dry, sub * 1.2, 0.0)
    place(dry, modal(R.uniform(500, 9000, 14), R.uniform(0.15, 0.5, 14), R.uniform(0.2, 0.7, 14), 2.0, R, True) * 0.9, 0.0)
    place(dry, thud(R, 200, 90, 0.12, 0.6, 0.5, 900) * 0.9, 0.0)
    place(dry, lp(brown(R, 2.4), 120, 3) * ad(2.4, 0.05, 0.9) * 5, 0.0)
    out = reverb(dry, R, 3.2, 0.45, 4500, pre=0.004)[:N(d)]
    return out


@sfx("cut_to_black_soft_tail",
     "Soft cut-to-black tail: the room tone sinks away under a slowly falling pair of low tones, "
     "high end rolling off, ending in silence. 4 s, stereo.",
     "0?, 31 (CUT TO BLACK), 15, 27", review=True, peak=-12, fade_in=0.01, fade_out=1.2, group="transition")
def to_black(R):
    d = 4.0
    t = T(d)
    out = np.zeros((N(d), 2))
    f = 220 * np.exp(-t / 3.0)
    tones = (np.sin(phase_of(f)) + 0.6 * np.sin(phase_of(f * 1.5)) + 0.3 * np.sin(phase_of(f * 2.0)))
    air = lp(pink(R, d), 900, 2)
    air2 = lp(pink(R, d), 900, 2)
    e = np.exp(-t / 1.2)
    out[:, 0] = (tones * 0.3 + air * 0.35) * e
    out[:, 1] = (np.roll(tones, 120) * 0.3 + air2 * 0.35) * e
    return out
