# Pine Script v6: compiler traps

Each rule below is either *documented* (it links to the docs page it comes from) or *observed* (it was seen in real compiles but is not in the docs, and is marked as such). The documented rules were checked against the docs on 2026-10-13. When a rule here disagrees with the live docs, the docs win; open an issue.

Main source: [Migration guide to v6](https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/).

## Contents
- Types and `na`
- The history operator `[]`
- Numbers and qualifiers
- Evaluation order
- Plots, colours and parameters
- Requests
- Strategy items that leak into indicator code
- Observed traps (not in the docs)

## Types and `na`

- **A `bool` can never be `na`.** It is strictly `true` or `false`. `na()`, `nz()` and `fixnan()` no longer accept bools. If you need a third state, use an `int` (`-1/0/1`). *Documented.*
- **There is no implicit int/float-to-bool cast.** `bar_index ? a : b` is an error; write `bool(bar_index) ? a : b`. *Documented.*
- **Parameters of "unique" types never accept `na`.** This covers plot styles, line styles, label styles and similar. A `switch` that produces one needs a `default =>` arm, and an `if` needs an `else`. *Documented.*
- **Never compare with `na`.** `x == na` and `x != na` are never true, so they cannot test for `na`. Use `na(x)`. To detect a change that includes the first value, write `na(prev) or x != prev`. *Documented:* [na](https://www.tradingview.com/pine-script-reference/v6/#var_na).
- **A bare `na` passed to an untyped function parameter cannot be type-inferred.** Cast it (`float(na)`, `int(na)`) or give the parameter a type. *Observed* as CE10189.

## The history operator `[]`

- **No `[]` on literals or built-in constants.** `6[1]`, `true[10]` and `color.red[3]` are all errors. *Documented.*
- **No `[]` directly on a UDT field.** Reference the object's history first, in parentheses: `(myObj[10]).field`. *Documented.*
- **`[a, b]` is not an array literal.** Square brackets build tuples, which are valid only for function returns, tuple destructuring (`[m, s] = f()`), and `request.*()` expressions. They also appear inline in `options = [...]` of `input.*()`. Assigning one to a plain variable (`x = ["a", "b"]`) is an error, so build arrays with `array.from()` or `array.new<T>()`. *Observed* as CE10156.
- **The history buffer is limited.** It is 5,000 bars for most series and 10,000 for `open`, `high`, `low`, `close` and `time`. A deeper reference fails at runtime with RE10143. Raise the buffer with `max_bars_back`. *Documented:* [limitations](https://www.tradingview.com/pine-script-docs/writing/limitations/).

## Numbers and qualifiers

- **Dividing two `const int`s can return a fraction** in v6: `5 / 2 == 2.5`. Wrap the result in `int()`, `math.floor()` or `math.round()` to get an integer. *Documented.*
- **Mutable variables are "series".** Passing one where "simple" is required (the `length` of `ta.ema()`, for example) is an error. Use an input or a `const`. *Documented.*
- **Arrays accept negative indices** in `get`, `set`, `insert` and `remove`: `-1` is the last element. *Documented.*

## Evaluation order

- **`and` and `or` are lazy.** The right operand is skipped once the result is known. A stateful call such as `ta.rsi()` or `ta.crossover()` on the right side then misses bars and drifts. Compute every stateful `ta.*` value in the global scope on every bar, then combine the variables. *Documented.* The same applies inside `if` blocks and ternaries; the compiler warns with CW10003 ([errors overview](https://www.tradingview.com/pine-script-docs/errors/overview/)).
- **A `for` loop re-evaluates its end bound before every iteration.** Compute the bound once, in a variable, before the loop. *Documented.*
- **`timeframe.period` always includes the multiplier:** `"1D"`, not `"D"`. *Documented.*

## Plots, colours and parameters

- **`transp=` is gone** from `plot`, `plotshape`, `plotchar`, `plotarrow`, `bgcolor` and `fill`. Use `color.new(c, t)` instead. *Documented.* The Style tab's colour picker appears only when the colour is "const" or "input"; computed colours still compile.
- **`offset` accepts no "series" value.** Use a simple value or an input. *Documented.*
- **`linewidth` must be ≥ 1.** *Documented.*
- **Naming the same parameter twice in one call is an error.** *Documented.*
- **Some colour constants changed value.** `color.red` is `#F23645`, `color.teal` is `#089981` and `color.yellow` is `#FDD835`. `label.new()` text now defaults to white. *Documented.*

## Requests

- **Dynamic requests are on by default.** `request.*()` accepts series symbol and timeframe arguments, and the calls may sit in loops and conditionals. Set `dynamic_requests = false` in `indicator()` to restore v5 behaviour; nested-scope calls then become errors. *Documented.*
- **An array or matrix id returned by `request.security()` can be `na`** on early bars. Check `not na(id)` before calling `.size()`, `.get()` or a loop. *Observed.*
- **Plain `"EXCH:SYM"` strings request unadjusted data**, even on a dividend-adjusted chart. To inherit the chart's settings, build the ticker with `ticker.inherit()` or use `syminfo.tickerid`. *Observed* 2026-10-12.
- **An `input.source` read inside `request.security()` on a higher timeframe** returns the first intraday bar of each day, not the day's value. *Observed* 2026-10-12.

## Strategy items that leak into indicator code

- `when=` was removed from `strategy.*()` order functions; use `if`. The default margin is now 100%. *Documented.*
- `strategy.opentrades.size(n)` takes a trade index (int), not an entry id string. *Observed* as CE10123.

## Observed traps (not in the docs)

These were seen on TradingView between 2026-09 and 2026-10. Each is worth knowing, but none is guaranteed.
- A seeded `math.random(seed = …)` restarts its sequence on every call. Draw all your numbers from a single call site in a loop.
- `order` is a reserved namespace and cannot be used as an identifier.
- `barstate.islastconfirmedhistory` may never become true when a requested symbol's market is open while the chart's market is closed. Also handle `barstate.islast`.
- `array.binary_search_leftmost()` on a missing value returns the index of the element to the left of the insertion slot.
- Scripts that read `chart.left_visible_bar_time` or `chart.right_visible_bar_time` re-run on every scroll, and so does every script that takes their output as an `input.source`.
- Hidden outputs such as a plot with a non-constant colour, or an `hline` placed before the exported plots, shift the plot indices that other scripts bind to through `input.source`.
- Heavy scripts can show an empty or partial table for several seconds after a save or a timeframe change. Wait and re-read before debugging.
