# Compile and verify through a TradingView MCP server

This file applies when a TradingView Desktop MCP server is connected. The one this was written against is [tradingview-mcp-jackson](https://github.com/LewisWJackson/tradingview-mcp-jackson) by Lewis Jackson, a fork of [tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp) by @tradesdontlie. It drives a locally running TradingView Desktop through the Chrome DevTools Protocol. Tool names below are the server's own. In Claude Code they appear prefixed with the name you gave the server in your MCP config: a server named `tradingview` gives `mcp__tradingview__pine_smart_compile`.

When no such server is connected, run the loop by hand: the user pastes the compiler output, the runtime errors and the Pine Logs. Never claim a step the tools did not show you.

## Before touching the editor (hazards, observed 2026-09 to 2026-10)

These cost real saved scripts. Check them every time.

1. **`pine_new` may not open a new script.** It can report `new_script_created` while the editor still holds the previously open script. A following `pine_set_source` plus save then **overwrites that saved script**. Before any `pine_set_source`, confirm the editor's title is the script you intend to overwrite, or a fresh untitled one: take a screenshot, or read the title from the DOM.
2. **`pine_open(name)` may paste rather than open.** It can paste the named script's source into whatever script is open, so a save then overwrites the wrong one. To switch scripts reliably, use the editor's Open dialog (Ctrl+O), check the header name, and only then save.
3. **The server stays attached to the tab it first connected to.** `tab_switch` does not move it. To work on another layout, navigate that tab to it.
4. **`indicator_set_inputs` can break a freshly added study** ("Can't parse pine"). Change inputs in the indicator's settings dialog, or remove and re-add the study.
5. **After saving a script with new inputs, remove and re-add its chart instance.** The old instance can keep the stale input set, and `input.source` bindings may reset to `close` seconds after a save.
6. **`data_get_study_values` reads the bar under the crosshair**, not necessarily the last bar. Move the crosshair, or read tables and labels written on `barstate.islast`.

If you are unsure what the editor holds, stop and ask the user. That beats overwriting their work.

## The loop with tools

| Loop step | Tools | Pass when |
|---|---|---|
| Compile | `pine_set_source`, then `pine_smart_compile`; `pine_get_errors` | 0 errors; every warning fixed or justified |
| Runtime | `chart_get_state` for the study's entity and status; `pine_get_console` for Pine Logs; `chart_set_symbol` and `chart_set_timeframe` for 2 symbols × 2 timeframes | no runtime error shown on the study; no `log.error` lines |
| Values | `data_get_ohlcv` for the bars to recompute from; `data_get_study_values` and `data_get_pine_tables` / `data_get_pine_labels` (pass `study_filter`) for the script's numbers; `pine_get_console` for `log.info` spot prints | N of N spot bars match within tolerance |
| Repainting | `replay_start`, `replay_step`, `replay_stop` | confirmed signals and higher-timeframe values do not change as replay advances |
| Visual | `capture_screenshot` (region `chart`) | matches the spec |
| Save | `pine_save`, then `pine_list_scripts` to confirm the name | the saved name is the one intended |

Read the source back with `pine_get_source` only when you must. It can return a very large payload.

## Compiling without the chart: `pine_check`

`pine_check` sends the source to TradingView's compile service as a guest, without using the chart. It is useful as a quick syntax gate, but note the caveats:

- **It checks compilation only.** It gives no runtime errors, no values and no repainting signal, so steps 5 to 7 of the loop still need the chart or the user.
- **The source leaves your machine** and goes to TradingView. Do not send proprietary logic without the user's consent.
- **It can report a false pass.** In the version read on 2026-10-13 (`src/core/pine.js`, around line 233), a reply with no compile result counts as `compiled: true` with zero errors. Before trusting a run of passes, run a script with a known error through it and confirm it fails. Treat "compiled" with no diagnostics on an unexpected reply as *unknown*, not a pass.
- It uses an undocumented endpoint, which can change or be rate-limited without notice.

## Debugging recipes

- **Find the failing line:** read `pine_get_errors`, fix only that line, and recompile. Do not rewrite unrelated code while fixing an error.
- **Check a runtime value:** add `log.info("…{0}", x)` behind `debugMode`, recompile, read `pine_get_console`, then remove the line or leave it gated.
- **Read drawn levels:** use `data_get_pine_lines`, `data_get_pine_labels`, `data_get_pine_boxes` or `data_get_pine_tables`, with `study_filter` set to the script's title. The indicator must be visible on the chart.
