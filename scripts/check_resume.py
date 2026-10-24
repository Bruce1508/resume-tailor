#!/usr/bin/env python3
"""Mechanical resume checks for the AGENTS.md workflow (STEP 6 and Section 5).

  python3 scripts/check_resume.py resume.tex [--keywords jd_keywords.txt]
  python3 scripts/check_resume.py --stop-hook      (Claude Code Stop hook, see .claude/settings.json)

FAIL = a hard rule is broken and must be fixed. WARN = fix it or justify it in the final report.
Reads profile/never_claim.md and jd_keywords.txt (one keyword per line, top 5 first) when present.
Needs latexmk, pdfinfo and pdftotext (poppler). Python standard library only.
"""
import hashlib
import json
import re
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEVER_CLAIM_FILE = ROOT / "profile" / "never_claim.md"
CACHE_FILE = ROOT / ".claude" / ".check_cache.json"
BUZZWORDS = ["synergy", "go-getter", "thought leader", "hardworking", "dynamically managed",
             "results-driven", "passionate", "detail-oriented", "team player"]
BANNED_HEADINGS = re.compile(r"summary|profile|objective|about", re.I)
SECTION_ORDER = ["Experience", "Projects", "Education", "Skills"]
HEATMAP_WORDS = 7  # recruiters read the left edge (F-pattern): the metric must land this early


def word_re(pat, flags=0):
    return re.compile(r"(?<![\w.&])" + pat + r"(?![\w&])", flags)


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=180)


def load_never_claim(path=NEVER_CLAIM_FILE):
    """Return (never_anywhere, skills_line_only) term lists from profile/never_claim.md."""
    anywhere, skills_only, bucket = [], [], None
    if not path.exists():
        return anywhere, skills_only
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            low = line.lower()
            bucket = skills_only if "skills" in low else anywhere if "never" in low else None
        elif bucket is not None and line.strip().startswith("- "):
            term = line.strip()[2:].split(" (")[0].strip().strip("`")
            if term:
                bucket.append(term)
    return anywhere, skills_only


def parse_layout(text):
    """Return (headings, bullets, skills_lines). Bullets keep their section and rendered lines."""
    headings, bullets, skills, section, cur = [], [], [], None, None
    for line in text.splitlines():
        if not line.strip():
            continue
        if not line[0].isspace():
            section, cur = line.strip(), None
            headings.append(section)
        elif line.startswith("  •"):
            cur = {"section": section, "lines": [line.strip().lstrip("• ").strip()]}
            bullets.append(cur)
        elif cur and line.startswith("    ") and not line[4].isspace():
            cur["lines"].append(line.strip())
        else:
            cur = None
            if section and "Skills" in section:
                skills.append(line.strip())
    return headings, bullets, skills


