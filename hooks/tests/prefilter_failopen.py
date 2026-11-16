#!/usr/bin/env python3
"""A missing or broken harness_event.py must never change the hook's normal behavior (2026-11-16).
Copies the UserPromptSubmit hook to a temp dir, then runs it with the shared module
absent, with a syntax error, and with a module that raises. The hook must still exit 0 and still
fire on its trigger."""
import json, os, shutil, subprocess, sys, tempfile
HOOKS = os.environ.get("HOOKS_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FILES = {"prompt-optimizer-nudge.sh": ("sh", "Draft a cover letter to the journal editor explaining why this paper belongs")}
MODES = {"missing": None, "syntax error": "def (:\n",
         "raises on import": "raise RuntimeError('boom')\n",
         "raises on call": "import sys\ndef is_harness_event(p):\n    raise RuntimeError('boom')\nif __name__ == '__main__':\n    raise SystemExit(7)\n"}
bad = n = 0
for mode, body in MODES.items():
    d = tempfile.mkdtemp(prefix="prefilter_failopen_")
    for f in FILES:
        shutil.copy(os.path.join(HOOKS, f), d)
    if body is not None:
        open(os.path.join(d, "harness_event.py"), "w").write(body)
    for f, (interp, prompt) in FILES.items():
        o = subprocess.run([interp, os.path.join(d, f)], input=json.dumps({"prompt": prompt}),
                           capture_output=True, text=True)
        ok = o.returncode == 0 and o.stdout.strip() != ""
        n += 1; bad += (not ok)
        print("  %s %s with harness_event.py %s" % ("ok  " if ok else "FAIL", f, mode),
              "" if ok else "-- rc=%s out=%r err=%r" % (o.returncode, o.stdout[:40], o.stderr[-120:]))
    shutil.rmtree(d, ignore_errors=True)
print("%d checks, FAILURES: %d" % (n, bad))
sys.exit(1 if bad else 0)
