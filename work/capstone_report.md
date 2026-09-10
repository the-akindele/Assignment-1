# Capstone Report — Lane 2: Refresh / Content Opportunity Scoring

- **Author:** David Akindele
- **Lane:** Lane 2 — Refresh / Content Opportunity Scoring
- **Repo:** the-akindele/Assignment-1
- **Date:** completed 2026-09-10 (started 2026-08-22)

> The deployed paper lives at https://the-akindele.github.io/Assignment-1/ (`docs/index.html`).
> Every number below is recomputed in `work/notebooks/capstone.ipynb`, which runs top to bottom.
> These eight sections mirror the Pass / Needs-Work rubric axes; nothing here is optional.

## 1. Problem framing

**Decision this supports:** which page should a content editor *look at first* when the goal is to
keep high-traffic content from losing search impressions. The editor has a small weekly budget
(≈20 pages) for refreshes.

- **Unit of analysis:** one page at one decision date `t = 2026-05-31`.
- **Output:** a ranked, reason-coded refresh queue (pages ordered by how strongly the evidence says
  they need attention). The queue decides *order only*; the human makes the edit.
- **Cost of a wrong call:** asymmetric. Refreshing a page that would not have moved costs editor-hours
  (recoverable). Skipping a page that keeps losing traffic incurs a loss that is only visible in next
  month's report.
- **Why data/ML helps:** the queue is built from observed search signals, and we can *measure* how
  often "ranked first" really meant "declined next window" — on held-out clients. The task's base
  rate is 67.4%, so every metric is reported against that bar.

## 2. Data safety

**Used:** the full FlyRank ML Internship warehouse release, build **v20260703** (gated,
`FlyRank/internship-warehouse`), queried remotely via DuckDB: `fact_content_daily_performance`
(78,835,655 rows) for window features and the label, `dim_content` (519,606) for static descriptors,
and `dim_clients` (104) as the grouping key for the split. Reduced to one snapshot of **108,254
eligible pages** (impressions ≥ 100 in B and ≥ 15 GSC-days in B). Windows: features in B =
(2026-05-01, 2026-05-31], decision at `t = 2026-05-31`, label in F = (2026-05-31, 2026-06-30].

