# Bounded joint affine prototype: calibration only

Frozen before outputs. Four preselected projections Q/K/V/O at layer17.
Use the already captured8case gradient/input covariances from the orientation
probe. No new inference, no validation use, no weights training.

Objective: tr(G (Wteacher−D W0−LR) C (Wteacher−D W0−LR)^T).
For fixed D: exact two-sided SVD. For fixed LR: exact coupled diagonal solve
H d = diag(G (Wteacher−LR) C W0^T), H=G elementwise(W0 C W0^T).
Run exactly5block cycles, starting at sourceD. This alternating least-squares
principle is known; private use for DoRA compression is not yet established
as novel. Nearby prior: OBD, KFAC, EoRA, SigmaScale, ChainDoRA; bounded search
on joint posthoc DoRA calibration found no confirmed exact predecessor.

Rank for each module is its frozen structural_uniform rank7/8 from the whole
adapter. D cost is counted. Local module budgets can differ from ordinary
rank8; only the eventual144module adapter would have exactly matched total
budget. Do not claim matched-budget algorithm superiority from this probe.

Compare local error to fixed-D two-sided SVD and ordinary rank8two-sided SVD.
Check exact block optima/monotonic decrease, finite deployed FP32 factors,
nondegenerate D and actual parameter counts. Gate for considering a full
candidate: at least10% aggregate improvement over fixed-D, with no clear
aggregate disadvantage to ordinary two-sided SVD. A positive proxy gate
does not guarantee teacher KL, accuracy, novelty or conference level.
Do not tune the number of iterations or covariance shrinkage after outputs.
