#!/usr/bin/env python3
"""Flaky Test Detective checker. No dependencies; Windows, macOS, Linux.

Run every example with your command (from the flaky-test-detective folder):
    python checker/check.py --cmd "node detective.js"
    python checker/check.py --cmd "python detective.py" --level 1
    python checker/check.py --cmd "java Main.java" --only L1-02-regression

Your command gets the CSV path as its last argument (Level 2 examples also get --retries
before the path) and must print the JSON report to stdout.

Compare two files you produced yourself:
    python checker/check.py --compare examples/L1-01-basic/expected.json my_output.json

Rules of comparison: every key in the expected file must be present with the same value
(extra keys in your output are allowed), lists must have the same items in the same order,
numbers may differ by at most 0.0001.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXAMPLES = os.path.join(ROOT, "examples")
TOLERANCE = 0.0001 + 1e-9


def diff(expected, actual, path="$"):
    """Return a description of the first difference, or None."""
    if isinstance(expected, bool) or isinstance(actual, bool):
        return None if expected is actual else f"{path}: expected {json.dumps(expected)}, got {json.dumps(actual)}"
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return None if abs(expected - actual) <= TOLERANCE else f"{path}: expected {expected}, got {actual}"
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return f"{path}: expected an object, got {type(actual).__name__}"
        for key, value in expected.items():
            if key not in actual:
                return f"{path}: missing key \"{key}\""
            d = diff(value, actual[key], f"{path}.{key}")
            if d:
                return d
        return None
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return f"{path}: expected a list, got {type(actual).__name__}"
        for i, (e, a) in enumerate(zip(expected, actual)):
            d = diff(e, a, f"{path}[{i}]")
            if d:
                return d
        if len(expected) != len(actual):
            return f"{path}: expected {len(expected)} items, got {len(actual)}"
        return None
    return None if expected == actual else f"{path}: expected {json.dumps(expected)}, got {json.dumps(actual)}"


def load_json_text(text, label):
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, f"{label} is not valid JSON ({exc}). First 200 chars: {text[:200]!r}"


def run_example(cmd, name):
    folder = os.path.join(EXAMPLES, name)
    csv_path = os.path.relpath(os.path.join(folder, "runs.csv"), ROOT)
    flag = " --retries" if name.startswith("L2") else ""
    full = f'{cmd}{flag} "{csv_path}"'
    try:
        proc = subprocess.run(full, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return f"timed out after 120 s: {full}"
    if proc.returncode != 0:
        return f"exit code {proc.returncode} from: {full}\n      stderr: {proc.stderr.strip()[:500]}"
    actual, err = load_json_text(proc.stdout, "your output")
    if err:
        return err
    with open(os.path.join(folder, "expected.json"), encoding="utf-8") as fh:
        expected = json.load(fh)
    return diff(expected, actual)


def main():
    ap = argparse.ArgumentParser(description="Check your Flaky Test Detective against the examples.")
    ap.add_argument("--cmd", help='command that runs your tool, e.g. "node detective.js"')
    ap.add_argument("--level", type=int, choices=[1, 2], help="only run examples of this level")
    ap.add_argument("--only", help="only run this example folder")
    ap.add_argument("--compare", nargs=2, metavar=("EXPECTED", "ACTUAL"), help="compare two JSON files")
    args = ap.parse_args()

    if args.compare:
        with open(args.compare[0], encoding="utf-8") as fh:
            expected = json.load(fh)
        with open(args.compare[1], encoding="utf-8") as fh:
            actual, err = load_json_text(fh.read(), args.compare[1])
        problem = err or diff(expected, actual)
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
