"""Screenplay parser for tableread.py: units, dialogue, parentheticals, action lines."""
import re
def parse(path):
    L = open(path, encoding="utf-8").read().split("\n")
    units = []; cur = None; act = "Cold open"; inb = False; pend = None; actname = None
    def newunit(num, title, line):
        nonlocal cur
        cur = dict(num=num, title=title, target=None, act=act, items=[], line=line)
        units.append(cur)
    for i, l in enumerate(L):
        m = re.match(r"^# (COLD OPEN|ACT (ONE|TWO|THREE|FOUR)\b.*|TAG|WHAT WAS REAL.*)$", l)
        if m and not inb:
            h = m.group(1); act = h
            mm = re.match(r"ACT (\w+) — \"(.*)\"", h)
            if mm: actname = (mm.group(1).title(), mm.group(2))
            else: actname = None
            if h.startswith("WHAT WAS REAL"):
                newunit("WWR", "WHAT WAS REAL", i+1); cur["target"] = 40
            if actname: pend = ("act", actname)
            continue
        m = re.match(r"^### (\d+(?:–\d+)?) · (.*)$", l)
        if m and not inb:
            newunit(m.group(1), m.group(2).replace("*", ""), i+1)
            if pend: cur["act_title"] = pend[1]; pend = None
            continue
        m = re.search(r"\*\*Target:\*\* (\d+) s", l)
        if m and cur and not inb: cur["target"] = int(m.group(1)); continue
        if l.startswith("```"): inb = not inb; pend_cue = None; continue
        if not inb or cur is None: continue
        if not l.strip(): continue
        ind = len(l) - len(l.lstrip()); s = l.strip()
        if ind >= 25:
            cue = s; cur["items"].append(dict(kind="cue", text=s, line=i+1)); continue
        if ind >= 15 and s.startswith("("):
            # parenthetical (may wrap)
            cur["items"].append(dict(kind="paren", text=s, line=i+1)); continue
        if ind >= 10:
            cur["items"].append(dict(kind="dlg", text=s, line=i+1)); continue
        cur["items"].append(dict(kind="action", text=s, line=i+1))
    return units

def lines_of(unit):
    """Group items into spoken lines + action items in order. Returns list of dicts."""
    out = []; cue = None; pars = []; buf = []; first = None
    def flush():
        nonlocal buf, pars, first
        if buf and cue:
            out.append(dict(kind="line", cue=cue, parens=pars, text=" ".join(buf), line=first))
        buf = []; pars = []; first = None
    for it in unit["items"]:
        if it["kind"] == "cue": flush(); cue = it["text"]; continue
        if it["kind"] == "paren":
            if buf: flush(); pars = [it["text"]]   # mid-speech parenthetical: new chunk, same cue
            else: pars.append(it["text"])
            continue
        if it["kind"] == "dlg":
            if first is None: first = it["line"]
            buf.append(it["text"]); continue
        flush(); cue_keep = cue
        out.append(dict(kind="action", text=it["text"], line=it["line"]))
        cue = None if True else cue_keep
        # action ends the speech block
    flush()
    return out
