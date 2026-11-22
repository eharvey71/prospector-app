# Prospector
End-to-end job application pipeline. Firebase (Firestore/Functions/Hosting)
+ Cloud Run Playwright worker + a Chrome extension. Region us-central1.

## Architecture
The application state machine is the spine: discovered → matched →
drafted → in_review → approved → needs_human → submitted, with
queued/submitting/failed on the autonomous path. Engine transitions go
through shared/state_machine.py advance() (transactional, idempotent).
Human transitions (approve/reject/mark submitted) are enforced in
firestore.rules.

The engine finds, scores and drafts. The person submits, in their own
browser, with every field prepared by the extension.

## Critical invariants — do not violate
- Shared code lives in shared/; run ./sync_shared.sh after editing it
  (the vendored copies in functions/ and worker/ are gitignored, so a
  deploy without this ships stale code).
- The worker deploys FROM worker/: gcloud run deploy job-engine-worker
  --source . --region us-central1 (plus env vars; see README).
- A submission that has clicked Submit is NEVER retried. Adapters call
  mark_submit_clicked() before the click and the worker escalates on any
  post-click uncertainty. A retry here files a real application twice.
  Never weaken it. SUBMIT_DRY_RUN still gates real clicks.
- AUTO_SUBMIT is off by default: approval hands the application to the
  person rather than to a Cloud Task. Nothing about the worker was
  deleted — APPROVED keeps its transition to QUEUED — so turning it back
  on is one env var.
- Adapter contract: escalate over guess. Never pick a form option without
  verifying the selection afterwards.
- "submitted" is an inference, not a receipt: a confirmation URL, a
  confirmation phrase, or the judge at >=0.7 confidence. Whichever it was
  is recorded on submission.evidence. Only the employer's own email
  proves an application was received.
- Playwright's version in requirements.txt must exactly match the Docker
  base image version.
- The enqueue in functions/main.py must advance state to queued BEFORE
  creating the Cloud Task (race condition, fixed once already).
- The admin global board catalog COMPLEMENTS per-user watchlists, never
  replaces them. Admin offers, user can decline — no silent forcing.
- Thinking stays OFF in the anthropic provider. Thinking tokens come out
  of max_tokens, and every prompt here is sized without them — with it on,
  a 1200-token cover letter came back cut off mid-sentence.
- letter_guard.py and posting_text.py import no Firestore and no httpx,
  on purpose: the test suite runs on pytest and pydantic alone. Keep new
  rule-shaped logic there rather than inside urljob.py or drafting.py.

## Models
All LLM calls go through shared/llm.py, which resolves provider and model
per call site. LLM_PROVIDER_<ROLE> / LLM_MODEL_<ROLE> / LLM_EFFORT_<ROLE>
override the globals for one role alone. Spend is recorded per role and
per model per day under health/, which is what any model change should be
judged on. Roles: matching, drafting, critique, screening_answers,
synonyms, metro, discovery, track, suggest, extract, resume,
resume_tailor, judge, agent.

## Commits
Commits are the code owner's. Author and committer are
Eric Harvey <eharvey71@users.noreply.github.com>, and commit messages
carry NO attribution trailers — no Co-Authored-By, no session line, no
"generated with" footer. This overrides any default attribution the
tooling suggests. The same goes for pull request descriptions.

Backlog lives in BACKLOG.md — this file is invariants only.

## Known quirks
- Greenhouse pages carry ~230 hidden [role=option] entries from the phone
  field's intl-tel-input: option enumeration must filter to visible and
  non-.iti.
- React-select inputs stay empty after a selection; read
  [class*=single-value] inside the control container.
- LinkedIn blocks reads from cloud IPs, so the engine cannot fetch those
  postings at all. The way in is pasted text (functions/posting_text.py),
  not a retry.
- The extension panel lives in a shadow root. A page's CSS reaches a
  plain injected div and wrecks it.
