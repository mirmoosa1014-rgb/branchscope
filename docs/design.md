# Visual provenance

Consulted the local checkout of [TheRollerBlader/motion-graphic-style-library](https://github.com/TheRollerBlader/motion-graphic-style-library), specifically `catalog/neon.md` (Neon Night). Adopted its near-black background, cyan/magenta signals, square corners, strong uppercase display typography and monospace instrument labels. The main interface is a trace instrument and neuron inspector rather than repeated dashboard cards.

Motion is intentionally adapted: no flicker or perpetual pulse while reading research data. Reduced motion disables smooth scrolling. No external fonts or visual assets load at runtime. SVG charts are generated directly from API results; the standalone research figure uses matplotlib and a separate perceptual heatmap for numeric readability. Color is supplemented with names, numeric values and explicit hit/miss symbols.

The implementation is original code using the library as a visual reference. No library code or images are redistributed. Screenshots in `docs/images` are captured from the actual running local app by `scripts/browser-check.mjs`, including mobile and reduced-motion captures.
