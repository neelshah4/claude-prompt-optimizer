"""Fixtures for the prompt-optimizer Stop hook on long transcripts.
Run from the repository root:  python3 hooks/tests/stop_hook_tail_fixtures.py
Set HOOKS_DIR to test a different copy of the hooks.

The Stop hook used to keep only the last 4,000,000 bytes of the transcript. When the turn's
opening human prompt lay before that window the hook saw no prompt and allowed the stop
unchecked. It now widens the window (bounded at 64 MB, then fails open) until the prompt is found.
"""
import json, os, shutil, subprocess, sys, tempfile, time

HOOKS = os.environ.get("HOOKS_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PO = os.path.join(HOOKS, "prompt-optimizer-stop-check.sh")
TMP = tempfile.mkdtemp(prefix="stop_tail_")
bad = 0
n = 0


def check(name, ok, detail=""):
    global bad, n
    n += 1
    if ok:
        print("  ok   " + name)
    else:
        bad += 1
        print("  FAIL " + name + (" -- " + detail if detail else ""))


def U(text, **kw):
    d = {"type": "user", "message": {"content": text}}
    d.update(kw)
    return d


def A(text="", tools=()):
    blocks = [{"type": "text", "text": text}] if text else []
    for nm, inp in tools:
        blocks.append({"type": "tool_use", "name": nm, "input": inp})
    return {"type": "assistant", "message": {"content": blocks}}


def write_t(entries, name, filler_bytes=0, filler_after_idx=0):
    """Write a transcript. filler_bytes of inert assistant text lines are inserted after entry
    filler_after_idx (so the entries before it end up outside the 4 MB tail window)."""
    path = os.path.join(TMP, name + ".jsonl")
    with open(path, "w") as fh:
        for i, e in enumerate(entries):
            fh.write(json.dumps(e) + "\n")
            if i == filler_after_idx and filler_bytes:
                chunk = json.dumps(A("lorem ipsum dolor sit amet " * 4000)) + "\n"  # ~108 KB
                wrote = 0
                while wrote < filler_bytes:
                    fh.write(chunk)
                    wrote += len(chunk)
    return path


def stop(hook, path, last="", env=None, extra=None):
    d = {"stop_hook_active": False, "permission_mode": "default", "transcript_path": path,
         "session_id": "t", "last_assistant_message": last}
    if extra:
        d.update(extra)
    e2 = dict(os.environ)
    for k in ("CLAUDE_PO_STOP_DISABLE", "CLAUDE_ANTIAI_STOP_DISABLE", "CLAUDE_ANTIAI_REVIEW_DISABLE"):
        e2.pop(k, None)
    if env:
        e2.update(env)
    t0 = time.time()
    o = subprocess.run(["sh", hook], input=json.dumps(d), capture_output=True, text=True, env=e2)
    blocked, reason = False, ""
    if o.stdout.strip():
        try:
            j = json.loads(o.stdout)
            blocked = j.get("decision") == "block"
            reason = j.get("reason", "")
        except Exception:
            pass
    return o.returncode, blocked, reason, time.time() - t0


LONG_PROMPT = ("Please look at the cohort extract and tell me which of the three sensitivity analyses we should "
               "run first, given that the data request is already submitted and the reviewers asked about "
               "calibration in the neonatal subgroup before anything else is done on the dataset today.")
assert len(LONG_PROMPT.split()) >= 25

# ---------------------------------------------------------------- B3
print("B3 prompt-optimizer-stop-check: opening prompt before the 4 MB window")
small = write_t([U(LONG_PROMPT), A("Here is my answer with no block at all.")], "po_small")
rc, blocked, why, _ = stop(PO, small)
check("small transcript: 25+ word human prompt, no block -> blocks (control)", rc == 0 and blocked, why)

big = write_t([U(LONG_PROMPT), A("start"), A("Here is my answer with no block at all.")], "po_big",
              filler_bytes=5_000_000, filler_after_idx=1)
check("fixture is larger than 4 MB", os.path.getsize(big) > 4_000_000, str(os.path.getsize(big)))
rc, blocked, why, _ = stop(PO, big)
check("5 MB transcript, prompt before the window -> still blocks", rc == 0 and blocked, "rc=%s blocked=%s" % (rc, blocked))

# Updated 2026-11-20 after an independent grader pass: a schema-less block
# encoded the substring loophole; the case still pins the 5 MB tail window.
VALID_PO = ("<optimized_prompt><role>Analyst choosing the first sensitivity analysis.</role><inputs>none</inputs>"
            "<instructions>1. Rank the three analyses.</instructions><assumptions>none</assumptions>"
            "<eval>check: one analysis is named first - judge: reading the reply</eval></optimized_prompt>")
big_ok = write_t([U(LONG_PROMPT), A("start"), A(VALID_PO + " then the answer.")], "po_big_ok",
                 filler_bytes=5_000_000, filler_after_idx=1)
rc, blocked, why, _ = stop(PO, big_ok)
check("5 MB transcript with a block present (in-window) -> allows", rc == 0 and not blocked)

big_skip = write_t([U("thanks"), A("start"), A("You are welcome.")], "po_big_skip",
                   filler_bytes=5_000_000, filler_after_idx=1)
rc, blocked, why, _ = stop(PO, big_skip)
check("5 MB transcript, trivial prompt before the window -> allows", rc == 0 and not blocked)

big_nh = write_t([U('Another Claude session sent a message:\n<agent-message from="abc">\n[Subagent hand-back] ' + LONG_PROMPT,
                    isMeta=True, origin={"kind": "peer"}), A("start"), A("Understood.")], "po_big_nh",
                 filler_bytes=5_000_000, filler_after_idx=1)
rc, blocked, why, _ = stop(PO, big_nh)
check("5 MB transcript, non-human turn start before the window -> allows", rc == 0 and not blocked)

huge = write_t([U(LONG_PROMPT), A("start"), A("answer")], "po_huge", filler_bytes=70_000_000, filler_after_idx=1)
rc, blocked, why, secs = stop(PO, huge)
check("70 MB transcript, prompt beyond the 64 MB bound -> fails open (allows)", rc == 0 and not blocked)
check("70 MB transcript returns in under 30 s", secs < 30, "%.1fs" % secs)
os.remove(huge)

print("%d checks, FAILURES: %d" % (n, bad))
shutil.rmtree(TMP, ignore_errors=True)
sys.exit(1 if bad else 0)