**Excluded on purpose, and why:** `fact_content_query_90d` (its fixed window contains F at this `t`);
`imp_f` and every F-derived aggregate (they *are* the label's numerator); the whole
`ga4_*`/`sessions_*`/`ai_*`/`scroll_events` family (zero-filled outside GA4 availability, ~74% off);
`provider_used`/`model_used` (circular — would relearn the old product rule — and a privacy risk);
workflow timestamps; both hash-ID columns as features (grouping/splitting only). No raw titles, URLs,
domains, keywords, or queries are used anywhere.

**Leakage risks considered:** label-derived fields are the classic trap here, so anything computed
from F, or from a window straddling `t`, is forbidden by rule. Pseudonymous IDs (`client_hash_id`,
`content_hash_id`) are grouping keys only. **Confirmations:** the capstone notebook's §2 runs a
column-name public-safety check over the analysis outputs (none of the banned names present), and §7
regenerates the paper's figures without printing raw client/content IDs.

## 3. Baseline

Before any model I froze a transparent rule that mirrors how an editor already triages:

    flag  = has_traffic(imp_b ≥ 600) AND stale(age_days ≥ 180) AND position_slipping(pos_avg_b ≥ 12)
    score = flag × imp_b          # volume decides order within the flag

**Why fair:** it uses the same eligible pages, the same label, and the same precision@K metric as the
model. On the same data and metric: it flags **12,930 pages** (11.9% of eligible), and its ranked
in-sample precision@K (recomputed in the capstone notebook from the saved queue) is
**0.80 / 0.85 / 0.78 / 0.81 / 0.775 / 0.80** at K = 10/20/50/100/200/500 — a consistent
**1.15–1.26× lift** over the 0.674 base rate. The model-versus-baseline comparison on held-out
clients is in §5; the in-sample numbers are never quoted without it.

## 4. Model / analysis

**Method:** a logistic regression (readable, coefficient-based) and a random forest (300 trees, seed 1),
chosen because the signal audit found banded, non-linear effects a linear boundary can miss. Task fits
the lane: a ranking/prioritization problem over content, judged by top-K precision.

**Features (22, all knowable at `t`):** traffic and position in B (`imp_b, clk_b, ctr_b, gsc_days_b,
pos_avg_b, pos_vol_b`); static content descriptors with `has_*` companion flags for their ~22–31%
missingness (`word_count` … `backlinks`); age/freshness (`age_days, days_since_update`); three
label-encoded categoricals (`content_type, main_intent, competition_level`). Left out on purpose:
`imp_f` and all F-aggregates, the query table, the GA4 family, product flags, and both hash IDs.

**Target, in one sentence:** `declined_30d = 1` iff `imp_f < 0.8 × imp_b` — impressions fall more
than 20% in the 30 days after `t` versus the baseline month (base rate **67.4%**).

## 5. Evaluation

**Split:** GroupKFold(5) **grouped by client**, because the leakage hunt proved a random split
overstates skill by ~0.09 AUC (rows from one client share hidden character). The grouped fold measures
the production case — clients the model never trained on. Time-awareness is enforced by construction:
features from B (≤ t), label from F (> t).

**Metric with its base rate, on the same folds:**

| Delivered by | Precision@20 | Precision@50 | ROC AUC |
|---|---|---|---|
| base rate (no model) | 0.67 | 0.67 | 0.50 (chance) |
| baseline rule (transparent) | **0.73** | **0.73** | — |
| logistic regression | 0.65 | — | 0.54 |
| random forest (300 trees) | 0.70 | — | 0.61 |

The learned model does **not** clear the transparent baseline at the top of the list; the forest's only
clear edge is ranking depth for the mid-list.

**Leakage probes (the confession test), logistic regression, same legal set:**
random split AUC 0.632 → grouped AUC 0.539 (the ~0.09 drop *is* the memorization finding); adding
`imp_f` → 0.998 ("≈1.0" is the confession); a query-table-style forward signal → 0.873; adding
`provider_used`/`model_used` → 0.652 (circular + privacy → excluded).

**Error analysis:** the clearest misses are shared — huge (60k–120k impressions), old, off-page-1
pages that *held steady* (big pages can stay flat despite weak position), ≈15% of in-sample top-20
picks. Fold variance is high (each test fold holds ~5–8 clients), so the mean table is the claim, not
any single fold. Logistic regression underfits the banded signal (AUC 0.54); the forest captures depth.

## 6. Interpretation

**What was found:** the zero-weight readable rule concentrates decline-association in the top of the
queue (1.15–1.26× lift in-sample; 0.73 vs 0.67 base rate held-out at precision@20, beating both
learned models at the top). The random forest adds *ranking depth*, not top-K wins (AUC 0.61 vs 0.54,
precision@20 0.70 vs the rule's 0.73).

**In plain words for an editor:** the flame-patterned pages — "earns real traffic, is old, and sits off
page 1" — are the ones worth a look first; raw volume then decides the order. Five reason-code patterns
cover ~77% of the eligible population, so the queue is explainable end to end.

**Surprises and negative results:** the honest negative is the validation finding itself — the same
forest scores 0.79 AUC under a naive split and 0.99 with one forward-window feature, versus 0.615 on
the client-grouped, time-aware split. Those flattering numbers are the signature of leakage, not of
skill. A well-understood "no effect": at the top-K the editor uses, the extra model complexity buys
nothing over the readable rule.

## 7. Recommendation

1. **Run the transparent rule as the working triage tool** — and verify each pick by hand
   (live & indexable? already refreshed in the last ~30 days? position reading real? does the demand
   still exist? are we allowed to touch it?).
2. **Use the random forest for the middle of the queue, not the top** (its edge is ranking depth).
3. **Watch the documented blind spots** — flagged pages at ≥60k impressions (18 in this snapshot)
   and the ~15% of top-20 in-sample "misses" need a person.
4. **Never automate destructive actions** from this score: `declined` means "impressions dropped next
   window", not "delete this page"; `low_signals` pages are off the rule, not no-value.
5. **Re-run monthly against a fresh warehouse build** — every number here is tied to one build;
   re-check base-rate drift, held-out precision (~0.74 confirmatory floor), and the duplication/GA4
   guards.
6. **Treat 600 / 180 / 12 as settings**, tuned on the portfolio, not a recipe.
7. **Close the causal gap deliberately** with a randomized/matched evaluation of refresh edits — the
   one design this snapshot cannot provide.

**Confidence:** high on the ranking claim (holdout-measured); deliberately low on any outcome claim for
the edits themselves (no experiment ran).

## 8. Reproducibility

- **Fresh clone, starter slice (everything public):** `git clone https://github.com/the-akindele/Assignment-1`,
  `pip install -r requirements.txt`, then `python scripts/run_all.py` — runs the five-step reference
  pipeline end to end on the bundled anonymized starter set (`data/raw/content_refresh_anonymized.csv`,
  30,000 pages) and builds the PDF report.
- **Full-warehouse paper (gated data):** run `work/scripts/hf_query.py` against the gated
  `FlyRank/internship-warehouse` (needs the internship's credentials), then execute the notebooks in
  order `w01 → w02 → w03 → w03_feature_leakage_check → w04_signal_audit → w04_baseline_score →
  w05_model → w06_validation_audit → w07_action_playbook → capstone`.
- **Capstone notebook (`work/notebooks/capstone.ipynb`)** recomputes the playbook numbers from the
  saved analysis outputs, restates the warehouse-only held-out numbers from w05/w06 with sources named,
  and regenerates all five figures the deployed page embeds. It is committed with its outputs and
  executes top to bottom.
- **Pins:** seed 1; scikit-learn 1.8.0, pandas 3.0.3 (deltas in `requirements.txt`); results stable
  within a few points across library versions.
- **Not committed (by design):** any dataset, `*.csv` under `work/`, and warehouse exports — `.gitignore`
  blocks them so the repo is public-safe.

---

> **Claims checklist before submitting:** observed / measured / directional / decision-support
> **Metrics vs. base rate:** base rate 67.4% is printed next to every precision@K and accuracy figure;
> AUC / lift over baseline are the honest discrimination numbers.
> language everywhere · no causal claims without an experiment or causal design · no
> "predicted Google's algorithm" · no client-identifying details · numbers in this report
> match a fresh re-run of `work/notebooks/capstone.ipynb`.