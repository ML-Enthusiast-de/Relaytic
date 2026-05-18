# Relaytic Product Story

Relaytic is The Relay Inference Lab: a local-first structured-data system that turns data, intent, modeling, control, and evidence into auditable artifacts.

Relaytic-AML is the current flagship story because AML forces the product to solve a harder problem than generic model training. A credible AML system must handle rare events, messy labels, graph structure, analyst review budgets, temporal drift, public-claim safety, and human or agent handoff.

## First Viewer Path

The first viewer path should be:

1. Install and check health.
2. Run the public-safe AML review-queue demo.
3. Open mission control.
4. Inspect the top case packet and queue evidence.
5. Inspect business-value and baseline/ablation artifacts.
6. Inspect temporal, environment, benchmark, and public-claim gates.
7. Export a safe context pack for an external reviewer or LLM.

Commands:

```powershell
relaytic doctor --expected-profile full --format json
relaytic demo aml-review-queue --run-dir artifacts\relaytic_aml_demo --format json
relaytic mission-control launch --run-dir artifacts\relaytic_aml_demo
relaytic aml environment --run-dir artifacts\relaytic_aml_demo --format json
relaytic guide export-context --run-dir artifacts\relaytic_aml_demo --audience external-llm --format json
```

## Architecture Map

```text
local data + plain-language goal
  -> governed Relaytic run
  -> task and AML contracts
  -> graph, casework, stream-risk, temporal, baseline, business-value, and environment artifacts
  -> mission control, guide, assist, benchmark, and external context surfaces
  -> claim gates before public or paper-facing statements
```

Every surface reads the same local artifacts. Mission control, guide, CLI, MCP, and external context export are interfaces over that artifact graph; they are not separate sources of truth.

## Proof Links

Start here:

- [Why Relaytic-AML](why_relaytic_aml.md)
- [Paper Benchmark Runbook](paper_benchmark_runbook.md)
- [Relaytic UI Frontier Review](relaytic_ui_frontier_review.md)
- [User Handbook](handbooks/relaytic_user_handbook.md)
- [Agent Handbook](handbooks/relaytic_agent_handbook.md)
- [AML Frontier Contract](specs/aml_frontier_contract.md)
- [AML Benchmark Pack](specs/aml_benchmark_pack.md)

Run evidence to inspect:

- `run_summary.json`
- `reports/summary.md`
- `aml_demo_bundle_manifest.json`
- `aml_investigation_board.json`
- `case_packet.json`
- `aml_business_value_report.json`
- `operational_metric_guard.json`
- `aml_baseline_matrix.json`
- `aml_ablation_matrix.json`
- `aml_temporal_benchmark_claim_report.json`
- `aml_environment_scorecard.json`
- `aml_benchmark_environment_scorecard.json`
- `benchmark_release_gate.json`
- `paper_claim_guard_report.json`
- `aml_public_claim_guard.json`
- `external_llm_context_pack.json`

## Claim Ladder

- **Workflow demo:** the AML review-queue demo shows the user experience, artifacts, and proof path on public-safe fixture data.
- **Engineering benchmark:** dev-benchmark and proxy runs can improve the system and reveal failures.
- **Holdout benchmark:** held-out benchmark runs can support stronger technical claims when leakage, claim, and environment gates pass.
- **Paper-ready release:** the Slice 15Z-R release-freeze pack is the first place where attention-seeking public claims should be treated as stable.

## What A Reviewer Should Notice

Relaytic-AML is strongest when the reviewer can see that the system:

- knows when it has only demo evidence
- knows when a claim is blocked
- exposes the case packet and review budget instead of only AUROC
- separates public claim readiness from model score
- gives humans and external agents a direct path to the artifacts that matter
