---
name: pine-v6-indicators
description: Write, fix, convert or improve TradingView Pine Script v6 indicators (indicator() scripts that plot, draw, alert or show tables). Use when the user asks for a TradingView indicator, overlay, oscillator, dashboard or alert; pastes Pine code to fix or convert from v4/v5; quotes a Pine compile or runtime error; or asks why an indicator repaints or looks different live. Also covers the visual and alert side of strategy() scripts, but not order logic or backtest evaluation.
---

# Pine Script v6 indicators

The user wants a TradingView indicator that works the first time they paste it. Give them clean v6 code, a short note on how to use it, and an honest statement of whether it was compiled. Keep explanations short: most users are traders, not programmers.

## What users ask for, and what to give back

| They ask | Give back |
|---|---|
| "Make me an indicator that…" | The complete script, plus 3–5 lines covering what it shows, how to add it, and what the main inputs do. |
| "Fix this error" (pasted error or code) | The corrected script, and one or two sentences on what was wrong. |
| "Convert my v4/v5 script to v6" | The ported script and a short list of what changed. Behaviour stays the same unless a v6 rule forces a change; say so if one does. |
| "Add alerts / a table / a higher timeframe / colours" | The updated script, changing only what was asked. |
| "Why does it repaint / look different live?" | A plain-language reason and a fixed version (`references/correctness.md#repainting`). |

Build clear requests straight away. Pick sensible defaults and mention them in one line. Ask a question only when the answer changes the result, such as an unspecified overlay-or-pane choice for something that could go either way.

## Writing the script

Before writing, skim `references/pine-v6-gotchas.md`: these are the v6 rules models most often break. Open the other references only when the job needs them:
- `references/visuals-cookbook.md` for lines, boxes, labels, tables and colours.
- `references/correctness.md` for other timeframes (`request.security()`), signals, alerts and repainting.
- `references/limits-and-performance.md` when the script loops, uses many drawings, or is slow.

Defaults:
- Start with `//@version=6`. For conversions, use the gotchas list rather than just bumping the version number.
- Make lengths and colours inputs, each with a clear title. Group inputs with `group =` when there are more than a few.
- Put bands, averages and levels on the price chart (`overlay = true`). Put oscillators in their own pane.
- Use built-in `ta.*` functions, not hand-written loops.
- Add an alert for each clear signal. Fire signals on closed bars (`barstate.isconfirmed`) so they don't flicker or vanish.
- Create tables and single live lines once with `var`, then update them.
- Save the script to a `.pine` file unless the user prefers another extension. On later changes, edit that file rather than re-pasting everything.
- If the user's own existing code has a style, keep to it.

```pine
//@version=6
indicator("SMA cross", overlay = true)

int   lengthInput = input.int(20, "Length", minval = 1)
color lineColor   = input.color(color.orange, "Line colour")

float sma    = ta.sma(close, lengthInput)
bool  crossUp = ta.crossover(close, sma) and barstate.isconfirmed

plot(sma, "SMA", color = lineColor, linewidth = 2)
plotshape(crossUp, "Cross up", style = shape.triangleup, location = location.belowbar, color = color.teal, size = size.small)
alertcondition(crossUp, "Close above SMA", "{{ticker}} closed above the SMA")
```

## Before handing it over

Run through these quickly. Together they catch most first-paste failures:
- No `na` on a `bool`, and no number used as a bool without `bool(...)`.
- Stateful `ta.*` calls (crossover, rsi, highest, …) sit in the global scope, never only inside an `if`, a ternary, or the right side of `and`/`or`.
- No `transp =`. Use `color.new(color, transparency)`.
- No `x == na`; use `na(x)`.
- `request.security()` for another timeframe uses the no-repaint form (`references/correctness.md#repainting`).
- Every `switch` or `if` that returns a style has a `default` or `else`.

## Compiling

- **TradingView MCP connected:** put the script on the user's chart, compile it, and fix errors until it compiles cleanly. Take a screenshot to confirm it draws what was asked. Follow `references/tradingview-mcp.md`, and read its safety notes before saving: a careless save can overwrite another script.
- **No MCP:** you can't compile. Say so plainly, then tell the user: "Paste it into the Pine Editor (bottom of the chart), click *Add to chart*, and send me any red error text." When they send an error, fix it and say briefly what changed.

Never say a script compiles or works unless you saw it compile.

## Hand-over format

Keep it short:

> **What it does:** one or two lines.
> **Add it:** Pine Editor → paste → *Add to chart*. *(Skip this line if you added it via the MCP.)*
> **Settings:** the inputs that matter, one line each.
> **Status:** "Compiled cleanly on your chart" / "Not compiled here: paste it in and send me any error".

## When more checking is worth it

Some situations call for more than a clean compile. Offer the extra checks in `references/correctness.md` (repainting check, checking values against an independent calculation, testing on a second symbol and timeframe) when:
- the user asks to verify it or asks "is this right?";
- signals or alerts will drive real trades;
- the maths is non-trivial (custom formulas, multi-timeframe logic, statistics).

Don't run the extra checks on a simple plot or visual unless the user asks. For speed problems, see `references/limits-and-performance.md`.
