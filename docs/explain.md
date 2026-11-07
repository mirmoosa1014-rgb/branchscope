# Explain it without a microarchitecture course

A program often asks a yes/no question. A processor would like to guess the answer before waiting for it. A wrong guess wastes work. Here, a tiny learner keeps a score for recent answers. It predicts, sees the real answer, then changes its scores. The next guess uses only what has already happened.

The always-taken predictor always says yes. Bimodal keeps a little habit counter for each address. Gshare combines the address with recent answers to choose a counter. The perceptron adds weighted recent answers. Some patterns suit one approach better than another; this lab lets you inspect the mistakes.

## Ten reviewer questions

1. **Is the data real?** No, explicitly synthetic branch streams.
2. **Where is the machine learning?** Integer perceptron weights train after each outcome resolves.
3. **Can the model see the answer?** Only after its prediction is recorded; a suffix-change test checks this.
4. **How is tuning separated?** Validation seeds choose H; test seeds evaluate the fixed choice.
5. **Does test-time training leak?** It is an online protocol: previous resolved labels are allowed, current labels are not.
6. **Is the comparison equal-size?** Equal storage ceilings, actual used bits reported; rounding differs.
7. **Does a bigger model always win?** No. Longer history uses more weights per row, reducing rows and increasing collisions.
8. **Why show random branches?** They reveal whether the experiment is claiming impossible predictability.
9. **Where does learning fail?** XOR, phase reversal, random outcomes and aliasing provide counterexamples.
10. **Does this prove a faster chip?** No. Real traces, hardware cost, prediction latency and speculation need separate validation.
