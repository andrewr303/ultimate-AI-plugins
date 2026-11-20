# How the Example Widget hinge is tested

The Example Widget hinge test is a bench procedure that opens and closes the lid until the pin wears out. Last verified 2026-10-12 against the [Example Labs test protocol](https://example.org/labs/hinge-protocol).

The Model 3 hinge survived 20,000 cycles in the 2025 run. This is one snapshot from a single lab, not a guarantee for every home.

| Model | Cycles | Price |
| --- | --- | --- |
| Model 2 | 12,500 | $9 |
| Model 3 | 20,000 | $12 |

```bash
widget-bench --model 3 --cycles 20000
```

Results may vary with humidity. Read the [raw data](https://example.org/labs/hinge-2025.csv) before quoting the figures.
