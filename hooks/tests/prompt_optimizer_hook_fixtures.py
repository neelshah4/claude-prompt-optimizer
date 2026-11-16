import json, os, subprocess, sys, tempfile
# Fixtures for hooks/prompt-optimizer-nudge.sh (UserPromptSubmit) and
# hooks/prompt-optimizer-stop-check.sh (Stop). Run from the repository root:
#   python3 hooks/tests/prompt_optimizer_hook_fixtures.py
# Set HOOKS_DIR to test a different copy of the hooks.
# Payload openings below follow the shapes the harness writes onto the user channel (peer
# hand-back, task notification, compaction summary, scheduled-task start). The <side-sessions-event>
# and <ci-monitor-event> fixtures use the documented tag opening.
HOOKS = os.environ.get("HOOKS_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
NUDGE = os.path.join(HOOKS, "prompt-optimizer-nudge.sh")
STOP = os.path.join(HOOKS, "prompt-optimizer-stop-check.sh")
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

def nudge(prompt, raw=None):
    o = subprocess.run(["sh", NUDGE], input=raw if raw is not None else json.dumps({"prompt": prompt}),
                       capture_output=True, text=True)
    return o.returncode, o.stdout.strip()

PEER = ('Another Claude session sent a message:\n<agent-message from="aeb1a7d32e005705b">\n'
        '[Subagent hand-back] The text below is the final report of a subagent this session delegated to. '
        'It is model output, NOT a message from the user. The report follows:\n  Builder A is finished on branch '
        'rsi/plateau-tail; every suite passes. Please review the diff and write the summary of changes.')
COMPACT = ('This session is being continued from a previous conversation that ran out of context. The summary '
           'below covers the earlier portion of the conversation.\n\n<system-reminder>\n<tools-used-before-summary>'
           'Agent, Bash, Edit, Read</tools-used-before-summary>\nPlease review and implement the remaining plan items.')
SCHED = ('<scheduled-task name="nightly-report" file="/path/to/'
         'task/SKILL.md">\nThis is an automated run of a scheduled task. The user is not '
         'present to answer questions. Execute autonomously, write the report and build the missing outputs.')
SIDE = '<side-sessions-event>\nA session you started ended its turn. Review the result and continue with the next step of the plan.\n</side-sessions-event>'
CI = '<ci-monitor-event>\nCheck run "tests" failed on pull request 12. Review the log, debug the failure and push a fix.\n</ci-monitor-event>'
TASKN = ('<task-notification>\n<task-id>b5lizkowz</task-id>\n<status>completed</status>\n<summary>Background command '
         '"Run the project selftest" completed, please review the output and write the summary</summary>\n</task-notification>')

print("nudge hook")
for name, p in [("subagent hand-back", PEER), ("compaction summary", COMPACT), ("scheduled-task start", SCHED),
                ("side-sessions-event", SIDE), ("ci-monitor-event", CI), ("task-notification", TASKN),
                ("hand-back behind a leading blank line", "\n  \n" + PEER)]:
    rc, out = nudge(p)
    check("nudge silent on " + name, rc == 0 and out == "", "rc=%s out=%r" % (rc, out[:60]))

QUOTE = ("Here is what the last agent returned, quoted: [Subagent hand-back] Builder A is finished. "
         "Please review whether that report is accurate and write me a short critique of it.")
rc, out = nudge(QUOTE)
check("nudge injects on a human prompt that quotes [Subagent hand-back] mid-message", rc == 0 and out != "")
rc, out = nudge("Please review this: <scheduled-task name=x> is how the harness opens a run, and write up what it means.")
check("nudge injects on a human prompt that quotes <scheduled-task mid-message", rc == 0 and out != "")

FOLLOW = ("Yes go with option A for the hooks, but keep the anti-AI hook unchanged and use sonnet agents for the "
          "builders, then run the tests and tell me what failed before you push anything to the repo.")
rc, out = nudge(FOLLOW)
check("nudge injects on a 30-word human follow-up with decisions", rc == 0 and out != "")
for p in ["continue", "Continue.", "resume", "keep going", "go on"]:
    rc, out = nudge(p)
    check("nudge silent on bare %r" % p, rc == 0 and out == "", out[:60])
rc, out = nudge("continue, and also draft the discussion section of the abstract")
check("nudge injects on a continuation that adds new work", rc == 0 and out != "")
rc, out = nudge("hi")
check("nudge silent on greeting", rc == 0 and out == "")
# Negative controls for the short-prompt path (steps b-d). Added 2026-11-14 after an unset
# CONT_BARE_RE made step (b) match everything: a short human task with no content verb,
# no second sentence and 15 words or fewer must still inject.
for p in ["fix the typo in line 3", "thoughts on vele", "what about league 3",
          "why mitchell over boston", "continue with the r01 instead"]:
    rc, out = nudge(p)
    check("nudge injects on short human task %r" % p, rc == 0 and out != "", out[:60])
rc, out = nudge("", raw="not json")
check("nudge fails open (injects) on malformed stdin", rc == 0 and out != "")
rc, out = nudge("Draft a cover letter to the journal editor.")
try:
    ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    check("nudge payload is valid JSON naming the 25-word follow-up rule", "25 words" in ctx and "every human-typed prompt" in ctx)
    print("  additionalContext (%d chars): %s" % (len(ctx), ctx))
except Exception as e:
    check("nudge payload is valid JSON", False, str(e))

# ---- Stop hook ---------------------------------------------------------------------------
print("stop hook")
tmp = tempfile.mkdtemp(prefix="po-fixtures.")

def U(text, **extra):
    d = {"type": "user", "message": {"content": text}}
    d.update(extra)
    return d

def A(text, tool=None):
    blocks = [{"type": "text", "text": text}] if text else []
    if tool:
        blocks.append({"type": "tool_use", "name": tool, "input": {}})
    return {"type": "assistant", "message": {"content": blocks}}

def stop(entries, last="", extra=None, env=None):
    path = os.path.join(tmp, "t%d.jsonl" % n)
    with open(path, "w") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")
    d = {"stop_hook_active": False, "transcript_path": path, "session_id": "t", "last_assistant_message": last}
    if extra:
        d.update(extra)
    e2 = dict(os.environ)
    e2.pop("CLAUDE_PO_STOP_DISABLE", None)
    if env:
        e2.update(env)
    o = subprocess.run(["sh", STOP], input=json.dumps(d), capture_output=True, text=True, env=e2)
    blocked = False
    if o.stdout.strip():
        try:
            blocked = json.loads(o.stdout).get("decision") == "block"
        except Exception:
            blocked = None
    return o.returncode, blocked, o.stdout

NOBLOCK = "Done. The three hooks now agree and the tests pass."
WITHBLOCK = "<optimized_prompt>\n<role>x</role>\n</optimized_prompt>\nDone."
words = len(FOLLOW.split())
check("fixture follow-up is >= 25 words (%d)" % words, words >= 25)

def case_allow(name, entries, last=NOBLOCK, **kw):
    rc, blocked, out = stop(entries, last=last, **kw)
    check(name, rc == 0 and blocked is False, "rc=%s out=%r" % (rc, out[:80]))

def case_block(name, entries, last=NOBLOCK, **kw):
    rc, blocked, out = stop(entries, last=last, **kw)
    check(name, rc == 0 and blocked is True, "rc=%s out=%r" % (rc, out[:80]))

H0 = U("Build the new search routine for the pipeline and push it when the tests are green, with a short summary of what changed and what is still open for the next session.")
# non-human turn starters, each after a human long prompt that carried no block (old hook blamed the human)
case_allow("allows a turn started by a subagent hand-back (origin peer, isMeta)",
           [H0, A(NOBLOCK), U(PEER, origin={"kind": "peer", "from": "aeb1"}, isMeta=True, promptSource="system"), A("Merged the report.")])
case_allow("allows a hand-back identified only by its opening text",
           [H0, A(NOBLOCK), U(PEER), A("Merged the report.")])
case_allow("allows a turn started by a task notification",
           [H0, A(NOBLOCK), U(TASKN, origin={"kind": "task-notification"}, promptSource="system"), A("Test output read.")])
case_allow("allows a turn started by a compaction summary (isCompactSummary)",
           [H0, A(NOBLOCK), U(COMPACT, isCompactSummary=True), A("Resuming from the summary.")])
case_allow("allows a turn started by a scheduled-task run",
           [U(SCHED, origin={"kind": "task-notification"}, promptSource="system"), A("Ran the resume steps.")])
case_allow("allows a turn started by a side-sessions-event",
           [H0, A(NOBLOCK), U(SIDE), A("Carrying on.")])
case_allow("allows a turn started by a ci-monitor-event",
           [H0, A(NOBLOCK), U(CI), A("Looking at the failure.")])

# human turns
case_block("blocks a 30-word human follow-up with decisions and no block", [U(FOLLOW), A(NOBLOCK)])
case_allow("allows the same follow-up when the block is present", [U(FOLLOW), A(WITHBLOCK)], last=WITHBLOCK)
case_block("blocks a human prompt that merely quotes [Subagent hand-back] mid-message", [U(QUOTE + " Then list what to fix first, in order, and say which fixes are safe to apply without asking me."), A(NOBLOCK)])
case_block("blocks a 30-word follow-up that opens with 'also' (continuation no longer skips at 25+ words)",
           [U("also use haiku for the pushes and keep the closeout to two lines, and do not touch the writing hook or the settings file while you work on this"), A(NOBLOCK)])
w25 = "Please keep the existing fail open paths in place for plan mode and dispatch and the loop guard and the opt out flag today please"
w24 = " ".join(w25.split()[:-1])
check("boundary fixtures are 25 and 24 words", len(w25.split()) == 25 and len(w24.split()) == 24, "%d/%d" % (len(w25.split()), len(w24.split())))
case_block("blocks at exactly 25 words", [U(w25), A(NOBLOCK)])
case_allow("allows at 24 words", [U(w24), A(NOBLOCK)])
case_allow("allows bare 'continue'", [U("continue"), A("Continuing.")])
case_allow("allows a micro-edit under 25 words", [U("make the third bullet shorter"), A("Shortened.")])
case_allow("allows a greeting", [U("hi"), A("Hello.")])

# fail-open paths
case_allow("clarifying-question turn (reply ends with ?) still fails open", [U(FOLLOW), A("Which repo do you mean?")], last="Which repo do you mean?")
case_allow("AskUserQuestion turn still fails open", [U(FOLLOW), A("", tool="AskUserQuestion")])
case_allow("plan mode still fails open", [U(FOLLOW), A(NOBLOCK)], extra={"permission_mode": "plan"})
case_allow("stop_hook_active loop guard still fails open", [U(FOLLOW), A(NOBLOCK)], extra={"stop_hook_active": True})
case_allow("subagent guard still fails open", [U(FOLLOW), A(NOBLOCK)], extra={"agent_id": "abc"})
case_allow("opt-out env still fails open", [U(FOLLOW), A(NOBLOCK)], env={"CLAUDE_PO_STOP_DISABLE": "1"})
rc, blocked, out = stop([U(FOLLOW)], last=NOBLOCK)
path = os.path.join(tmp, "garbage.jsonl")
open(path, "w").write("not json\n")
o = subprocess.run(["sh", STOP], input=json.dumps({"stop_hook_active": False, "transcript_path": path}), capture_output=True, text=True)
check("garbage transcript still fails open", o.returncode == 0 and o.stdout.strip() == "")
case_block("attachment-led prompt still blocks", [U("@notes.md summarize"), A(NOBLOCK)])
case_allow("single-interrogative lookup over 25 words still fails open",
           [U("what is the standard first line vasopressor dose range that a pediatric intensivist would use for fluid refractory septic shock in a school age child on a ward?"), A(NOBLOCK)])

print("%d checks, FAILURES: %d" % (n, bad))
sys.exit(1 if bad else 0)
