# Posthoc restoration of the zero-ranked K projection

Both frozen allocators assigned rank0 to K in layer1. Test whether restoring
that native projection rescues the excess error, while every other projection
stays at its already frozen compressed state. This is an exploratory diagnostic
chosen after allocation outputs, not independent method validation.

Three conditions: weighted_uniform_restore_k1, weighted_allocated_restore_k1,
structural_allocated_restore_k1. Same64development cases and cached native
teacher logits as the completed diagnostic. Native reference checks unchanged.
No new data selection or fitting. Compare against their original conditions.

Restoration adds native adapter parameters, so this is **not** an equal-budget
compression algorithm. Report added storage explicitly. The uniform restoration
controls for the benefit of restoring K1 even without rank allocation.
Interpret a rescue as evidence about this composition of endpoint interventions,
not about training causes or a unique cause independent of other projections.

Source/hash/case alignment, finite metrics and complete3×64coverage required.
Report paired changes and fraction of allocation excess KL removed. No
algorithm novelty or task-accuracy claim from prefix fidelity alone.
