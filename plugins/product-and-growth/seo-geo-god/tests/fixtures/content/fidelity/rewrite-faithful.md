# How the Example Widget hinge is tested

The Example Widget hinge test is a bench procedure: the lid opens and closes until the pin wears out. The [Example Labs test protocol](https://example.org/labs/hinge-protocol) describes the procedure, which was last verified 2026-10-12.

In the 2025 run, the Model 3 hinge survived 20,000 cycles. That figure is one snapshot from a single lab and not a guarantee for every home.

| Model | Cycles | Price |
| --- | --- | --- |
| Model 2 | 12,500 | $9 |
| Model 3 | 20,000 | $12 |
| Model 4 | 24,000 | $15 |

```bash
widget-bench --model 3 --cycles 20000
```

Results may vary with humidity, so read the [raw data](https://example.org/labs/hinge-2025.csv) before you quote the figures.
