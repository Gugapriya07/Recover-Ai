# RecoverAI — Autonomous Revenue Recovery Agent

RecoverAI detects failed and at-risk payments, decides whether and how to
recover them, executes a bounded recovery action, and logs every decision
for audit — with explicit stopping rules and escalation to a human when a
transaction falls outside safe autonomous limits.

Built for the **AI Revenue Recovery** track.

## What it actually does (pipeline)

```
Failed payment
      │
      ▼
DETECT       revenue_scanner.py     → find at-risk / failed transactions
      │
      ▼
INVESTIGATE  investigation.py       → gather customer history, failure reason
      │
      ▼
PREDICT      ml/recovery_predictor.py → ML model estimates recovery probability
      │
      ▼
VALUE        erv_engine.py          → Expected Recovery Value (probability × amount − cost)
      │
      ▼
DECIDE       intervention_engine.py → choose an action (retry, reminder, new
      │                               payment method, wait-and-retry, stop, escalate)
      ▼
POLICY       policy_engine.py       → 10 explicit safety rules: retry caps,
      │                               minimum probability/ERV thresholds,
      │                               autonomous amount ceiling, expired-card
      │                               and auth-failure specific guards
      ▼
EXECUTE      action_executor.py     → carries out the approved action
      │
      ▼
VERIFY       verification.py        → confirms whether the action succeeded
      │
      ▼
LOG          recovery_log.py        → every decision persisted for audit:
                                       probability, ERV, policy decision,
                                       execution + verification status,
                                       final outcome, amount recovered
```

Every transaction moves through an explicit state machine
(`DETECTED → INVESTIGATING → EVALUATING → POLICY_CHECK → EXECUTING →
VERIFYING → <final state>`), and the full timeline is visible in the
frontend for any transaction.

## Why this is bounded, not a black box

- **Stopping rules**: max retry count, minimum recovery probability,
  minimum expected recovery value, no re-attempting a transaction that
  already reached a terminal state.
- **Escalation, not autonomous action, above a value ceiling**: any
  transaction above the autonomous recovery limit is routed to manual
  review instead of being acted on automatically.
- **Failure-reason-specific guards**: e.g. an expired card is never
  retried — it's routed to "request new payment method" instead.
- **Full audit trail**: every decision is logged with the reasoning that
  produced it, not just the outcome.

## Live-verified results (this run)

These numbers come from actually resetting the database, reseeding, and
running every failed transaction through the agent — not from a
cherry-picked example.

| Metric | Value |
|---|---|
| Total transactions | 28 |
| Failed transactions processed | 17 |
| Recovered | 14 (50.0% recovery rate) |
| Amount recovered | ₹7,497 |
| Revenue recovery rate | 7.58% |
| Escalated to manual review | 1 transaction, ₹24,999 (above autonomous limit) |
| Pending (awaiting customer action) | ₹1,199 |

The mix of outcomes (recovered / recovery-failed / pending / escalated)
is intentional — a system that "recovers" 100% of the time isn't making
real decisions, it's rubber-stamping.

## ML model

A logistic regression predicts recovery probability from: amount,
payment method, failure reason, customer success rate, and previous
successful payments. Trained on a hand-authored synthetic dataset
(53 rows) covering both low- and high-value transactions.

Held-out test set (25% split): accuracy, precision, recall, and F1 are
printed by the training script itself (`ml/training/train_recovery_model.py`).
With a dataset this small, treat these as indicative, not a rigorous
benchmark — the honest next step with more time is a larger, more
diverse training set.

## Running it locally

```bash
cd backend
pip install -r requirements.txt

# reset and seed sample data
python reset_recovery.py
python seed_data.py

# run the API
uvicorn main:app --reload
```

Key endpoints:
- `GET /analyze/{transaction_id}` — run the full agent on one transaction
- `GET /agent/recover/{transaction_id}` — same, agent-facing route
- `GET /recovery-logs` — full audit trail
- `GET /metrics` — aggregate dashboard numbers (recovery rate, amount
  recovered, escalated, pending)

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Known limitations (being upfront about them)

- Training data is small and synthetic — real transaction data would
  materially improve probability estimates.
- Execution outcomes are currently deterministic for a given action;
  real-world payment retries have inherent uncertainty this doesn't yet
  model.
- Built for a single-node, synchronous batch — not yet tested at scale.
