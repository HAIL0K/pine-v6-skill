# Correctness: execution model, repainting, alerts, debugging

How Pine runs, why indicators repaint, how to request other timeframes, and alerts. The last three sections (debugging, invariants, checking values) are the deeper checks to offer when a user asks to verify a script, or when its signals will drive real trades; simple visuals don't need them. Checked against the docs on 2026-10-13.

## Contents
- Execution model
- Repainting
- `request.security()` patterns
- Alerts
- Debugging with `log.*`
- Invariants
- Checking values

## Execution model

Docs: [Execution model](https://www.tradingview.com/pine-script-docs/language/execution-model/).

- A script runs once per historical bar, on that bar's close. On the realtime bar it runs on every tick, and before each tick it rolls back every variable to its value at the last bar close. A `var` keeps its value across bars but still rolls back within the realtime bar. A `varip` does not roll back.
- So a historical bar sees only its final values, while the realtime bar sees intermediate ones. Anything that looks at intrabar state (`close` mid-bar, `varip` counters) behaves differently on the two kinds of bar. That difference is where most repainting comes from.
- `barstate.isconfirmed` is true on a bar's final execution: on every historical bar, and on the closing tick of the realtime bar. Gating a signal on it makes the realtime result match what history will later show.
- `barstate.islast` is true on the last bar, including on every realtime tick. Use it to draw tables and other one-off drawings once instead of on every bar.
- Docs on `varip`: scripts that use it "cannot be backtested", and their historical plots may not reflect realtime behaviour. Use it only for realtime-only tools.

## Repainting

Docs: [Repainting](https://www.tradingview.com/pine-script-docs/concepts/repainting/).

A script repaints when its values or signals on past bars differ from what it showed live. When checking a script for repainting, look at four things:

| Source | Repaints? | Fix |
|---|---|---|
| `request.security()` on a higher timeframe with the default `lookahead_off` | **Yes.** On the realtime bar it returns the developing higher-timeframe value, which changes. | Use the non-repainting pattern below. |
| `request.security(..., lookahead = barmerge.lookahead_on)` *without* `[1]` | **Yes, and worse:** it leaks future data on historical bars. | Never use this combination. |
| Signals computed from `close`, `high` or `low` of the realtime bar | Yes: they flicker within the bar. | Gate on `barstate.isconfirmed`. |
| `varip`, `timenow`, `chart.*visible*` | Yes, by design. | Allow only if the spec says so. |

The documented non-repainting pattern: the `[1]` and `lookahead_on` are interdependent, and removing either breaks it.

```pine
//@version=6
indicator("No-repaint HTF close", overlay = true)
string tfInput = input.timeframe("1D", "Higher timeframe")

noRepaintSecurity(string sym, string tf, float src) =>
    request.security(sym, tf, src[1], lookahead = barmerge.lookahead_on)

float htfClose = noRepaintSecurity(syminfo.tickerid, tfInput, close)
plot(htfClose, "HTF close (previous, confirmed)", color = color.purple, linewidth = 2)
```

This gives the *previous confirmed* higher-timeframe value. That is the cost of not repainting: it lags one higher-timeframe bar. Say so in the hand-off.

Do not quietly fill early `na`s from the request with the chart's own values (`na(htf) ? close : htf`). That mixes timeframes without telling anyone; leave them as `na`.

## `request.security()` patterns

Docs: [Other timeframes and data](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/).

- Combine values from the same context into one call that returns a tuple: `[h, l] = request.security(sym, tf, [high, low])`. This saves request budget (40 unique calls) and is faster. A UDT can carry more than a tuple can, and every request shares a 127-element tuple cap.
- For lower timeframes, use `request.security_lower_tf()`, which returns arrays. Bound the history it pulls with `calc_bars_count`, and guard the array id against `na`.
- Requesting the chart's own timeframe adds nothing but cost. Skip the call.
- Data for another symbol inherits the chart's adjustment settings only through `ticker.inherit()` or a `ticker.new()` built with the same settings.

## Alerts

Docs: [Alerts](https://www.tradingview.com/pine-script-docs/concepts/alerts/).

- `alertcondition(cond, title, message)` defines a condition the user picks in the Create Alert dialog. Its message is a constant string with `{{placeholders}}`. It costs one plot count.
- `alert(message, freq)` fires from script logic, and its message can include runtime values (`str.tostring(rsi, "#.##")`). For confirmed signals, use `freq = alert.freq_once_per_bar_close`. The user creates one "Any alert() function call" alert per script.
- Default to `alert()` when the message needs values, and to `alertcondition()` when the user wants separate selectable conditions. Many scripts offer both.
- Gate both on confirmed bars unless the spec wants intrabar alerts. Alerts that fire from realtime intrabars are, in the docs' words, potentially "heavily misleading".

## Debugging with `log.*`

Docs: [Debugging](https://www.tradingview.com/pine-script-docs/writing/debugging/).

- `log.info()`, `log.warning()` and `log.error()` write to the Pine Logs pane, with a timestamp and a link back to the source line. They take a format string: `log.info("bar {0} rsi {1}", bar_index, rsi)`.
- Print spot values for the value check at fixed bars, so the run is reproducible: `if bar_index % 500 == 0 or barstate.islast`.
- With the MCP, read the logs with `pine_get_console`. Without it, ask the user to paste them.
- `runtime.error(msg)` halts the script with a visible error. Use it only for "this must never happen" states, inside `debugMode`.

## Invariants

When verifying a script, add a `debugMode` input (off by default) that checks what must always hold, and logs a `log.error` when it doesn't. Typical invariants:
- Bands: `upper >= basis` and `basis >= lower` whenever all three are not `na`.
- Oscillators stay inside their range (RSI 0 to 100, a stochastic 0 to 100).
- A signal never fires on an unconfirmed bar, if the spec bans repainting: `if debugMode and signal and not barstate.isconfirmed`, then `log.error(...)`.
- Counters and running sums never go negative or `na` after warm-up.

The invariants catch logic errors that compile cleanly. With them in place, "0 `log.error` lines" becomes a check that means something.

## Checking values

The compiler checks syntax; this check covers the maths.

1. Pick at least 5 bars spread across history (early, middle, recent, and the last confirmed bar), avoiding the warm-up period.
2. Get the script's values at those bars: with the MCP, read plotted values, tables or labels; without it, use the `log.info` spot prints the user pastes.
3. Recompute the same quantity independently from the same OHLCV, for example in pandas. Do not port the Pine code line by line: an independent route is what catches a shared mistake. Match Pine's own definitions, such as `ta.rsi` using RMA (Wilder) smoothing and `ta.stdev` the population standard deviation, from the [reference manual](https://www.tradingview.com/pine-script-reference/v6/).
4. Require a match within one tick, or 1e-6 relative for derived values. Report it as "N of N spot bars match".
5. A mismatch is a bug until it is explained, for instance by a different data feed, session or adjustment. Write the explanation into the hand-off.
