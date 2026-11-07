# Model card: online perceptron

Purpose: inspect a small, transparent branch-direction learner on synthetic traces. Not for predicting real CPU performance.

Inputs: PC-derived table row; bias input 1; last H resolved outcomes encoded as +1 (taken) or -1 (not taken). No current label, future branch, workload identity or random generator state enters a prediction. The score is the bias plus weighted history sum. Score >= 0 predicts taken; the score is not a probability.

After resolution, train on an incorrect prediction or absolute score <= floor(1.93H + 14). Add actual-sign × input to each weight and saturate to [-128,127]. The threshold formula and core educational learning mechanism are drawn from [Jiménez and Lin](https://www.cs.utexas.edu/~lin/papers/hpca01.pdf). We use a straightforward serial simulator and do not reproduce their pipeline or hardware implementation.

History candidates 4, 8, 16, 32 are compared at a 256-byte ceiling on seeds 11–13, all six synthetic families. The lowest macro-average validation error selects H; ties choose smaller H. Final H=8. Test seeds 101–105 are not used for tuning. These are new seeds of known workload families, **not held-out families**. Online adaptation on a test trace is intentional: every outcome is scored before it becomes training evidence.

`models/demo-perceptron.json` is format version 1, signed integer weights, H=8, 8-bit weight width, final resolved history and training threshold. It comes from the delayed-correlation demo, seed 101, 6,000 branches, 256-byte ceiling. It is a post-run diagnostic snapshot, not an initialization for benchmark or UI runs, and not an exported production hardware implementation.

Known failures: nonlinear relationships such as XOR, insufficient history for delayed signals, destructive table aliasing, abrupt phase changes, and unpredictable random outcomes. More history can hurt because it reduces rows at a fixed storage ceiling. Synthetic accuracy provides no evidence of real-world usefulness without real trace evaluation and timing/area analysis.
