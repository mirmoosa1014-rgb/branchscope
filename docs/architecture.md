# Architecture

`workloads.py` generates a complete synthetic trace; only `(PC)` reaches `predict`. `experiment.py` records the prediction and pre-update score, then gives `(PC, actual)` to `resolve`. Resolution recomputes the same score from unchanged state and trains the addressed row before shifting history. No current outcome or future branch enters the prediction features. Tests flip the current/future suffix and assert unchanged predictions through the first changed outcome.

`predictors.py` holds all persistent simulation state. PC addresses are four-byte aligned. Bimodal indexes `(PC >> 2) modulo entries`; gshare XORs the shifted PC and global history then masks to the power-of-two table. Perceptron uses PC modulo the number of weight rows and the signed resolved-history vector. History is newest-first. Counter tables begin weakly not-taken; weights begin zero; history begins not-taken. Warmup updates every predictor but is excluded from metrics.

`experiment.py` chooses the perceptron history using validation only, then runs a fixed test sweep. Whole seeds are separated, not random branches from one stream. `results/` is the reproducible evidence; `models/` contains an inspectable post-demo weight snapshot. The model has no external training library or pickle loader.

`server.py` serves only `web/` and two API routes on 127.0.0.1. POST bodies are JSON, at most 1 KiB, with known fields and bounded values. Browser cross-origin POST requests are rejected. No uploads, shell commands, remote data or file paths are accepted. The stdlib server is for a single local user, not public deployment. Each run constructs fresh predictors and performs 6,000 branches per algorithm.

`web/` is framework-free HTML/CSS/JavaScript. It visualizes actual API results, never fabricated scores. No build step or runtime npm dependencies are required. Optional Playwright is pinned and locked for browser verification only. `scripts/figures.py` uses matplotlib solely for standalone research artifacts.

## Storage model

Bimodal: `2 × entries` bits. Gshare: `2 × entries + history` bits. Perceptron: `8 × entries × (history + 1) + history` bits. The extra weight is the bias. Counters use the largest power-of-two entry count fitting the ceiling; perceptron uses the largest integer row count fitting it. Always taken is zero bits. Actual used bits are reported because rounding leaves unused space. This counts persistent logical predictor state, not Python object memory, combinational logic, addresses, tags, arithmetic units, or speculative checkpoints. Latency and chip area are not modeled.
