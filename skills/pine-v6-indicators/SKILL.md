---
name: pine-v6-indicators
description: Write, fix, port or optimise TradingView Pine Script v6 indicators (indicator() scripts that plot, draw, alert or show tables), and verify them by compiling, checking runtime errors and comparing values. Use when the user asks for a Pine Script or TradingView indicator, overlay, oscillator, dashboard or multi-timeframe tool; pastes //@version=4/5/6 code to fix or port; or quotes a Pine compile or runtime error (CExxxxx, RExxxxx). Also covers the indicator side of strategy() scripts (plots, drawings, alerts), but not order logic or backtest evaluation.
---

# Pine Script v6 indicators

Write TradingView indicators in Pine Script v6, then prove they work. A script counts as done when the checks in the loop below have passed. Looking right is not enough. The official manual is the authority: https://www.tradingview.com/pine-script-docs/ (reference manual: https://www.tradingview.com/pine-script-reference/v6/). The reference files here hold the parts models most often get wrong. Each file names its docs sources and the date they were checked, and `references/pine-v6-gotchas.md` marks every rule as *documented* or *observed*.

## The loop

Run every step. When a step cannot run in the current setup, say so on the hand-off's *Not verified* line. Never skip it silently.

1. **Spec.** In one short block, write down the inputs, the outputs (plots, drawings, alerts, tables), the pane (overlay or separate), the intended timeframes, and whether the indicator may repaint. The default is that it may not. If the request is clear, pick defaults and state them; ask only when a choice changes the output.
2. **Write.** Follow the skeleton below and read `references/pine-v6-gotchas.md` before writing. Read the matching reference for the job:
   - `references/correctness.md` for any `request.*()`, signal or alert;
   - `references/visuals-cookbook.md` for drawings or tables;
   - `references/limits-and-performance.md` for loops, arrays or heavy history.

   Add a `debugMode` input that guards the script's invariants (see `references/correctness.md#invariants`).
3. **Static check.** Go through the checklist at the end of this file: v6 traps, budget counts, and the repainting audit.
4. **Compile.**
   - *With a TradingView MCP connected:* follow `references/tradingview-mcp.md`. Inject, compile, read errors, fix, and repeat until there are 0 errors. Fix every warning or justify it in one line.
   - *Without one:* give the user the file and ask them to paste the Pine Editor's full error and warning output. Iterate on what they paste. Never claim a clean compile you did not see.
5. **Runtime.** A clean compile can still fail when the script runs, with errors such as RE10139 (memory) or RE10143 (historical buffer). Run the script on at least two symbols and two timeframes, one of them intraday. A failing study shows an error icon next to its name in the chart legend (observed UI behaviour, not documented). With the MCP, look for it in a chart screenshot; without one, ask the user. Stop when no study shows an error and the Pine Logs hold no `log.error` from the `debugMode` guards.
6. **Values.** Recompute the core series independently, for example in Python from the same OHLCV. Compare it with the script's own `log.info` spot prints at 5 or more bars spread across history; read them with the MCP's console tool, or ask the user to paste the Pine Logs. Chart read-outs show only the bar under the crosshair, so they are not a source for historical values. The tolerance is one tick, or 1e-6 relative for derived values. A mismatch is a bug until it is explained.
7. **Repainting.** Confirm that every signal and higher-timeframe value uses a non-repainting pattern (`references/correctness.md#repainting`), unless the spec allowed repainting. With the MCP, step through bar replay and check that confirmed signals do not move.
8. **Visual.** Take a screenshot, or ask the user to look. Judge the result against the spec, not against "looks fine".
9. **Hand-off.** Report verification as numbers, for example: "0 compile errors, 0 warnings, 0 runtime errors on 2 symbols × 2 timeframes, 5 of 5 spot bars match". Then give a *Not verified* line, which lists every step above that could not run.

## Script skeleton

