# Pine v6 skill for Claude

Teaches Claude to write TradingView indicators in Pine Script v6 that work the first time you paste them.

AI-written Pine often fails because models still write old v5 code, which v6 rejects. This skill gives Claude the v6 rules it tends to break, good defaults, and a habit of telling you honestly whether the script was compiled.

## What you can ask

- "Make me an indicator that colours the background when RSI is above 70."
- "Fix this error:" followed by the red error text and your code.
- "Convert my v5 script to v6."
- "Add alerts and a small table showing the daily trend."
- "Why does my indicator look different live than on history?"

You get back the script, a few lines on how to add it and what the settings do, and a status line: *compiled on your chart* or *not compiled here, so paste it in and send me any error*.

## Install

**Claude Code**

```
/plugin marketplace add HAIL0K/pine-v6-skill
/plugin install pine-v6@pine-v6-skill
```

Or copy the folder `skills/pine-v6-indicators/` into `~/.claude/skills/`.

**claude.ai or Claude Desktop:** download `pine-v6-indicators.zip` from the [Releases](../../releases) page, or build it with `python scripts/build_zip.py`. Then upload it under *Settings → Capabilities → Skills*.

There's nothing to switch on: Claude uses the skill whenever you talk about Pine or TradingView indicators.

## Optional: let Claude compile on your own chart

On its own, Claude can't run TradingView, so you paste the script in and report any error. With a TradingView MCP server, Claude can put the script on your chart, compile it, fix errors and take a screenshot by itself.

This skill is written for **[tradingview-mcp-jackson](https://github.com/LewisWJackson/tradingview-mcp-jackson)** by Lewis Jackson, which builds on the original **[tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp)** by [@tradesdontlie](https://github.com/tradesdontlie). Follow that repo's README to set it up. You need TradingView Desktop and your own TradingView subscription.

> **Heads-up:** in our use, the MCP's "new script" and "open script" commands sometimes left a *different* script open in the editor, and saving then overwrote it. The skill tells Claude to check which script is open before saving, but keep backups of scripts you care about.

## Want more than "it compiles"?

Ask Claude to *verify* the indicator. It can check for repainting, compare the indicator's numbers with an independent calculation, and test it on a second symbol and timeframe. It also offers these checks on its own when signals will drive real trades.

## Credits

- [tradesdontlie/tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp), the original TradingView Desktop MCP server (MIT).
- [LewisWJackson/tradingview-mcp-jackson](https://github.com/LewisWJackson/tradingview-mcp-jackson), the fork we use. This repo contains none of its code, and we did not modify it.
- The [TradingView Pine Script v6 documentation](https://www.tradingview.com/pine-script-docs/), which the skill's rules are checked against and link to.

Not affiliated with TradingView Inc. or Anthropic. TradingView and Pine Script are trademarks of TradingView, Inc. Indicators are tools, not trading advice.

Maintaining or improving the skill? See [CONTRIBUTING.md](CONTRIBUTING.md). MIT licensed: see [LICENSE](LICENSE).
