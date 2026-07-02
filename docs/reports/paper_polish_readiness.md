# Paper P20 Polish Readiness

P20 checks whether the current paper reads as a professional AI systems/evaluation paper rather than an internal benchmark export. It does not add benchmark results or relax claim boundaries.

- Status: `ready_for_final_pdf_preflight`
- Paper content ready for P21 source/PDF preflight: `True`
- Upload ready now: `False`
- Next slice: `Paper Track P21 - final source/PDF preflight and release changelog`

## PaySim Story

- Best probe: `XGBoost` at validation PR-AUC `0.5944` on the probe surface.
- Selected full finalist: `Extra Trees` at validation PR-AUC `0.5687` before the fixed test.
- Fixed-test PR-AUC: `0.6388`.
- Test-surface policy: `nonselected_competitive_finalists_have_no_test_metrics`.

## Guidance Path

- README path ready: `True`
- Paper avoids internal planning-file guidance: `True`
- Cross-platform commands visible: `True`

## Remaining Human Work

- compile and inspect the final PDF from the regenerated source bundle
- run LaTeX warning, font-embedding, metadata, and rendered-page checks
- confirm a clean git tag target before any public upload
