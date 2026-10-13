"""Compile every examples/**/*.pine through TradingView's guest compile service.

Opt-in, not run in CI: it sends the example sources to TradingView over the network,
through an undocumented endpoint (the same one the tradingview-mcp `pine_check` tool
uses). Only the example scripts in this repo are sent.

Fails closed:
  - a reply without a compile result is UNKNOWN, which counts as a FAIL, not a pass;
  - every file under examples/broken/ must FAIL to compile (canary). If a canary
    passes, the check is not checking anything and the whole run fails;
  - finding 0 examples or 0 canaries is a FAIL.

Usage: python scripts/compile_examples.py [--yes]
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = ("https://pine-facade.tradingview.com/pine-facade/translate_light"
       "?user_name=Guest&pine_id=00000000-0000-0000-0000-000000000000")


def compile_source(source: str) -> tuple[str, list[str], list[str]]:
    """Return (status, errors, warnings); status is 'ok', 'error' or 'unknown'."""
    body = urllib.parse.urlencode({"source": source}).encode()
    req = urllib.request.Request(URL, data=body, method="POST", headers={
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.tradingview.com/",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as e:  # network, HTTP or JSON failure
        return "unknown", [f"request failed: {e}"], []
    inner = payload.get("result") if isinstance(payload, dict) else None
    if isinstance(payload, dict) and isinstance(payload.get("error"), str) and payload["error"]:
        return "error", [payload["error"]], []
    if not isinstance(inner, dict):
        return "unknown", [f"no compile result in reply: {str(payload)[:200]}"], []
    fmt = lambda d: f"L{d.get('start', {}).get('line')}: {d.get('message')}"
    errors = [fmt(e) for e in inner.get("errors2") or []]
    warnings = [fmt(w) for w in inner.get("warnings2") or []]
    return ("error" if errors else "ok"), errors, warnings


def main() -> int:
    examples = sorted((ROOT / "examples").rglob("*.pine"))
    canaries = [p for p in examples if "broken" in p.relative_to(ROOT).parts]
    good = [p for p in examples if p not in canaries]
    if not good or not canaries:
        print(f"FAIL: found {len(good)} examples and {len(canaries)} canaries; need at least 1 of each")
        return 1
    if "--yes" not in sys.argv:
        print(f"This sends {len(examples)} example scripts to TradingView's compile service. Re-run with --yes.")
        return 2

    failures = 0
    for path in canaries + good:  # canaries first: no point checking examples if the check is blind
        rel = path.relative_to(ROOT).as_posix()
        status, errors, warnings = compile_source(path.read_text(encoding="utf-8"))
        expect_fail = path in canaries
        passed = (status == "error") if expect_fail else (status == "ok")
        tag = "PASS" if passed else "FAIL"
        print(f"{tag}  {rel}  status={status} errors={len(errors)} warnings={len(warnings)}")
        for line in errors + [f"warning {w}" for w in warnings]:
            print(f"        {line}")
        if not passed:
            failures += 1
            if expect_fail:
                print("FAIL: canary compiled cleanly, so the compile check is not trustworthy; stopping.")
                return 1
        time.sleep(1.0)  # be gentle with an undocumented endpoint

    print(f"{len(good) + len(canaries) - failures} of {len(good) + len(canaries)} files behaved as expected "
          f"({len(good)} examples must compile, {len(canaries)} canaries must fail)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
