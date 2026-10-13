# Draft issue for tradingview-mcp(-jackson): `pine_check` reports a pass when the compile reply has no result

*Not filed. A draft for the repo owner to send if they choose.*

## What we see

`check()` in `src/core/pine.js` (lines 186-243 at commit `01c193a` of LewisWJackson/tradingview-mcp-jackson) sets `compiled = errors.length === 0`. Errors are collected only from `result.errors2` or from a string `error`. If TradingView's reply has neither (an empty object, a changed schema, or a rate-limit page parsed as JSON), the tool returns `compiled: true` with the note "Pine Script compiled successfully."

## Why it matters

Agents use `pine_check` as a compile gate. A malformed or changed reply turns every script into a pass, and nothing signals it.

## Ask

When `result` is missing or is not an object, return `success: false` (or `compiled: null`) with the raw reply attached, and add a test that feeds `{}` into the parser and expects a non-pass. We have not checked whether upstream `tradesdontlie/tradingview-mcp` has the same code.
