# How to use

## Requirements
- LuaLaTeX
- Biber
- Python 3.9 or newer

## Setup
Put your name and student number in `utilities/utility.tex`:
```latex
\newcommand{\studentname}{Your Name}
\newcommand{\studentnumber}{12345678}
```

Register each subject once in the same file, as a key, a code, and a title:
```latex
\newsubject{cse3vis}{CSE3VIS}{Computer Vision}
```

Then pick the subject and name the assignment in `main/main.tex`:
```latex
\newcommand{\currentsubject}{cse3vis}
\assignmentname{1}[Part 1]
```
The `[Part 1]` is optional. An unknown subject key stops the build instead of
printing a blank title page.

## Compiling
To compile and get a `.pdf` run:
```
python3 compile.py
```
This runs LuaLaTeX, then Biber, then LuaLaTeX twice more to settle the
citations and cross-references. If a pass fails, the script stops there and
tells you which log to read.

The output PDF goes in the project root, named
`SUBJECTCODE_A<number>_STUDENTNUMBER.pdf`. An assignment part is included when
you set one, so the example above produces `CSE3VIS_A1_Part1_12345678.pdf`.
