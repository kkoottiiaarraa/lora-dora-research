# CUDA normalizer diagnostic


Under CUDA BF16 autocast, build full FP32 identity, apply two F.linear operations, transpose BF16 product, add to FP32 base, compute FP32 row norm and FP32 quotient. Every module norm is bitwise compared with installed PEFT DoraLinearLayer.get_weight_norm. Flags are recorded without modification. A direct B@A shortcut is not used.


Pilot/full reproducibility tolerance was fixed at8FP32 eps relative and0 absolute, before seeing results. Exact comparisons and measured errors are retained. CUDA tensor wall and stream-event intervals include host synchronization gaps between operations; neither measures pure compute or utilization. Process-minus-initial-hashio is an approximate residency upper bound through metadata snapshot, excluding import startup and tiny final writes. Failed cleanup attempts retain raw artifacts and separately reported measured tensor intervals, with full failed process times unavailable. No p-values over rows/modules. Normalizer agreement does not establish full-function equality or a training cause.


