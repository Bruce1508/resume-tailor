<div align="center">

# resume-tailor

**Tailor your resume to any job with an AI agent, without letting it invent a single claim.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776ab.svg)](scripts/check_resume.py)
[![AGENTS.md](https://img.shields.io/badge/agent--instructions-AGENTS.md-blue)](AGENTS.md)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20Code%20%7C%20Codex%20%7C%20Gemini%20CLI%20%7C%20Cursor-6b4fbb)](#compatible-agents)

<img src="docs/assets/hero.webp" alt="A split desk: an ad-hoc chat-and-document workflow on the left, a repository-based LaTeX resume workflow on the right" width="100%">

[Features](#features) · [Quick start](#quick-start) · [Usage](#usage) · [Checker](#what-the-checker-catches) · [Contributing](#contributing)

</div>

---

Most AI resume tools chase the keyword filter and will add skills you never had.
**resume-tailor** does the opposite: a set of agent instructions (`AGENTS.md`) plus a
Python checker that keep every bullet tied to a fact you can defend in an interview.

## Features

- 📋 **Fact ledger:** every claim traces to `profile/facts.md`, tagged `verified`, `confirmed`, or `estimate`
- 🚫 **Enforced blocklist:** terms in `profile/never_claim.md` fail the check if they reach the resume
- ✋ **Approval gate:** the agent stops after its gap analysis and waits for your go-ahead
- 🎯 **Recruiter-aware placement:** top keywords land in the first 100 words; metrics in the first 7 words of each bullet
- ✅ **Mechanical quality gate:** one command checks page count, layout, reading order, links, and keywords
- 🔌 **Agent-agnostic:** one `AGENTS.md` for Claude Code, Codex, Cursor, Gemini CLI, and opencode

<p align="center">
  <img src="docs/assets/manual-vs-workflow.svg" alt="A typical chat-and-document loop compared with this repository's fact, approval, editing, checking, and snapshot workflow" width="100%">
</p>

## How it works

1. **Setup (once):** the agent interviews you and writes your facts, blocklist, and master `resume.tex`
2. **Analyze:** for each job, it extracts keywords, scores the match, and lists the gaps
3. **Approve:** it stops and shows you the edit plan
4. **Rewrite:** it rewrites bullets, then runs an ATS pass and a recruiter pass
5. **Verify:** `scripts/check_resume.py` must report 0 FAIL before the PDF is done

<p align="center">
  <img src="docs/assets/quality-gate.svg" alt="resume.tex flows through check_resume.py, which audits PDF format, layout, reading order, links, never-claim terms, and keyword placement before a FAIL-free build" width="100%">
</p>

<div align="center">
<img src="docs/sample-preview.png" alt="Sample one-page resume for a fictional candidate" width="620">

<sub>Fictional sample (Alex Chen) rendered from <code>template/resume.tex</code>: 0 FAIL, 0 WARN</sub>
</div>

## Prerequisites

| Tool | Why | Install |
|---|---|---|
| LaTeX + `latexmk` | Builds the PDF | macOS: `brew install --cask mactex-no-gui`<br>Ubuntu/Debian: `sudo apt install latexmk texlive-latex-extra texlive-fonts-extra`<br>Windows: [MiKTeX](https://miktex.org/) + Perl |
| Poppler | `pdfinfo` / `pdftotext` for the checker | `brew install poppler` / `sudo apt install poppler-utils` |
| Python 3.9+ | Runs the checker | Standard library only |
| A coding agent | Runs the workflow | Claude Code, Codex CLI, Cursor, Gemini CLI, opencode |

## Quick start

**1. Clone the repository**

```bash
git clone https://github.com/Bruce1508/resume-tailor.git my-resume
cd my-resume
```

**2. Verify your toolchain**

```bash
python3 scripts/check_resume.py template/resume.tex
# expected: == template/resume.tex: 0 FAIL, 0 WARN
```

**3. Build your profile (once)**

```text
/setup
```

**4. Tailor for a job**

```text
/tailor <paste the job description>
```

The agent stops after its analysis. Reply to approve or adjust the plan.

## Usage

### With Claude Code

| Command | What it does |
|---|---|
| `/setup` | Interviews you and writes `profile/` and `resume.tex` |
| `/tailor <JD>` | Runs the 6-step tailoring workflow, pausing for approval |

A `Stop` hook in `.claude/settings.json` runs the checker automatically whenever
`resume.tex` or a file in `applications/` changes, and sends any FAIL or WARN back to the
agent. Each file version is reported once, so it never loops.

### With other agents

Codex, Cursor, Gemini CLI, and opencode have no slash commands. Ask in plain text:

```text
Run the Setup workflow in AGENTS.md, Section 2.
```

```text
Run the Tailoring workflow in AGENTS.md, Section 3, for this job description: <paste>
```

These agents follow the checker rule from `AGENTS.md` but do not run it automatically.

### Running the checker yourself

```bash
python3 scripts/check_resume.py resume.tex
python3 scripts/check_resume.py applications/Acme/resume.tex --keywords jd_keywords.txt
```

- Exits `1` on any FAIL, `0` otherwise (CI-friendly)
- Reads `profile/never_claim.md` and, if present, `jd_keywords.txt` (one keyword per line, top 5 first)
- Rules live in constants at the top of the script: `BUZZWORDS`, `SECTION_ORDER`, `HEATMAP_WORDS`

## What the checker catches

| FAIL (must fix) | WARN (fix or justify) |
|---|---|
| Not exactly 1 US Letter page | Missing core section |
| LaTeX Overfull/Underfull warnings | Bullet with no number |
| Em dashes | First metric after word 7 |
| Bullet longer than 2 lines | Word repeated within a bullet |
| Summary/Profile/Objective/About heading | Bullets opening with the same verb |
| Sections out of order | Mixed date formats |
| Skills line that wraps | JD keyword missing |
| Blocklisted term anywhere | Top-5 keyword outside the first 100 words |
| Skills-only term inside a bullet | Top-5 keyword only on a bullet's second line |
| Buzzword (`synergy`, `passionate`, ...) | |
| No `mailto:` link | |

The checker catches formatting and rule violations. It cannot prove a claim is true.

## Repository layout

```text
.
├── AGENTS.md                  # the full workflow (single source of instructions)
├── CLAUDE.md                  # points Claude Code at AGENTS.md
├── .gemini/settings.json      # points Gemini CLI at AGENTS.md
├── .claude/
│   ├── commands/              # /setup and /tailor
│   └── settings.json          # Stop hook that runs the checker
├── scripts/check_resume.py    # standalone checker, no dependencies
├── template/resume.tex        # Jake-style LaTeX resume, fictional sample
├── profile.example/           # sample facts.md and never_claim.md
└── docs/                      # README images
```

Created by you and **gitignored**: `profile/`, `resume.tex`, `resume.pdf`,
`applications/`, `tailoring_history.md`, `jd_keywords.txt`.

## Compatible agents

| Agent | Reads `AGENTS.md` | Slash commands | Auto-check hook |
|---|---|---|---|
| Claude Code | ✅ via `CLAUDE.md` | ✅ | ✅ |
| Codex CLI | ✅ | ❌ | ❌ |
| Cursor | ✅ | ❌ | ❌ |
| Gemini CLI | ✅ via `.gemini/settings.json` | ❌ | ❌ |
| opencode | ✅ | ❌ | ❌ |

## Privacy

- Personal files are gitignored by default; remove those lines only in a **private** fork
- The checker runs locally and makes no network calls
- Your coding agent sends the files it reads to its model provider, under that provider's terms
- Before making any fork public, search it (including Git history) for personal data

## FAQ

**Non-software roles?** The rules are general, but the examples target software postings. Adjust wording, not mechanism.

**No metric for real work?** Don't invent one. `AGENTS.md` Section 5.2 shows how to reframe the claim so it becomes measurable.

## Contributing

Issues and pull requests are welcome.

1. Open an issue first for larger changes
2. Keep `scripts/check_resume.py` standard-library only
3. Run `python3 scripts/check_resume.py template/resume.tex` and confirm `0 FAIL` before opening a PR
4. Never commit real personal data; use the fictional sample for examples

## Credits

- LaTeX template: [Jake Gutierrez's resume](https://github.com/jakegut/resume), based on [sb2nov/resume](https://github.com/sb2nov/resume)
- Hero image is AI-generated; diagrams are editable SVGs

## License

[MIT](LICENSE)
