import re
import subprocess
import sys
from pathlib import Path
import shutil

ROOT: Path = Path(__file__).parent
MAIN = ROOT / "main" / "main.tex"
UTILITY = ROOT / "utilities" / "utility.tex"


def read_macro(file_path: Path, macro: str):
    with open(file_path, "r") as f:
        content = f.read()
    match = re.search(rf"\\newcommand{{\\{macro}}}\{{(.*?)\}}", content)
    return match.group(1) if match else "UNKNOWN"


def get_subject_code(file_path: Path, key: str):
    with open(file_path, "r") as f:
        content = f.read()
    matches = re.findall(r"\\newsubject\{(.*?)\}\{(.*?)\}\{(.*?)\}", content)
    for k, code, name in matches:
        if k == key:
            return code
    return "UNKNOWN"


def slug(text: str):
    """Strip anything that doesn't belong in a filename or -jobname."""
    return re.sub(r"[^A-Za-z0-9]", "", text)


def run_cmd(cmd: list[str], cwd: Path, label: str):
    """Run a subprocess command, print a label, and abort if it fails."""
    print(f"\n{'=' * 60}")
    print(f"  Running: {label}")
    print(f"  Command: {' '.join(str(c) for c in cmd)}")
    print(f"{'=' * 60}\n")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"\n FAILED: {label} (exit {result.returncode})")
        print(" This build produced no PDF.")
        print(f" See {cwd / f'{jobname}.log'} for the first '!' line.")
        sys.exit(result.returncode)
    return result


subject_key = read_macro(MAIN, "currentsubject")
subject_code = get_subject_code(UTILITY, subject_key).upper()
studentnumber: str = read_macro(UTILITY, "studentnumber")
assignment: str = read_macro(MAIN, "currentassignment")
assignment_part: str = read_macro(MAIN, "currentpart")

# Keep the optional part in the name too, or Part 1 and Part 2 of the same
# assignment both land on the same filename and clobber each other.
name_parts = [subject_code, f"A{slug(assignment)}"]
if slug(assignment_part):
    name_parts.append(slug(assignment_part))
name_parts.append(studentnumber)
jobname = "_".join(name_parts)

latex_cmd = [
    "lualatex",
    "-interaction=nonstopmode",
    f"-jobname={jobname}",
    MAIN.name,
]
biber_cmd = [
    "biber",
    jobname,
]

run_cmd(latex_cmd, cwd=MAIN.parent, label="LuaLaTeX — Pass 1 (generate .bcf for Biber)")
run_cmd(biber_cmd, cwd=MAIN.parent, label="Biber — resolve citations > .bbl")
run_cmd(latex_cmd, cwd=MAIN.parent, label="LuaLaTeX — Pass 2 (incorporate .bbl)")
run_cmd(
    latex_cmd, cwd=MAIN.parent, label="LuaLaTeX — Pass 3 (finalise cross-references)"
)
generated_pdf = MAIN.parent / f"{jobname}.pdf"
output_pdf = ROOT / f"{jobname}.pdf"

if generated_pdf.exists():
    shutil.move(str(generated_pdf), output_pdf)
    print(f"\n Output: {output_pdf}")
else:
    print(f"\n Expected PDF not found: {generated_pdf}")
