# Evaluation protocol

All data is synthetic, generated locally with Python's seeded `random.Random`. No external dataset or real hardware is used. The same materialized trace is reused for every algorithm and budget within a workload/seed pair. Each model resets before each run.

- Validation seeds: 11, 12, 13. Choose history at 256 bytes using the arithmetic mean over six workloads and three seeds.
- Test seeds: 101, 102, 103, 104, 105. No test seed enters configuration selection.
- Full length: 12,000 branches, warmup: 512, scored: 11,488.
- Algorithms: taken, bimodal, gshare, perceptron. Byte ceilings: 64, 128, 256, 512, 1024.
- Full result rows: 6 × 5 × 5 × 4 = 600. The zero-state taken predictor repeats across ceilings as a reference.
- Quick mode: one validation seed, two test seeds, 3,000 branches. It writes `artifacts/quick`, never overwriting published evidence. Its selected history may differ.

## Workloads

Loop: seven taken outcomes and one exit, cycling eight sites. Biased: sixteen sites with 90% or 10% taken probabilities. Delayed: random source, seven random distractors, then a target copying that source (eight branches back). XOR: two random sources followed by their XOR. Phase: biased sites reverse at each quarter of a trace. Random: independent fair outcomes at one site. Workload generation is not a model of actual instruction scheduling.

Validation error by history is saved alongside every full result. The selected history is shared across algorithms with histories and all test budgets; this is a controlled fixed-history comparison, **not separate best-possible tuning for every algorithm or budget**. Bimodal has no history. Table rounding means equal ceilings do not guarantee equal used bits. Each row reports logical used bits.

The metric is `100 × misses / scored conditional branches`, not MPKI (we do not simulate total instructions). Per-PC counts allow separating predictable targets from random sources. Time plots use non-overlapping windows of 256 scored branches, with the final partial window correctly normalized. The demo has 6,000 branches and is separate from the 12,000-branch full report.

The storage figure averages the six workloads within each test seed, then reports mean and sample standard deviation over five seeds. Bands are variability summaries, not confidence intervals. No statistical significance or speedup is claimed. We include failures rather than choosing only successful workloads. Raw CSV and JSON are committed; tests verify metrics from counts and exact demo reproduction.

## Limitations and next experiments

No speculative updates/rollback, predictor latency, energy, instruction timing, real traces, neural probability calibration, or hardware synthesis. Error differences cannot be converted directly into CPU speedups. Fair future extensions include separately tuning each baseline on validation only, adding real licensed traces and testing held-out workload families. Do not tune on the published test seeds and then call the same test untouched.
