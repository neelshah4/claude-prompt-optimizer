#!/bin/sh
# prompt-optimizer Stop hook — HIGH-CONFIDENCE-ONLY conversion backstop (added 2026-07-12).
#
# (1) PRECISION BACKSTOP, NOT A BLANKET ENFORCER. This hook blocks a finished turn ONLY when
#     the initiating prompt is a high-confidence prompt-optimizer MISS — an attachment-led ask
#     (an @-token), a pasted plan / persona to execute, or a long (>40w) content-verb prompt —
#     AND no optimized_prompt block was produced. It CANNOT reproduce the skill's soft skips
#     (single-fact lookup, definition, block-would-exceed-answer) or its deferred-block turns
#     (clarifying questions, dispatch, plan mode), so it does NOT try: it FAILS OPEN (exit 0,
#     no block) on every ambiguity, missing field, unreadable transcript, or parse error. Net
#     false-block surface is ~zero; it still catches the two biggest measured miss clusters.
#
# (2) THE TRANSCRIPT JSONL SCHEMA IS UNDOCUMENTED. We grep it empirically ({"type":"user"|
#     "assistant","message":{"content": <string|array of blocks>}}, tool_use as an assistant
#     content block). It may change across Claude Code versions. That is exactly why the ENTIRE
#     transcript parse is wrapped in one try/except that exits 0 on any error — a schema change
#     degrades this hook to "allow stop", never to a false block and never to a loop.
#
# (3) LOOP GUARD FIRST. `stop_hook_active == true` -> exit 0 before anything else. This is NOT
#     auto-enforced by the harness; omitting it risks a runaway Stop->block->Stop loop (a
#     documented ~50-minute incident, issue #55754).
#
# (4) OPT-OUT. `CLAUDE_PO_STOP_DISABLE=1` in the environment -> exit 0. Scheduled / headless /
#     workflow task definitions (pubmed-watcher, career-tracker, review-passport runs) set this
#     so a non-interactive agent is never nagged; plan / bypassPermissions modes also exit 0.
#
# (5) THREE-WAY SAME-CHANGE-SET CONTRACT. This Stop hook, the UserPromptSubmit nudge hook
#     (prompt-optimizer-nudge.sh), and the prompt-optimizer SKILL.md Skip list move together.
#     The high-confidence miss signals + hard-skip exclusions below are a strict SUBSET of the
#     nudge's "should fire" set (the nudge's VERB_RE / GREETING_RE / ACK_RE / YESNO_RE /
#     STATUS_RE / CMD_RE are reused verbatim). Edit one, re-audit all three.

input=$(cat)

CLAUDE_PO_STOP_INPUT="$input" python3 <<'PY'
import os, re, json, string, sys

def allow():
    # Fail OPEN: no stdout, exit 0 -> Stop proceeds, turn is NOT blocked.
    sys.exit(0)

# --- Step 2: parse the Stop-hook stdin JSON. Any exception -> fail open. ---------------------
try:
    data = json.loads(os.environ.get("CLAUDE_PO_STOP_INPUT", ""))
    if not isinstance(data, dict):
        allow()
except SystemExit:
    raise
except Exception:
    allow()

stop_hook_active   = bool(data.get("stop_hook_active", False))
permission_mode    = data.get("permission_mode", "default")
transcript_path    = data.get("transcript_path", "") or ""
last_assistant_msg = data.get("last_assistant_message", "") or ""
if not isinstance(last_assistant_msg, str):
    last_assistant_msg = ""

# --- Step 3: loop guard FIRST (mandatory; issue #55754). ------------------------------------
if stop_hook_active:
    allow()

# --- Step 4: subagent guard. Never block a dispatched subagent (we register Stop, not SubagentStop). ---
if data.get("agent_id") or data.get("agent_type"):
    allow()

# --- Step 5: plan / headless guards + env opt-out. -----------------------------------------
if permission_mode in ("plan", "bypassPermissions"):
    allow()
if os.environ.get("CLAUDE_PO_STOP_DISABLE") == "1":
    allow()

# --- Step 6: transcript must exist and be readable. -----------------------------------------
if not transcript_path or not os.path.isfile(transcript_path):
    allow()

