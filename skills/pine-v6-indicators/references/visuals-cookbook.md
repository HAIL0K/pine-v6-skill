# Visuals cookbook

Snippets for the visual side of indicators. Each one is a fragment to drop into a `//@version=6` indicator: assume the inputs and variables it names exist. Complete scripts that use these patterns are in the repo's `examples/` folder; `examples/visuals-cookbook-smoke.pine` holds the drawing snippets in one script (not yet compiled; run `scripts/compile_examples.py`).

Sources (checked 2026-10-13): [Plots](https://www.tradingview.com/pine-script-docs/visuals/plots/), [Lines and boxes](https://www.tradingview.com/pine-script-docs/visuals/lines-and-boxes/), [Text and shapes](https://www.tradingview.com/pine-script-docs/visuals/text-and-shapes/), [Tables](https://www.tradingview.com/pine-script-docs/visuals/tables/), [Colors](https://www.tradingview.com/pine-script-docs/visuals/colors/).

## Plots and fills

```pine
plot(basis, "Basis", color = color.blue, linewidth = 2)
plot(delta, "Delta", style = plot.style_columns, color = delta >= 0 ? color.teal : color.red)

upperPlot = plot(upper, "Upper", color = color.gray)
lowerPlot = plot(lower, "Lower", color = color.gray)
fill(upperPlot, lowerPlot, color = color.new(color.gray, 90), title = "Band fill")

hline(70, "Overbought", color = color.new(color.red, 50), linestyle = hline.style_dashed)
```

- Transparency is set with `color.new(c, 0..100)`; there is no `transp=`.
- To hide a plot from the chart but keep it in the Data Window, use `display = display.data_window`. `display.none` hides it everywhere, although other scripts can still read it as an `input.source`.
- A plot whose colour is computed (as in the delta example) still compiles, but loses its colour picker in the Style tab.

## Signal markers

```pine
plotshape(longSignal,  "Long",  style = shape.triangleup,   location = location.belowbar, color = color.green, size = size.small)
plotshape(shortSignal, "Short", style = shape.triangledown, location = location.abovebar, color = color.red,   size = size.small)
plotchar(exitSignal, "Exit", char = "×", location = location.abovebar, color = color.gray)
```

`plotshape()` and `plotchar()` cost plot counts but no drawing budget. They also stay on every bar in history, whereas labels keep only the last 500. Prefer them for per-bar markers.

## Lines, boxes, labels

A single *live* object: create it once, then move it.

```pine
var line pivotLine = line.new(na, na, na, na, color = color.orange, width = 2, extend = extend.right)
if barstate.islast and not na(pivotHigh)
    line.set_xy1(pivotLine, bar_index - 20, pivotHigh)
    line.set_xy2(pivotLine, bar_index, pivotHigh)
```

One object *per event*: gate the `.new()` call itself, and raise the count limit in `indicator(..., max_labels_count = 500)` if needed.

```pine
if crossUp and barstate.isconfirmed
    label.new(bar_index, low, str.tostring(close, format.mintick), style = label.style_label_up,
         color = color.teal, textcolor = color.white)
```

A range box that grows while the session is open:

```pine
var box sessionBox = na
bool inSession = not na(time(timeframe.period, sessionInput))
if inSession and not inSession[1]
    sessionBox := box.new(bar_index, high, bar_index, low, border_color = color.blue, bgcolor = color.new(color.blue, 90))
else if inSession and not na(sessionBox)
    box.set_right(sessionBox, bar_index)
    box.set_top(sessionBox, math.max(box.get_top(sessionBox), high))
    box.set_bottom(sessionBox, math.min(box.get_bottom(sessionBox), low))
```

- Never call `.new()` on every bar for something that should be single. The oldest copies are deleted silently at the cap, and the chart slows down.
- Objects created on the realtime bar are rolled back and recreated on each tick unless the creation is gated on `barstate.isconfirmed`. That is harmless, but it costs time.

## Tables

```pine
var table dash = table.new(position.top_right, 2, 3, border_width = 1, bgcolor = color.new(color.black, 80))
if barstate.islast
    table.cell(dash, 0, 0, "Metric", text_color = color.white)
    table.cell(dash, 1, 0, "Value",  text_color = color.white)
    table.cell(dash, 0, 1, "RSI",    text_color = color.white)
    table.cell(dash, 1, 1, str.tostring(rsiValue, "#.##"), text_color = color.white)
    table.cell(dash, 0, 2, "ATR",    text_color = color.white)
    table.cell(dash, 1, 2, str.tostring(atrValue, format.mintick), text_color = color.white)
```

- Create the table once with `var`, and fill it only on `barstate.islast`.
- There is one table per `position.*`. For more sections, add rows and columns to a single table.
- Table cells and strings count toward the script's memory limit (RE10139) far more than floats do. Keep large dashboards lean.

## Background and bar colour

```pine
bgcolor(regime == 1 ? color.new(color.green, 90) : regime == -1 ? color.new(color.red, 90) : na, title = "Regime")
barcolor(close > open ? color.lime : color.maroon, title = "Bar colour")
```

## Colour choices

- Pair the colours with something else that marks the state: a shape, text or position. Colour should not be the only cue, since red/green colour blindness is common.
- Keep transparency between 80 and 95 for backgrounds and fills, so the price stays readable.
- Make colours inputs, so users can match their own chart themes.
