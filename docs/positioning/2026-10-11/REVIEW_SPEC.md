# Publication positioning and literature claims audit

User asks whether existing results justify further analysis/paper, which prior
claims they support or limit, and how their novelty compares with real papers
at different venues. This is a read-only research/literature stage, not new GPU
experiments, training, publication, or changes to accepted artifacts.

Root owns synthesis in POSITIONING.md and HANDOFF. Two delegated source tasks
use gpt-6.1-sol, high (user maximum xhigh). Only new docs under this directory
may be written. Old analysis manifests/bundles/AGENTS/MEMORY remain frozen.
Use official proceedings, OpenReview decisions, primary paper texts and
official reviewer guidance. Separate accepted main conference, Findings,
workshop and preprint; submission alone is not acceptance. No fabricated
acceptance probabilities, novelty percentages or universal venue threshold.

## Comparator task

Own COMPARATORS.md. Find 5–7 close actual accepted papers across main ML
conferences, NLP main/Findings, TMLR and/or workshops as evidence allows.
Prefer empirical/mechanistic/critical LoRA analyses, not only new methods.
For each: exact title, year/venue/track verified by official link, central
incremental conceptual contribution, experimental breadth/controls from paper,
what it demonstrates about contribution type and what ours still lacks.
Examples to verify, not assume status: LoRA vs Full Fine-Tuning intruder
dimensions; LoRA Learns Less and Forgets Less; LoRA-Squeeze; Shortcuts in the
Tail; DeLoRA; EVA. Do not imply small idea means weak evidence or low standards.
Return concise sourced findings; record status uncertainty instead of filling
slots with unverified papers. No outreach, downloads of weights or GPU work.

## Prior claims task

Own CLAIMS_RECHECK.md. Read current claim-evidence.csv, REPORT.md, literature
file and new radial FINDINGS.md. Recheck primary statements relevant to DoRA,
SORA, DeLoRA, EVA and compression papers against actual text/official status.
Focus on whether posthoc active radial removal/quality preservation or rank32
compression support, limit, or refute the authors' ACTUAL claims. Detect closest
prior experiments such as removing/freezing magnitude or normalization; don't
attribute a necessary condition to a paper that only gives a motivating
correlation. Explicitly distinguish training from inference and fixed-checkpoint
from cross-seed evidence. Record URLs and section/table/figure, no large quotes.
Return genuine conflicts/overlap, not predetermined reassurance or novelty.

Root will inspect results and browsing sources, assess paper scope/venues with
explicit uncertainty, and propose bounded analyses of existing data. This stage
does not silently authorize new quality runs or Answer.AI downloads.