# --- Regexes (VERB/GREETING/ACK/YESNO/STATUS/CMD reused verbatim from the nudge hook). ------
VERB_RE   = r"write|draft|analyz|build|creat|review|summar|design|plan|compar|explain|evaluat|optim|generat|revis|edit|critique|assess|model|calculat|implement|refactor|debug|research|outline|rewrite"
GREETING_RE = r"^(hi|hey|hello|good (morning|afternoon|evening)|yo|sup|howdy)[.! ]*$"
ACK_RE      = r"^((thanks?|thank you|ok(ay)?|got it|great|perfect|nice|cool|sounds good|yep|yeah|nope|sure|k|done)[,.!]?\s*)+$"
YESNO_RE    = r"^(yes|no)[.! ]*$"
_PUNCT      = "[" + re.escape(string.punctuation) + "]?"
STATUS_RE   = (r"^(what" + _PUNCT + r"s (running|left|next|the status)|"
               r"did (it|that|.{0,25}) (work|finish|pass|run)|"
               r"is .{0,30} (installed|running|done|ready|up)|are we|"
               r"check (it|the status|my changes))\??$")
CMD_RE      = r"^(rename|move|mv|delete|rm|open|run|install|cd|ls|cat|git|npm|node|python)\b"

# Continuation-anaphora (verbatim from target-artifacts.md §B step 7c; that file is not live —
# the only copy on disk is the archived provenance copy at
# ~/.claude/backups/skill-upgrades/skill-upgrade-prompt-optimizer-20260711/target-artifacts.md).
CONT_RE = (r"^(resume|continue|go on|keep going|proceed|redo|try again|also|now (make|do|add)|"
           r"check it|update the|the .{0,30} you (built|made|wrote)|"
           r"make the .{0,25}(shorter|longer|bigger|smaller))")

# Pasted-plan / persona markers.
PERSONA_PLAN_RE = r"\byou are an?\b|intended executor|# plan|deploy (multiple |sub)?agents|using multi[- ]agent"

TERMINAL_TOOLS = {"AskUserQuestion", "ask_user_input_v0", "ExitPlanMode", "EnterPlanMode", "Task"}

