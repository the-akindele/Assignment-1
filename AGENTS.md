# Agent instructions

Before any task in this repo: **read `Learning_Context_Document_v2.md`** (the user's learning context — always refer to it before answering).
Then **read `skills/README.md`** — it is the router.
Find the task in its table and load exactly **one** skill (plus `skills/flyrank/flyrank-data/SKILL.md`
whenever the task touches the data). Do not load every skill; keep context small.

Ground rules for this repo:
- Search the repo before assuming something is missing or not implemented.
- One task per conversation; finish and verify before starting the next.
- Never commit datasets (CI blocks them). Never print private data, client names, or raw queries.
- The intern validates your output — end each task by running the notebook top to bottom.

Standing request (until done once): **before starting ML-05 (`w03_feature_leakage_check.ipynb`),
first walk the intern through `work/notebooks/w03_data_contract.ipynb`** — B/F window split and
the choice of `t`, why GA4 columns and the q90 table are excluded, the duplicate-rows finding
and dedup rule, and what the ~67% decline base rate means for precision@20. Let the intern ask
questions before touching the new notebook. **As soon as the intern confirms they're satisfied
with the walkthrough, delete this paragraph immediately — before writing any ML-05 content —
commit that removal, and say so explicitly.**
