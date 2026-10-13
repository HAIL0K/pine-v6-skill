# Changelog

## 1.0.0 (unreleased)

First public release, built from a private skill used since 2026-08.

- The skill is organised around what users ask for: build an indicator, fix an error, convert from v4/v5, add features, explain repainting. Each job has a short, fixed hand-over: the script, how to add it, the settings, and an honest compile status.
- It compiles on the user's chart when a TradingView MCP server is connected. Otherwise it says the script is not compiled and asks for the error text. It never claims a compile it did not see.
- Deeper checks (repainting, values against an independent calculation, a second symbol and timeframe) are offered when the user asks to verify, or when signals will drive trades. They are not forced on simple visuals.
- The v6 rules were checked against the TradingView docs (2026-10-13). Each reference names its sources, and the gotchas file marks every rule *documented* or *observed*.
- Fixed the old cookbook's live-line example, which created a new line on every realtime tick, and its higher-timeframe advice: `lookahead_off` alone still repaints.
- Removed one user's personal preferences and client-specific tool names.
- Added example scripts (3 of 3 compile with 0 errors and 0 warnings on TradingView's compiler, 2026-10-13, as do the 2 complete scripts in the skill's docs), a known-bad canary (fails as expected), `check_skill.py` (CI), `compile_examples.py` (opt-in), and a release workflow that attaches the claude.ai zip.
