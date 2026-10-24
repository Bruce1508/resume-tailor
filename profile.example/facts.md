# Facts (FICTIONAL SAMPLE: Alex Chen)

The single source of truth for every claim on the resume. The agent may use only facts
labeled `verified` or `confirmed`; an `estimate` also needs its basis written down, and you
must be able to explain it in an interview.

- `verified`: checked against code, a report, a dashboard, or a link the agent can open
- `confirmed`: you stated it and can defend it, but nothing on disk proves it
- `estimate`: an approximate number with a written basis you agreed to

## Contact
- Name: Alex Chen
- Location: City, ST
- Email: alex.chen@example.com
- LinkedIn: linkedin.com/in/example
- GitHub: github.com/example

## Verification sources
- StudyQueue repo: ~/code/studyqueue (the agent re-counts metrics here before using them)

## Experience

### Software Engineer Intern, Example Logistics Co. (May 2025 -- August 2025, City, ST)
- [verified] Order lookup p50 latency 1.2 s -> 180 ms after PostgreSQL indexes + Redis cache (load-test report)
- [confirmed] The API is used by 3 internal teams
- [estimate] Saved about 4 hours/week of manual reporting. Basis: a manager spent ~45 min each weekday exporting CSVs; the scheduled Python job replaced it
- [verified] Shipment service coverage 41% -> 78% with 120 Jest tests (coverage report in repo)
- Role: sole intern on caching work; paired with a mentor on the reporting job
- Tools actually used: Node.js, Express, PostgreSQL, Redis, Python, GitHub Actions, Jest

## Projects

### StudyQueue (TypeScript / React / Firebase)
- [confirmed] About 250 weekly active students (Firebase Analytics, October 2025)
- [verified] Page load 3.4 s -> 1.1 s after route code-splitting and lazy-loaded images (Lighthouse)

## Education
- Example University, Bachelor of Science in Computer Science, September 2023 -- May 2027

## Rejected claims (never use, and why)
- "Improved performance 10x": no measurement exists
