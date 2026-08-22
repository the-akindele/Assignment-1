# Capstone Report — Lane 2: Refresh / Content Opportunity Scoring

- **Author:** David Akindele
- **Lane:** Lane 2 — Refresh / Content Opportunity Scoring
- **Repo:** the-akindele/Assignment-1
- **Date:** started 2026-08-22

> Copied from `work/capstone_report_template.md` — filled in as each assignment lands.
> The eight sections mirror the Pass / Needs-Work rubric axes, so nothing here is optional.

## 1. Problem framing

What decision does this support? Name the unit of analysis (page, client, day…), the output
(score, rank, cluster, report), the action a human takes from it, and the cost of a wrong
call. Why does data/ML help here at all?

> Drafted in ML-02/ML-03 (`work/notebooks/w01_research_question.ipynb`,
> `w02_ml_task_framing.ipynb`): rank pages by 30-day decline risk into a refresh queue,
> judged by precision@20. This section gets its final wording at ML-11.

## 2. Data safety

Which data you used and which columns you deliberately excluded (and why). Leakage risks you
considered — especially label-derived fields (`trend_direction`, `trend_pct`) and pseudonymous
IDs (grouping only, never features). Confirm nothing client-identifying appears anywhere in
`work/`.

> Contract written in ML-04 (`work/notebooks/w03_data_contract.ipynb`): warehouse release
> tables, B/F window split at decision date t, GA4 family + query table excluded, dedup rule
> for the sample slice. To be summarized here at ML-05+.

## 3. Baseline

The transparent rule or score you built first. Why it's a fair comparison, and its numbers on
the same data and metric as your model.

## 4. Model / analysis

Your method and why it fits the lane. The exact feature list (and what you left out on
purpose). The target or proxy definition, in one sentence.

## 5. Evaluation

Your split (grouped by client? time-aware?) and why. Metrics, model vs baseline **on the same
split**. What the errors look like — a short error analysis beats a big metric table.

## 6. Interpretation

What the model/clusters actually found. Feature importances or cluster profiles in plain
words. Surprises and negative results — a well-understood "no effect" is a valid result.

## 7. Recommendation

The ranked actions or decisions your output supports, and how a FlyRank editor would use them
tomorrow. State your confidence and the limits explicitly.

## 8. Reproducibility

The exact commands to re-run everything from a fresh clone, your random seeds, and your
environment (`pip freeze` highlights or `requirements.txt` deltas).

---

> **Claims checklist before submitting:** observed / measured / directional / decision-support
> **Metrics vs. base rate:** report your task's base rate (majority-class %) next to any
> precision@K or accuracy — a high score can just be a high base rate. AUC / lift over
> baseline are the honest discrimination numbers.
> language everywhere · no causal claims without an experiment or causal design · no
> "predicted Google's algorithm" · no client-identifying details · numbers in this report
> match a fresh re-run.