def extract_text(content):
    """Text from a message.content that may be a string OR a list of blocks. tool_use /
    tool_result blocks contribute no user/assistant *text* and are skipped."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict):
                if b.get("type") == "text" and isinstance(b.get("text"), str):
                    parts.append(b["text"])
            elif isinstance(b, str):
                parts.append(b)
        return "".join(parts)
    return ""

# --- Step 7: everything below is one big try/except -> fail open on ANY error. ---------------
try:
    with open(transcript_path, "rb") as fh:
        blob = fh.read()
    # Bounded tail read for speed; drop a partial first line if truncated.
    if len(blob) > 4_000_000:
        blob = blob[-4_000_000:]
        nl = blob.find(b"\n")
        if nl != -1:
            blob = blob[nl + 1:]
    text = blob.decode("utf-8", "replace")

    entries = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))  # garbage line -> raises -> fail open

    # 7a. Last real user prompt (skip tool_result-only + injected [prompt-optimizer]/system-reminder).
    # PRIMARY filter is the isMeta/sourceToolUseID guard immediately below: the Skill tool injects
    # the loaded SKILL.md body as a type:"user" transcript entry (isMeta:true, sourceToolUseID set
    # to the invoking tool_use id, text starting "Base directory for this skill: ..."), and other
    # harness-synthesized entries (queued auto-continuations, local-command caveats, image-size
    # annotations, Stop-hook feedback) carry isMeta:true the same way. None of these are a human
    # prompt. Empirically verified 2026-08-22 against 10 recent transcripts (1339 type:"user"
    # entries; 46 carried isMeta or sourceToolUseID, 22 of them literal Skill-body injections; zero
    # genuine human-typed prompts carried either field). The two string-prefix checks below are a
    # narrower, secondary defense for the nudge hook's own additionalContext marker text, which in
    # practice never appears as a user-entry (see N7) — they are not the mechanism that filters
    # Skill-injected bodies; the isMeta guard is.
    user_idx = -1
    prompt_text = ""
    for i, e in enumerate(entries):
        if not isinstance(e, dict) or e.get("type") != "user":
            continue
        if e.get("isMeta") or e.get("sourceToolUseID"):
            continue
        msg = e.get("message") or {}
        txt = extract_text(msg.get("content"))
        t = txt.strip()
        if not t:
            continue
        if t.startswith("[prompt-optimizer]") or t.startswith("<system-reminder>"):
            continue
        # Background-task events are delivered as type:"user" entries but carry no human
        # instruction — they are a completed Bash job, a Monitor line, or a finished agent
        # reporting back. Treating one as "the initiating prompt" makes a long tool-result
        # payload look like a long content-verb task, and the hook then demands an
        # optimized_prompt block for a turn the user never spoke in. Observed live twice on
        # 2026-08-01. The markers are emitted by the harness, not by any model, so they are a
        # reliable provenance signal rather than a text-shape guess.
        if ("[SYSTEM NOTIFICATION - NOT USER INPUT]" in t
                or "<task-notification>" in t
                or t.startswith("<local-command-stdout>")):
            continue
        user_idx = i
        prompt_text = txt
    if user_idx == -1:
        allow()

    # 7b. All assistant text this turn + the terminal tool_use name.
    assistant_text = ""
    last_tool_use_name = ""
    for e in entries[user_idx + 1:]:
        if not isinstance(e, dict) or e.get("type") != "assistant":
            continue
        content = (e.get("message") or {}).get("content")
        assistant_text += extract_text(content) + "\n"
        if isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    nm = b.get("name", "")
                    if nm:
                        last_tool_use_name = nm

    low = prompt_text.lower()
    stripped = prompt_text.strip()
    words = len(low.split())

    # --- High-confidence miss signal ---
    has_at   = bool(re.search(r"(^|\s)@\S", prompt_text))
    heading  = bool(re.match(r"#{1,3}\s", low.lstrip()))
    persona  = bool(re.search(PERSONA_PLAN_RE, low))
    long_verb = (words > 40) and bool(re.search(VERB_RE, low))
    high_conf = has_at or heading or persona or long_verb

    # --- Exclusions (any one True -> do NOT block) ---
    ends_q = stripped.endswith("?")
    multi_sentence = bool(re.search(r"[.?!]\s+\S", stripped))
    single_interrogative = ends_q and not multi_sentence

    trivial = (
        bool(re.search(GREETING_RE, low)) or
        bool(re.search(ACK_RE, low)) or
        bool(re.search(YESNO_RE, low)) or
        bool(re.search(STATUS_RE, low)) or
        (bool(re.search(CMD_RE, low)) and words <= 10)
    )

    continuation = bool(re.search(CONT_RE, low))

    block_present = ("optimized_prompt" in assistant_text) or ("optimized_prompt" in last_assistant_msg)
    lam_ends_q = last_assistant_msg.strip().endswith("?")
    tool_terminal_defer = last_tool_use_name in TERMINAL_TOOLS

    should_block = (
        high_conf
        and not single_interrogative
        and not trivial
        and not continuation
        and not block_present
        and not lam_ends_q
        and not tool_terminal_defer
    )

    if should_block:
        reason = ("This turn's prompt looks like a task (attachment-led or a pasted plan) but no "
                  "optimized_prompt block was produced. Prepend the 5-element optimized_prompt "
                  "block per the prompt-optimizer skill at the top of your continued response — "
                  "or, if a skip category genuinely applies, state which one in one line and finish.")
        # Compact separators to match target-artifacts.md §B verbatim ({"decision":"block",...}).
        # (target-artifacts.md is archived, not live — see
        # ~/.claude/backups/skill-upgrades/skill-upgrade-prompt-optimizer-20260711/target-artifacts.md.)
        sys.stdout.write(json.dumps({"decision": "block", "reason": reason},
                                    ensure_ascii=False, separators=(",", ":")))
        sys.exit(0)

    allow()

except SystemExit:
    raise
except Exception:
    allow()
PY

exit 0
