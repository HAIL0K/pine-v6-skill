# Limits and performance

Source: [Limitations](https://www.tradingview.com/pine-script-docs/writing/limitations/) and [Profiling and optimization](https://www.tradingview.com/pine-script-docs/writing/profiling-and-optimization/), checked 2026-10-13. Several limits depend on the user's TradingView plan and change over time. Check the live page before designing around an edge.

## Limits

| Resource | Limit |
|---|---|
| Plot count | 64 per script. One call can cost 1 to 7: `plotcandle()` can cost 7. `alertcondition()`, `bgcolor()` and `barcolor()` count. `fill()` counts only with a series colour. |
| Lines, boxes, labels | The last 50 of each are shown by default. Raise with `max_lines_count`, `max_boxes_count` and `max_labels_count`; the hard cap is 500 each. |
| Polylines | 50 by default, cap 100 (`max_polylines_count`). |
| Tables | One per `position.*`, so 9 at most. A second table at the same position replaces the first on screen. |
| Unique `request.*()` calls | 40, or 64 on the Ultimate plan. Identical calls count once. Calls inside libraries count. |
| Tuple elements across all requests | 127. For more, pack values into a UDT. |
| `request.footprint()` | One unique call; runs only on Premium and Ultimate. |
| Intrabars via `request.security_lower_tf()` | 100K bars (Basic to Premium), 125K (Expert), 200K (Ultimate). Bound with `calc_bars_count`. |
| History buffer for `[]` | 5,000 bars for most series; 10,000 for `open`, `high`, `low`, `close` and `time`. |
| Drawings at `xloc.bar_index` | 10,000 bars into the past, 500 into the future. |
| Compiled size | 100,256 tokens of compiled code; unused code is not counted. Imported libraries total at most 1M. |
| Variables | 1,000 per scope. |
| Collections | 100,000 elements per array or matrix; 50,000 key-value pairs per map. |
| Loop time | 500 ms per loop on any single bar. |
| Total execution | 20 s on Basic accounts, 40 s on others. |
| Compilation | 2 minutes. After three consecutive timeout warnings, compiling is blocked for an hour. |

A drawing with `na` coordinates still uses up its type's budget. To skip one, put the `.new()` call itself inside an `if`.

## Optimisation, in order of payoff

1. **Use built-ins rather than loops.** `ta.highest()`, `ta.sma()` and `math.sum()` beat hand-written lookback loops; the docs' benchmark shows this.
2. **Make one request per context.** Merge `request.security()` calls on the same symbol and timeframe into one tuple call. This saves both time and budget.
3. **Compute once.** Assign a repeated expression to a variable rather than writing it out again.
4. **Work incrementally, not from scratch.** Keep running state in `var` (sums, counters, arrays) and update it each bar, rather than looping over the last N bars on every bar. A loop whose length grows with `bar_index` is a bug waiting for the 500 ms limit.
5. **Update drawings rather than recreating them.** Create a line, box or table once with `var`, then move it with its setters (`line.set_xy1()`, `box.set_top()`, `table.cell()`). The docs measure setters as cheaper than delete-and-recreate.
6. **Gate last-bar work.** Fill tables and draw one-off labels inside `if barstate.islast`.
7. **Bound history.** Set `max_bars_back` and `calc_bars_count` to what the script needs, not more.

## Pine Profiler

Open the script in the Pine Editor with it on a chart, then choose More → Profiler mode. The Profiler shows estimated time per line and block, along with execution counts, and marks the top three hotspots with a flame icon. Use it after the first clean run when a script feels slow or nears the 20/40 s budget, then optimise the hot lines first. Results are estimates, because profiling adds its own overhead.

The MCP cannot read Profiler output. Ask the user to switch it on and report the flagged lines.
