"""Build dist/pine-v6-indicators.zip for uploading the skill to claude.ai."""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "pine-v6-indicators"
OUT = ROOT / "dist" / "pine-v6-indicators.zip"

files = sorted(p for p in SKILL.rglob("*") if p.is_file())
if not files:
    raise SystemExit(f"FAIL: no files under {SKILL}")
OUT.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for p in files:
        z.write(p, Path("pine-v6-indicators") / p.relative_to(SKILL))
print(f"wrote {OUT} ({len(files)} files)")
