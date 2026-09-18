# Model Attribution Experiment

Can a piece of observed text or a set of agent actions be traced back to the specific model that produced it, using only black-box evidence — no ability to query the model, no cooperation from whoever deployed it? This question was sharpened by HuggingFace's July 2026 incident write-up, where defenders could reconstruct an attacker's ~17,600 agent actions but never determined which model had driven them; the answer ultimately came from the attacker's own provider, not from any attribution technique applied to the evidence itself.

## Current experiment

Prior work (Ediga et al., "Trace") showed a classifier can identify which LLM produced a set of terminal agent actions with high accuracy when the agent scaffold it's running in was seen during training, but accuracy drops substantially when that scaffold is held out. That result covers only three scaffolds. Separately, other work on software-engineering agents found that the choice of framework can explain more behavioral variance than the choice of underlying model — suggesting an attribution signal might be picking up scaffold artifacts rather than the model itself.

This experiment tests whether a model-identity signal survives an agent scaffold a classifier has never seen, at a larger scale than three known scaffolds, using public SWE-bench agent-trajectory archives (no API calls to any model required). The approach is staged:

1. **Coverage check** (Stage 0) — build a model × framework matrix from public trajectory archives to confirm there's enough overlapping data to run the test at all.
2. **Pipeline pilot** (Stage 1) — get feature extraction and classification working end-to-end on one clean dataset, and measure how much signal is lost by mapping different frameworks' logs onto a shared action vocabulary.
3. **Cross-framework test** (Stage 2) — train a classifier on a balanced set of frameworks and models, then test on a framework held out entirely, comparing against the same-framework accuracy ceiling.

## Status

Design finalized. Stage 0 (coverage check) not yet run.
