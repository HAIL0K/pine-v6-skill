# Changelog

## 1.0.0 (2026-10-13)

First public release, built from a private skill used since 2026-08.

- The skill now runs a verification loop with stop criteria: compile, runtime, value check against an independent recompute, repainting audit, visual check. The hand-off reports numbers and a *Not verified* line. Before this, it checked only against the model's memory.
- Every v6 rule is checked against the TradingView docs (2026-10-13) and marked *documented* (with a link) or *observed*.
- New references: `correctness.md` (execution model, repainting, alerts, `log.*`, invariants, value check), `limits-and-performance.md` (limits, Profiler, optimisation) and `tradingview-mcp.md` (the MCP compile loop and its known hazards).
- Fixed the cookbook's live-line example, which created a new line on every realtime tick, and its higher-timeframe advice: `lookahead_off` alone still repaints.
- Removed one user's personal preferences and client-specific tool names.
- Added complete example scripts, a known-bad canary, `check_skill.py` (CI) and `compile_examples.py` (opt-in compile check).
