# Project summary

BranchScope is an educational CPU branch-prediction simulator with online perceptron learning, counter baselines, reproducible synthetic traces, storage-budget experiments and an interactive explanation of each prediction.

Measured evidence: 600 full evaluations with separate validation and test seeds, six workload families, five storage ceilings and four algorithms. At 256 bytes, the perceptron improves delayed-correlation error while losing to gshare on XOR and bimodal on phase reversal. No universal superiority or real-hardware benefit is claimed.

Truthful portfolio bullet: “Directed an AI-assisted branch-prediction lab comparing online perceptron learning with counter baselines across 600 reproducible synthetic evaluations, with a live trace viewer and documented failure cases.”

Contribution boundary: the owner supplied goals and authorization; Codex substantially implemented and validated this version. Revise the bullet if the owner later personally extends, reviews or measures the system, based on actual work.
