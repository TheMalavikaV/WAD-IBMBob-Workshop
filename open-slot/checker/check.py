#!/usr/bin/env python3
"""The Open Slot checker. No dependencies; Windows, macOS, Linux.

Run every example with your command (from the open-slot folder):
    python checker/check.py --cmd "node open_slot.js"
    python checker/check.py --cmd "python open_slot.py" --level 1
    python checker/check.py --cmd "java Main.java" --only L2-02-freed-patient-takes-waiting-slot

Your command is called as:   <your command> "<waitlist.json>" "<script.txt>"
and must print one JSON object per line (JSON Lines) to stdout.

Compare two files you produced yourself:
    python checker/check.py --compare examples/L1-01-first-accepts/expected.jsonl my_output.jsonl

Rules of comparison: same number of events, in the same order; every key in an expected event must be present
with the same value (extra keys are allowed); whitespace and key order do not matter; blank lines are ignored.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXAMPLES = os.path.join(ROOT, "examples")


def parse_jsonl(text, label):
    events = []
    for no, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            return None, f"{label} line {no} is not valid JSON: {line[:120]!r}"
    return events, None


def diff(expected, actual):
    for i, (e, a) in enumerate(zip(expected, actual), start=1):
        if not isinstance(a, dict):
            return f"event {i}: expected an object, got {json.dumps(a)}"
        for key, value in e.items():
            if a.get(key) != value:
                return f"event {i}: expected {json.dumps(e)}\n      got           {json.dumps(a)}"
    if len(expected) != len(actual):
        which = expected[len(actual)] if len(expected) > len(actual) else actual[len(expected)]
        return (f"expected {len(expected)} events, got {len(actual)}; first "
                f"{'missing' if len(expected) > len(actual) else 'extra'} event: {json.dumps(which)}")
    return None


def run_example(cmd, name):
    folder = os.path.join(EXAMPLES, name)
    waitlist = os.path.relpath(os.path.join(folder, "waitlist.json"), ROOT)
    script = os.path.relpath(os.path.join(folder, "script.txt"), ROOT)
    full = f'{cmd} "{waitlist}" "{script}"'
    try:
        proc = subprocess.run(full, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return f"timed out after 60 s: {full}"
    if proc.returncode != 0:
        return f"exit code {proc.returncode} from: {full}\n      stderr: {proc.stderr.strip()[:500]}"
    actual, err = parse_jsonl(proc.stdout, "your output")
    if err:
        return err
    with open(os.path.join(folder, "expected.jsonl"), encoding="utf-8") as fh:
        expected, _ = parse_jsonl(fh.read(), "expected")
    return diff(expected, actual)


def main():
    ap = argparse.ArgumentParser(description="Check your Open Slot solution against the examples.")
    ap.add_argument("--cmd", help='command that runs your program, e.g. "node open_slot.js"')
    ap.add_argument("--level", type=int, choices=[1, 2, 3], help="only run examples of this level")
    ap.add_argument("--only", help="only run this example folder")
    ap.add_argument("--compare", nargs=2, metavar=("EXPECTED", "ACTUAL"), help="compare two JSONL files")
    args = ap.parse_args()

    if args.compare:
        texts = []
        for path in args.compare:
            with open(path, encoding="utf-8") as fh:
                texts.append(fh.read())
        expected, err1 = parse_jsonl(texts[0], args.compare[0])
        actual, err2 = parse_jsonl(texts[1], args.compare[1])
        problem = err1 or err2 or diff(expected, actual)
        print("PASS" if not problem else f"FAIL  {problem}")
        return 0 if not problem else 1

    if not args.cmd:
        ap.print_help()
        return 2
    names = sorted(n for n in os.listdir(EXAMPLES) if os.path.isdir(os.path.join(EXAMPLES, n)))
    if args.level:
        names = [n for n in names if n.startswith(f"L{args.level}-")]
    if args.only:
        names = [n for n in names if n == args.only]
    failed = 0
    for name in names:
        problem = run_example(args.cmd, name)
        print(f"{'PASS' if not problem else 'FAIL'}  {name}" + (f"\n      {problem}" if problem else ""))
        failed += bool(problem)
    print(f"\n{len(names) - failed}/{len(names)} examples passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
