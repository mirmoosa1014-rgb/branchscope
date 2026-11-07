# A 90-second walkthrough

0–15 s: Start `python3 -m branchscope.server`, open localhost:8765. Explain that this is synthetic branch prediction, not measured CPU speed.

15–35 s: Run delayed correlation at seed 101, 256 bytes, history 8. Compare error percentages and used storage. Random source/distractor branches explain the remaining error.

35–55 s: Scrub the neuron inspector. Read the address, table row, signed score and actual outcome. The bars show weight × history before training on that outcome. Review the first sixteen decisions; misses have an explicit ×, not color alone.

55–75 s: Switch to XOR and run again. Observe the gshare/perceptron comparison. The nonlinear workload is an intentional failure case, not hidden from the report.

75–90 s: Export JSON. Point to seed, warmup, per-site counts and the actual model snapshot. End with the full benchmark figure and the limitations: no real traces, timing model or silicon claim.
