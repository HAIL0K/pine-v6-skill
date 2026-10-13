"""Structure lint for the pine-v6-indicators skill. Runs in CI; needs only the stdlib and git.

Fails closed: finding no skill, no references, no files to scan, or no Pine code where
Pine code is expected is a FAIL, not a pass.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "pine-v6-indicators"

# Strings that must never ship: local home paths and tool names that exist in only one
# client. Personal names are NOT listed here, because listing them would publish them.
# Put one regex per line in an untracked .local-denylist, or in PINE_SKILL_DENYLIST
# (separated by ";").
FORBIDDEN = [r"[A-Za-z]:\\Users\\", r"/Users/[a-z]", r"/home/[a-z]", r"\bcreate_file\b", r"\bstr_replace\b"]

# Pine v5-and-older syntax that is a compile error or a silent bug in v6.
V5_ISMS = {
    r"\btransp\s*=": "transp= was removed in v6; use color.new()",
    r"(?<![\w.])study\s*\(": "study() is v4; use indicator()",
    r"(?<![\w.])security\s*\(": "bare security() is v4; use request.security()",
    r"//@version=[1-5]\b": "script declares a pre-v6 version",
    r"\bwhen\s*=": "when= was removed from strategy.*() in v6",
}

# Files that must contain at least one ```pine block, so the v5-syntax scan cannot pass
# by matching nothing.
MUST_HAVE_PINE = [
    "skills/pine-v6-indicators/SKILL.md",
    "skills/pine-v6-indicators/references/correctness.md",
    "skills/pine-v6-indicators/references/visuals-cookbook.md",
]
MANIFESTS = [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"]
SELF = "scripts/check_skill.py"  # holds the patterns themselves
BINARY_SUFFIXES = {".zip", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf"}

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def local_denylist() -> list[str]:
    pats = []
    f = ROOT / ".local-denylist"
    if f.is_file():
        pats += [l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    pats += [p for p in os.environ.get("PINE_SKILL_DENYLIST", "").split(";") if p]
    return pats


def shipped_files() -> list[Path]:
    """Files git tracks, plus new files it would pick up (untracked and not ignored)."""
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        fail(f"git ls-files failed: {e}")
        return []
    return [ROOT / l for l in out.splitlines() if l and (ROOT / l).is_file()]


def check_skill_md() -> None:
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.is_file():
        fail(f"{skill_md.relative_to(ROOT)} not found")
        return
    text = skill_md.read_text(encoding="utf-8")
    fm = frontmatter(text)
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != SKILL_DIR.name:
        fail(f"frontmatter name {name!r} != folder {SKILL_DIR.name!r}")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        fail("name must be lowercase letters, digits and hyphens, at most 64 chars")
    if not 1 <= len(desc) <= 1024:
        fail(f"description length {len(desc)} outside 1..1024")
    if re.search(r"<[^>]+>", desc):
        fail("description must not contain XML tags")
    if text.count("\n") > 500:
        fail("SKILL.md is over 500 lines; move detail to references/")

    refs = sorted((SKILL_DIR / "references").glob("*.md"))
    if not refs:
        fail("no reference files found")
    linked = set(re.findall(r"references/([\w.-]+\.md)", text))
    for ref in refs:
        if ref.name not in linked:
            fail(f"references/{ref.name} is never mentioned in SKILL.md (orphan)")
    for n in linked:
        if not (SKILL_DIR / "references" / n).is_file():
            fail(f"SKILL.md mentions references/{n}, which does not exist")


def main() -> int:
    check_skill_md()

    forbidden = FORBIDDEN + local_denylist()
    scanned = pine_blocks = 0
    for path in shipped_files():
        rel = path.relative_to(ROOT).as_posix()
        if rel == ".local-denylist":
            fail(".local-denylist is not git-ignored; it would publish the names in it")
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        # Never skip text that fails to decode: a cp1252 file can still leak a path.
        content = path.read_text(encoding="utf-8", errors="replace")
        scanned += 1
        if rel != SELF:
            for pat in forbidden:
                if re.search(pat, content, re.I):
                    fail(f"{rel}: forbidden string matching {pat}")

        if rel.endswith(".pine"):
            if rel.startswith("examples/broken/"):
                continue  # deliberately broken canary for compile_examples.py
            if not content.startswith("//@version=6"):
                fail(f"{rel}: first line must be //@version=6")
            blocks = [content]
        elif rel.endswith(".md"):
            blocks = re.findall(r"```pine\n(.*?)```", content, re.S)
            if rel in MUST_HAVE_PINE and not blocks:
                fail(f"{rel}: expected Pine code blocks, found 0 (did the fence format change?)")
        else:
            blocks = []
        for block in blocks:
            pine_blocks += 1
            for line in block.splitlines():
                code = line if line.lstrip().startswith("//@") else line.split("//", 1)[0]
                for pat, why in V5_ISMS.items():
                    if re.search(pat, code):
                        fail(f"{rel}: {why}: {line.strip()}")

    for rel in MANIFESTS:
        manifest = ROOT / rel
        if not manifest.is_file():
            fail(f"{rel} is missing")
            continue
        try:
            json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail(f"{rel}: invalid JSON: {e}")

    if scanned == 0:
        fail("scanned 0 files")
    if pine_blocks == 0:
        fail("found 0 Pine code blocks; the v5-syntax scan checked nothing")

    print(f"scanned {scanned} files, {pine_blocks} Pine blocks")
    for e in errors:
        print("FAIL:", e)
    print("FAIL" if errors else "PASS")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