def check(tex, keywords_file=None):
    tex = Path(tex).resolve()
    pdf, log = tex.with_suffix(".pdf"), tex.with_suffix(".log")
    fails, warns, info = [], [], []

    build = run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", tex.name], tex.parent)
    if build.returncode != 0:
        return [f"build failed: {build.stdout[-600:]}"], [], []

    pinfo = run(["pdfinfo", str(pdf)], tex.parent).stdout
    pages = re.search(r"^Pages:\s+(\d+)", pinfo, re.M)
    if not pages or pages.group(1) != "1":
        fails.append(f"page count is {pages.group(1) if pages else '?'}, must be 1")
    if "612 x 792" not in pinfo:
        fails.append("page size is not US Letter (612 x 792 pts)")

    n_warn = len(re.findall(r"Overfull|Underfull", log.read_text(errors="ignore")))
    if n_warn:
        fails.append(f"{n_warn} Overfull/Underfull warnings in {log.name}")

    layout = run(["pdftotext", "-layout", str(pdf), "-"], tex.parent).stdout
    flow = " ".join(run(["pdftotext", str(pdf), "-"], tex.parent).stdout.split())
    if "—" in layout:
        fails.append(f"{layout.count('—')} em dash(es) in the PDF text")

    headings, bullets, skills = parse_layout(layout)
    for h in headings:
        if BANNED_HEADINGS.search(h):
            fails.append(f"banned section heading '{h}' (no Summary/Profile/Objective/About)")
    pos = [next((i for i, h in enumerate(headings) if req in h), None) for req in SECTION_ORDER]
    for req, p in zip(SECTION_ORDER, pos):
        if p is None:
            warns.append(f"no section heading containing '{req}'")
    found = [p for p in pos if p is not None]
    if found != sorted(found):
        fails.append(f"section order must be {' -> '.join(SECTION_ORDER)}; got {headings}")
    for s in skills:
        if ":" not in s:
            fails.append(f"Skills line wrapped onto a second rendered line: '{s}'")

    never_anywhere, skills_only = load_never_claim()
    for term in never_anywhere:
        if word_re(re.escape(term)).search(flow):
            fails.append(f"never-claim term '{term}' appears (profile/never_claim.md)")
    work = [b for b in bullets if b["section"] and re.search("Experience|Projects", b["section"])]
    for b in bullets:
        text = " ".join(b["lines"])
        head = f"[{b['section']}] '{text[:60]}...'"
        if len(b["lines"]) > 2:
            fails.append(f"bullet renders on {len(b['lines'])} lines (max 2): {head}")
        for bw in BUZZWORDS:
            if re.search(re.escape(bw), text, re.I):
                fails.append(f"buzzword '{bw}': {head}")
        if b not in work:
            continue
        for term in skills_only:
            if word_re(re.escape(term)).search(text):
                fails.append(f"'{term}' is Skills-line only, never a bullet: {head}")
        words = text.split()
        first_num = next((i for i, w in enumerate(words) if re.match(r"^[~<>$(]?\d", w)), None)
        if first_num is None:
            warns.append(f"no number in bullet: {head}")
        elif first_num >= HEATMAP_WORDS:
            warns.append(f"first metric is word {first_num + 1}; move it into the first "
                         f"{HEATMAP_WORDS} words (heat-map left edge): {head}")
        long_words = [w.lower() for w in re.findall(r"[A-Za-z]{6,}", text)]
        for w in sorted({w for w in long_words if long_words.count(w) > 1}):
            warns.append(f"word '{w}' repeated inside one bullet: {head}")
    openers = [" ".join(b["lines"]).split()[0] for b in work]
    for v in sorted({o for o in openers if openers.count(o) > 1}):
        warns.append(f"{openers.count(v)} bullets open with the same verb '{v}'")

    full_months = re.findall(r"\b(?:January|February|March|April|June|July|August|September|"
                             r"October|November|December) \d{4}", flow)
    short_months = re.findall(r"\b(?:Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)\.? \d{4}", flow)
    if full_months and short_months:
        warns.append("mixed date formats (full and abbreviated month names); use one")

    raw = pdf.read_bytes()
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        try:
            raw += zlib.decompress(m.group(1))
        except zlib.error:
            pass
    links = sorted({u.decode(errors="ignore") for u in re.findall(rb"/URI\s*\((.*?)\)", raw)})
    if not any(u.startswith("mailto:") for u in links):
        fails.append("no clickable mailto: link")
    info.append(f"{len(links)} links: {', '.join(links)}")

    kw_path = Path(keywords_file) if keywords_file else ROOT / "jd_keywords.txt"
    if kw_path.exists():
        kws = [k.strip() for k in kw_path.read_text().splitlines() if k.strip()]
        first100 = " ".join(flow.split()[:100])
        line1 = " ".join(l for l in layout.splitlines() if not l.startswith("    "))
        for i, kw in enumerate(kws):
            r = word_re(re.escape(kw), re.I)
            n_flow, n_layout = len(r.findall(flow)), len(r.findall(layout))
            info.append(f"keyword '{kw}': {n_flow} reflowed / {n_layout} layout")
            if n_flow == 0:
                warns.append(f"JD keyword '{kw}' missing (fine if no evidence; say so)")
            elif i < 5 and not r.search(first100):
                warns.append(f"top-5 keyword '{kw}' is not in the first 100 words (STEP 5)")
            elif i < 5 and not r.search(line1):
                warns.append(f"top-5 keyword '{kw}' appears only on bullet second lines (heat map)")
    else:
        info.append("no jd_keywords.txt: keyword checks skipped (written in STEP 2)")
    return fails, warns, info


def report(tex, fails, warns, info):
    out = [f"== {tex}: {len(fails)} FAIL, {len(warns)} WARN"]
    out += [f"FAIL: {f}" for f in fails] + [f"WARN: {w}" for w in warns] + [f"info: {i}" for i in info]
    return "\n".join(out)


def stop_hook():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        data = {}
    if data.get("stop_hook_active"):
        return 0
    cache = json.loads(CACHE_FILE.read_text()) if CACHE_FILE.exists() else {}
    texs = [p for p in [ROOT / "resume.tex", *sorted(ROOT.glob("applications/**/*.tex"))] if p.exists()]
    digest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in texs}
    # Each version of a file is checked (and can block) once, so the hook never loops.
    todo = [p for p in texs if cache.get(str(p.relative_to(ROOT))) != digest[str(p.relative_to(ROOT))]]
    reports, bad = [], False
    for p in todo:
        fails, warns, info = check(p)
        bad |= bool(fails or warns)
        reports.append(report(p.relative_to(ROOT), fails, warns, info))
    CACHE_FILE.parent.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps({**cache, **digest}, indent=1))
    if not bad:
        return 0
    print("\n".join(reports) + "\n\nFix every FAIL. For each WARN, fix it or state in your report "
          "why it stays (AGENTS.md STEP 6).", file=sys.stderr)
    return 2


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--stop-hook"]:
        sys.exit(stop_hook())
    if not args:
        sys.exit(__doc__)
    kw = args[args.index("--keywords") + 1] if "--keywords" in args else None
    fails, warns, info = check(args[0], kw)
    print(report(args[0], fails, warns, info))
    sys.exit(1 if fails else 0)
