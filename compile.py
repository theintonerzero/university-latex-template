import re
import subprocess
from pathlib import Path
import shutil

ROOT: Path = Path(__file__).parent
MAIN = ROOT / "main" / "main.tex"
UTILITY = ROOT / "utilities" / "utility.tex"
DELIVER = ROOT / "deliver"


def read_macro(file_path: Path, macro: str):
    with open(file_path, "r") as f:
        content = f.read()
    patterns = [rf"\\newcommand{{\\{macro}}}\{{(.*?)\}}", rf"\\{macro}\{{(.*?)\}}"]
    for pat in patterns:
        match = re.search(pat, content)
        if match:
            return match.group(1)
    return "UNKNOWN"


def get_subject_code(file_path: Path, key: str):
    with open(file_path, "r") as f:
        content = f.read()
    matches = re.findall(r"\\newsubject\{(.*?)\}\{(.*?)\}\{(.*?)\}", content)
    for k, code, name in matches:
        if k == key:
            return code
    return "UNKNOWN"


def run_cmd(cmd: list[str], cwd: Path, label: str):
    """Run a subprocess command, print a label, and return the CompletedProcess."""
    print(f"\n{'=' * 60}")
    print(f"  Running: {label}")
    print(f"  Command: {' '.join(str(c) for c in cmd)}")
    print(f"{'=' * 60}\n")
    return subprocess.run(cmd, cwd=cwd)


subject_key = read_macro(MAIN, "currentsubject")
subject_code = get_subject_code(UTILITY, subject_key).upper()
studentnumber: str = read_macro(UTILITY, "studentnumber")
currentsubject: str = read_macro(MAIN, "currentsubject").upper()
assignment: str = read_macro(MAIN, "assignmentname")
jobname = f"{subject_code}_A{assignment}_{studentnumber}"

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
