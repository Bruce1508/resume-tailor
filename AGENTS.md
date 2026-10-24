# AGENTS.md — Resume Tailoring Rules

This file is read by Claude Code, Codex, Cursor, Gemini CLI, and any other coding agent
that supports the [AGENTS.md standard](https://agents.md). It is the single source of
instructions; `CLAUDE.md` and `.gemini/settings.json` only point here.

## 1. Mission & Non-Negotiables

Maintain a one-page SWE resume in `resume.tex`, backed by a factual source of truth the
agent is never allowed to override with a better-sounding sentence.

Priority order when instructions conflict:
1. Factual accuracy
2. Match the target job description
3. Demonstrate measurable impact
4. ATS / recruiter readability
5. Visual polish

Rules:
- Resume content must be in English.
- **Never invent skills, experience, dates, awards, metrics, interests, or results.**
- Never copy another person's claims or metrics from a reference resume.
- `profile/facts.md` is the factual source of truth. Read it before every tailoring pass.
  The agent may use only facts labeled `verified` or `confirmed`; an `estimate` needs a
  written basis the person can defend in an interview.
- `profile/never_claim.md` lists technologies that must never appear, or must appear only
  on the Skills line. Leaving a keyword gap is correct; inventing evidence is not.
- `tailoring_history.md` (created on first tailoring pass) holds per-JD history: what
  changed, what was dropped and is recoverable, what a past pass already proved
  impossible. Read it only when you need the rationale behind a past wording choice.
- Technical claims must be verified against the relevant repo when possible — re-open the
  repo and re-count, don't trust a remembered number.
- If evidence is missing, ask the person or leave the claim out. Never split the
  difference with a vague adjective.
- `resume.tex` is editable; never edit the built `.pdf` directly.
- **Never write a Summary, Profile, Objective, or About section**, even when a job
  description or keyword target seems to call for one. Keywords go into the experience
  bullets and the Skills line instead.
- Per-company snapshots live in `applications/<Company>/` (`resume.tex` + `.pdf`). Never
  create them at the repo root.
- Keep the resume exactly one US Letter page.
- Never commit or push unless the person explicitly asks.

## 2. Setup Workflow (run once, before any tailoring)

Triggered by `/setup` (or "set up my resume" / "help me build my facts file").

A tailoring pass can only be as honest as the facts behind it. Do not skip this by
inventing a facts file from a resume PDF alone — a past resume may already contain
unverifiable or exaggerated claims.

1. **Collect raw material.** Ask for: an existing resume (PDF/text), LinkedIn export, or
   a plain description of jobs and projects. Read whatever is provided.
2. **Interview entry by entry.** For each job or project, ask:
   - What did you build, fix, or ship? What was the before/after?
   - What's the real number — users, requests, latency, time saved, test count, dataset
     size? If there is no number, is there a true verified *scope* instead (see 5.2)?
   - Where can this be checked — a repo, a dashboard, a report, a commit log?
   - What tools/libraries were *actually* used, specifically (not "a database," which
     one)?
3. **Label every fact** `verified` (checked against a source the agent can re-open),
   `confirmed` (the person stated it and can defend it, nothing on disk proves it), or
   `estimate` (approximate, with a written basis).
4. **Build `profile/never_claim.md` by elimination, not by asking what's missing.** Walk
   the target role family's common stack and ask yes/no for each: "Have you used X in a
   real project?" A "no" or "only a coursework exercise" goes on the list immediately —
   do not wait for a job description to surface the gap.
5. **Write `profile/facts.md`** from the interview, grouped by job/project, each fact
   tagged as in step 3. Copy `profile.example/facts.md` as the starting structure.
6. **Write `resume.tex`** from `template/resume.tex`, replacing every placeholder with
   real contact info and real entries built only from `verified`/`confirmed` facts.
7. **Build and verify** per Section 5 before telling the person setup is complete.

## 3. Tailoring Workflow (6 steps, run per job description)

Triggered by `/tailor` (or pasting a job description and asking to tailor).

Complete these steps **in order** for every job-description request. Do not jump
directly to rewriting. **Steps 1–2 are analysis only: stop after STEP 2 and wait for
explicit approval before touching `resume.tex`** (see 5.5 for why this is non-negotiable).

### STEP 1 — Hidden Keyword Extraction

Act as an expert ATS scanner. Read the entire job description first, then extract its
keywords into three categories:
- **Hard Skills** (languages, techniques, concepts)
- **Soft Skills**
- **Role-Specific Tools** (frameworks, platforms, products)

Count each keyword's literal occurrences and **highlight every keyword mentioned more
than twice** — those are what the ATS weights most. Record the JD's exact spelling
(`Node.js` vs `NodeJS`, `CI/CD` vs `continuous integration`); the resume reuses it.

Also note core responsibilities, success indicators, domain knowledge, and eligibility
requirements.

### STEP 2 — ATS Match & Gap Analysis

Compare the current resume and `profile/facts.md` against the STEP 1 keywords.

Report:
- **Estimated ATS Match Score (0–100%)**: share of STEP 1 Hard Skills + Role-Specific
  Tools found in the resume text, with the >2-mention keywords listed first.
- **Missing keywords**, split into (a) supported by `profile/facts.md`, safe to add, and
  (b) no evidence or on `never_claim.md`, which stay missing.
- **Missing required qualifications** (degree, years, certifications, eligibility
  blockers).
- Top 3 red flags visible in a 10-second recruiter scan.
- Strongest existing matches.
- Project ranking by JD relevance, with reasons (see Section 4).
- **Target 85%+ keyword overlap before submitting.** If bucket (b) makes 85%
  unreachable, state the honest ceiling (5.5) instead of chasing the target.
- The specific edit plan.

Write the STEP 1 keywords to `jd_keywords.txt` (one per line, the top 5 essential
keywords first, JD spelling); `scripts/check_resume.py` reads it in STEP 6.

**Do not modify the resume yet. Stop and wait for approval.**

### STEP 3 — Impact Bullet Optimization

Act as a senior recruiter and ATS parsing expert. Only after approval, determine which
bullets actually need modification and rewrite them to be impact-first, highly
scannable, and ATS-optimized.

Every bullet should answer:
1. WHAT did the person build/accomplish?
2. HOW did they do it?
3. WHAT measurable result, scale, or impact did it produce?

Default structure: **Accomplished X, measured by Y, by doing Z.** Natural reorderings
are allowed, especially **Outcome → Metric → Mechanism**.

```
BAD:  Worked on backend APIs for a web application.
GOOD: Built 6 REST APIs with Node.js and PostgreSQL, cutting average
      response time 35% across 200+ daily requests.
```

Hard rules:
- Write achievements, not job descriptions.
- Start every bullet with a strong action verb, and lead with the core achievement or
  result rather than the duty or task.
- No buzzwords or filler: `synergy`, `go-getter`, `thought leader`, `hardworking`,
  `dynamically managed`, `results-driven`, `passionate`, `detail-oriented`,
  `team player`. Use plain, concrete language.
- Every bullet must contain a concrete result, metric, scale, or defensible evidence
  when available. Ask: faster by how much? how many users? how much data? how much time
  saved? what changed?
- Avoid abstract/generic nouns for tools or actions (bare "Python," "troubleshooting,"
  "used AWS"). Name the specific library/tool/technique (e.g. "Pandas/Matplotlib" not
  "Python"). If unconfirmable, ask and record the confirmation in `profile/facts.md`
  before using it.
- **Never fabricate a number to satisfy the formula.** A defensible estimate is allowed
  only if the person confirms the basis and can explain it in an interview. If no
  legitimate outcome metric exists, use verified scale/scope instead.
- Integrate the STEP 1 keywords naturally, in the JD's exact spelling, only where
  `profile/facts.md` supports them for that entry.
- **Heat-map rule (recruiter eye-tracking):** recruiters read down the left edge in an
  F-pattern and skip the right half of each line and most second lines. Put the action
  verb and the result number within the **first 7 words** of every bullet, and never let
  a top-5 JD keyword appear only on a bullet's second line.

Prefer: Built, Shipped, Reduced, Improved, Designed, Automated, Hardened, Led, Delivered.
Avoid: Responsible for, Helped with, Worked on, Participated in, Various, Successfully.

Each bullet:
- one primary achievement
- 1–3 meaningful numbers, not a number on every noun
- does not just repeat the Technical Skills list; show the tool solving a problem
- ideally 1–2 rendered lines; only 1–3 bold high-signal anchors
- no keyword stuffing

#### Bullet order within each entry (non-negotiable)

- **The FIRST bullet of every job/project must lead with a genuine outcome or impact
  metric** (a before/after result, a user-facing change, a quality outcome) — never with
  scope-only counts (endpoint counts, model counts, team size, hackathon duration).
  Scope/scale numbers are supporting evidence for later bullets, not the opener.
- Every other bullet in that entry must also carry a concrete, quantified metric — audit
  this explicitly at the end of STEP 3, entry by entry, not just spot-checked.
- If reordering to satisfy this rule conflicts with another instruction, resolve it by
  keeping the impact metric first and adjusting which words are bolded — do not silently
  drop one instruction in favor of the other; state the trade-off.
- A verified true metric is not automatically worth including. If a number reads as weak
  or anti-traction to a recruiter (e.g. a low download/star count), flag it and prefer
  the underlying credential or time-saved metric instead — ask before removing.

### STEP 4 — ATS + Human Scrutiny

After rewriting, review the entire resume twice.

**ATS pass:** important JD keywords represented naturally; skills supported by
`profile/facts.md`; standard readable section names; no unsupported keyword stuffing;
ATS text extraction preserves reading order.

**Recruiter pass:** act as a recruiter scanning 200 resumes with only 5–10 seconds for
first review. Identify sections likely to be skipped, weak/generic bullets, bullets
whose impact is unclear, strongest evidence that should appear earlier, unnecessary
technical detail, anything that raises credibility concerns. Rewrite only the weak
sections — do not rewrite strong content merely for variation.

### STEP 5 — Lead Recruiter Final Polish

Act as the Lead Recruiter at the target company. Re-read the whole resume, including the
Technical Skills section, and tailor further only where it still misses the role.

- **The top 5 essential JD keywords must appear in the first 100 words** of the
  extracted text (header + first experience entry). Land them through the first entry's
  title line and opening bullets.
- **Entry header lines are the hottest spots after the name** (job title, company,
  project name + tech-stack line, dates). Lead each project's tech-stack line with the
  JD's top keywords that project truly uses. Never change a job title, company name, or
  date.
- **The top third of the page gets the most attention.** The entry with the strongest JD
  evidence comes first within its section.
- **Do not move Technical Skills to the top and do not add a Summary section.**
- Never put a keyword in an early bullet that `profile/facts.md` does not support for
  that entry; `never_claim.md` limits still apply. If a top-5 keyword cannot truthfully
  land in the first 100 words, report it as unreachable instead of forcing it.
- Within each Skills line, put the JD's top keywords first.

### STEP 6 — Verify, Build & Formatting Audit

Before finishing, run **all** of Section 5 below, then:
1. Confirm the top 5 JD keywords appear in the first 100 extracted words (STEP 5).
2. **Run `python3 scripts/check_resume.py resume.tex`** and paste its summary into the
   final report. Every FAIL must be 0. Every WARN is either fixed or listed in the report
   with the reason it stays. The script automates most of Section 5; it does not replace
   re-checking facts or the visual inspection.

## 4. Resume Structure

Order: Work Experience → Projects → Education → Technical Skills.

Projects are ordered by JD relevance, not by date or habit: the project whose evidence
matches the most JD requirements goes first. Re-rank them for every tailoring, state the
ranking and its reasons in STEP 2, and move whole entries only (never rewrite bullets
just to reorder).

Preserve the Jake-style ATS-friendly layout: clickable email/portfolio/LinkedIn/GitHub
links, current typography and restrained spacing. Technical Skills always stays last —
never move it up to chase keyword density.

## 5. Build & Verify (run every time, without being asked)

### 5.1 Build and verify commands

- Build: `latexmk -pdf -interaction=nonstopmode resume.tex`
- Warnings: `grep -c "Overfull\|Underfull" resume.log` (must be 0)
- Page + size: `pdfinfo resume.pdf | grep -i "^Pages\|^Page size"` (`1`, `612 x 792 pts`)
- Em dashes: `pdftotext -layout resume.pdf - | grep -c "—"` (must be 0)
- Bullet lines: `pdftotext -layout resume.pdf - | grep -n ""` — each bullet is 2 numbered
  lines with a blank line between; 3 means over budget
- Links: regex `/URI\s*\((.*?)\)` over raw PDF bytes in `python3` finds all of them; zlib
  inflation if streams are compressed
- First 100 words: `pdftotext resume.pdf - | tr -s '[:space:]' ' ' | cut -d' ' -f1-100`,
  then `grep -oiw` each top-5 keyword in that output
- **All of the above in one command:** `python3 scripts/check_resume.py resume.tex`
  (exit 1 on any FAIL; reads `jd_keywords.txt` and `profile/never_claim.md` if present)
- **Enforced by a Stop hook** (`.claude/settings.json`): whenever `resume.tex` or an
  `applications/**/*.tex` file changes, Claude Code runs the checker before the turn can
  end and sends any FAIL/WARN back to the agent. It only re-blocks when the file's
  content actually changes, so it never loops.

### 5.2 Impact-first audit (every bullet, every time)

The FIRST bullet of every entry must open with a genuine outcome — never a scope-only
count and never a description of activity. Every other bullet must also carry a concrete
quantified metric. Audit this entry by entry at the end of every edit; do not spot-check.
If a bullet genuinely has no number, do not invent one — instead try changing what the
bullet *asserts* so the true claim becomes quantifiable (e.g. "caught regressions before
merge," unquantifiable, becomes "blocked untested code from reaching production... every
merge," a complete-coverage claim a verified CI config can support).

### 5.3 Recruiter-clarity check

Read every bullet as a senior recruiter who has 10 seconds and is not a specialist in
this stack. Flag and fix:
- **Generic/abstract nouns**: bare "Python," "troubleshooting," "used AWS," "various."
  Name the specific library/tool/technique instead.
- **Project-internal vocabulary** that means nothing outside the repo.
- **Specialist jargon** a recruiter will stall on — plain-language it.
- **Vocabulary that sets a false expectation** — don't pick a word because it "sounds
  more technical" if it misleads about what the work actually was.
- **Event names in parentheses beside a bolded project name** read as client or sponsor
  companies. Always label them, e.g. `(HackMIT 2025 Hackathon)`, not `(HackMIT 2025)`.

### 5.4 Dash rule

No em dashes (—) anywhere; zero tolerance, check the built PDF text, not just the `.tex`
source. `--` is for numeric and date ranges only (`Apr 2025 -- Present`, `35--50
minutes`) — never as a sentence or parenthetical connector.

### 5.5 Process discipline

- **Stop after STEP 2 and wait for explicit approval before editing.** This exists
  because an unapproved pass is expensive to undo (`git checkout -- resume.tex
  resume.pdf` loses the delta). Present the keyword extraction, ATS match score, missing
  keywords and qualifications, and red flags first, then the specific edit plan, then
  wait.
- **Never commit or push unless explicitly asked.** When asked, commit with a message
  that records the JD, the score change, each change *and its reason*, the never-claim
  verification, and the build results.
- **State the honest ceiling.** If a JD names technologies not on the facts file, say
  what the realistic maximum score is and why, rather than implying a rewrite can reach
  85%.
- **Record every decision** in `profile/facts.md` (new facts) or `tailoring_history.md`
  (tailoring rationale), including things deliberately *not* done and why.

### 5.6 Mechanism-matches-claim check

A bullet can pass the impact-first audit, carry a real metric, and still be wrong
because the stated mechanism does not produce the stated outcome. Read each bullet as
`<outcome> because <mechanism>` and ask whether the mechanism actually causes it. Two
true facts wired together as false cause and effect (e.g. crediting encryption for
idempotency, when the real mechanism is idempotent database upserts) is a factual error
even though every word in it is individually true.

### 5.7 Read the whole page top-to-bottom before finishing

Some defects exist only at page level: four of five entries opening with an identical
verb, or a word repeated twice inside one bullet. Scan the full rendered page, not just
each edited bullet in isolation.

## 6. Never-Claim List

`profile/never_claim.md` is the source of truth; `scripts/check_resume.py` enforces it
automatically. Never add anything from that file to `resume.tex`, including when a job
description names it as required — leaving a keyword gap is correct, inventing evidence
is not. When a term's status changes, update `never_claim.md` and re-run the checker.