```pine
//@version=6
indicator("Name", shorttitle = "Short", overlay = true)

// ---- Inputs ----
int   lengthInput = input.int(20, "Length", minval = 1, group = "Settings")
color upColor     = input.color(color.teal, "Up color", group = "Style")
bool  debugMode   = input.bool(false, "Debug checks", group = "Debug")

// ---- Calculations ----
float basis = ta.sma(close, lengthInput)
float hh    = ta.highest(high, lengthInput)  // stateful ta.* calls stay in the global scope
float ll    = ta.lowest(low, lengthInput)

// ---- Invariants (debugMode) ----
if debugMode and not na(basis) and (basis > hh or basis < ll)
    log.error("basis outside the high/low range at bar {0}", bar_index)
if debugMode and (bar_index % 500 == 0 or barstate.islast)
    log.info("bar {0} basis {1}", bar_index, basis)  // spot prints for the value check

// ---- Visuals ----
plot(basis, "Basis", color = upColor, linewidth = 2)

// ---- Alerts ----
bool crossUp = ta.crossover(close, basis) and barstate.isconfirmed
alertcondition(crossUp, "Cross up", "{{ticker}} closed above the basis")
```

Section order: version, declaration, inputs (each with a title and a `group`), calculations, invariants, visuals, alerts.

## Defaults unless told otherwise

- Use `//@version=6`. When porting, never just bump the version number; port with `references/pine-v6-gotchas.md`.
- Prefer built-in `ta.*` functions to hand-rolled loops. They are tested and faster.
- Put bands, moving averages and levels on the price pane (`overlay = true`). Put oscillators in their own pane.
- Signals fire on confirmed bars only (`barstate.isconfirmed`), unless the spec says otherwise.
- Add an alert for every clear signal. Use `alertcondition()` for static messages and `alert()` when the message needs runtime values (`references/correctness.md#alerts`).
- Create persistent objects (tables, live lines, arrays) once with `var` and update them; never recreate them every bar.
- Write the script to a `.pine` file, unless the user's house style says otherwise. On revisions, edit that file in place rather than re-pasting the whole script.

## House style (override per user)

Teams often have their own conventions: the file extension, the input layout, whether long, short and exit signals are separate or combined, and naming. If a user or project states one, it wins over the defaults above. Ask once when a convention would materially change the script.

## Pre-hand-off checklist

- [ ] `//@version=6` is the first line.
- [ ] No bare `na` is passed to an untyped function parameter. Cast it: `float(na)`.
- [ ] No `[]` on a literal, a built-in constant or a UDT field. Use `(obj[1]).field`.
- [ ] Every `if`/`switch` producing a value of a "unique" type (plot or line style, etc.) has an `else` or `default` branch.
- [ ] No int or float is used as a bool without `bool(...)`. No bool can be `na`.
- [ ] Every stateful `ta.*` call runs on every bar, in the global scope. None sits only inside an `if`, a ternary, or the right side of `and`/`or`.
- [ ] There are no `x == na` or `x != na` comparisons; use `na(x)`.
- [ ] Budgets are within limits: plot count ≤ 64, unique `request.*()` calls ≤ 40, drawings within their `max_*_count`, and history references within the buffer (`references/limits-and-performance.md`).
- [ ] Repainting audit is done. Every `request.security()` call uses the `[1]` + `lookahead_on` pattern or is justified, and signals are gated on `barstate.isconfirmed`.
- [ ] Inputs are titled and grouped. Colours and lengths are inputs, not hard-coded.
- [ ] The hand-off states verification as numbers and has a *Not verified* line.

## Reference files

- `references/pine-v6-gotchas.md`: v5-to-v6 breaking changes and observed compiler traps. Read it before every script.
- `references/correctness.md`: the execution model, repainting, `request.security()` patterns, alerts, `log.*` debugging, invariants and the value check.
- `references/limits-and-performance.md`: platform limits, the Pine Profiler, and optimisation patterns.
- `references/visuals-cookbook.md`: plots, fills, shapes, lines, boxes, labels, tables and colours.
- `references/tradingview-mcp.md`: the compile and verify loop through a TradingView Desktop MCP server, and its known hazards.
