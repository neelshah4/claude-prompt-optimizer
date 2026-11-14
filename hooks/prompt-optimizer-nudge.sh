#!/bin/sh
# Deterministic prompt-optimizer directive (hardened 2026-06-07; precision pass 2026-06-07b;
# skip #9 added 2026-07-03; pre-filter gate added 2026-07-09; additionalContext payload
# rewritten 2026-07-12, conversion-enforcement pass; 2026-11-14 human-turns-only a0 markers,
# additionalContext skip list aligned to the follow-up rule, bare-continuation suppression).
#
# Same-change-set contract (three-way): this nudge hook, the new Stop hook
# prompt-optimizer-stop-check.sh (the fire-rate backstop that audits a finished turn), and
# the prompt-optimizer SKILL.md Skip list must move together — the skip enumeration in the
# additionalContext string below is verbatim-aligned with the skill's Skip categories, and
# the Stop hook enforces a strict high-confidence SUBSET of "should fire". Edit one, edit all.
#
# Injects a firm directive so the prompt-optimizer skill fires on any substantive prompt —
# The user no longer types "use prompt optimizer first". This hook now PRE-FILTERS before
# printing: it silently suppresses injection ONLY on a small set of high-confidence trivial
# prompts (pure greetings, bare acks/continuations, bare yes/no, tightly-anchored
# status/verification checks, and single deterministic commands). Everything else —
# including anything ambiguous, long, multi-clause, or containing a content-production verb
# — injects. This gate is a strict, conservative SUBSET of the skill's own Skip list (see
# prompt-optimizer/SKILL.md); the skill still enforces the remaining skip categories
# (single-fact lookups, bare definitions, in-prompt continuations, block-would-exceed-answer)
# in-context, not the hook. False negatives (failing to inject on a real task) are far worse
# than false positives, so parse failures and empty prompts fall open to INJECT.

input=$(cat)
prompt=$(printf '%s' "$input" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null)

emit() {
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"[prompt-optimizer] Invoke the prompt-optimizer skill first on every human-typed prompt unless it matches a Skip category (greeting, bare ack, bare yes/no, status check, single deterministic command, pure continuation or micro-edit under 25 words, single-fact lookup, bare definition, block longer than the answer). A follow-up of 25 words or more that carries answers, decisions or new instructions fires. Put its optimized_prompt block at the top of the response. When uncertain, fire."}}
JSON
}

# Fall open on any extraction failure or empty prompt — never suppress on a parse failure.
if [ -z "$prompt" ]; then
  emit
  exit 0
fi

# --- Step (a0): background-task event, not a human turn. Suppress before anything else. ---
# These arrive as a UserPromptSubmit with a payload the harness wrote (a finished background
# command, a Monitor event, an agent result). Step (a) below force-injects on any prompt over
# 15 words, so a notification payload always tripped it and the nudge fired on turns the user
# never spoke in — observed twice on 2026-08-01. Matched on harness-emitted markers, never on
# text shape, so a human quoting one of these strings in a real request still fires.
case "$prompt" in
  *"[SYSTEM NOTIFICATION - NOT USER INPUT]"*|*"<task-notification>"*|*"<local-command-stdout>"*)
    exit 0 ;;
esac

# --- Step (a0b): other non-human turns (2026-11-14): subagent hand-back, compaction or
# continuation summary, scheduled-task start, <side-sessions-event>, <ci-monitor-event>.
# Matched only on the OPENING of the prompt (first ~400 characters, leading whitespace
# dropped), so a human who quotes "[Subagent hand-back]" or a tag mid-message still fires.
# Real openings (transcripts, 2026-11): "Another Claude session sent a message:\n<agent-message
# from=...>\n[Subagent hand-back] ...", "This session is being continued from a previous
# conversation ...", "<scheduled-task name=... file=...>". The two event tags are documented as
# genuine only as their own message; no live payload of those two was found in 60 transcripts.
head=$(printf '%s' "$prompt" | head -c 400 | tr -d '\r' | awk 'NF{f=1} f' | sed 's/^[[:space:]]*//')
case "$head" in
  "Another Claude session sent a message"*|"<agent-message from="*|\
  "This session is being continued from a previous conversation"*|\
  "<scheduled-task"*|"<side-sessions-event"*|"<ci-monitor-event"*)
    exit 0 ;;
esac

lower=$(printf '%s' "$prompt" | tr 'A-Z' 'a-z')

# --- Step (a): FORCE-INJECT first — content-production verb stem, long prompt, or multi-sentence.
# This dominates every skip test below; it is what makes suppressing a real task nearly impossible.
VERB_RE='write|draft|analyz|build|creat|review|summar|design|plan|compar|explain|evaluat|optim|generat|revis|edit|critique|assess|model|calculat|implement|refactor|debug|research|outline|rewrite'
if printf '%s' "$lower" | grep -Eq "$VERB_RE"; then
  emit
  exit 0
fi

words=$(printf '%s' "$lower" | wc -w | tr -d ' ')
if [ "$words" -gt 15 ]; then
  emit
  exit 0
fi

# Multi-sentence: a '.' or '?' followed by whitespace then more text (not a filename/abbrev
# where the punctuation is glued to the next character, e.g. "foo.txt").
if printf '%s' "$lower" | grep -Eq '[.?][[:space:]]+[^[:space:]]'; then
  emit
  exit 0
fi

# --- Step (b): TIER-A hard-skip — pure greeting / bare ack-continuation / bare yes-no,
# only when the WHOLE prompt reduces to one of these (anchored ^...$).
GREETING_RE='^(hi|hey|hello|good (morning|afternoon|evening)|yo|sup|howdy)[.!\ ]*$'
ACK_RE='^((thanks?|thank you|ok(ay)?|got it|great|perfect|nice|cool|sounds good|yep|yeah|nope|sure|k|done)[,.!]?[[:space:]]*)+$'
YESNO_RE='^(yes|no)[.!\ ]*$'
# Defined here, above its use: an unset pattern is an empty regex, which matches every prompt
# and silently suppressed all short prompts (caught 2026-11-14 before ship).
CONT_BARE_RE='^(continue|resume|go on|keep going|carry on)[.!\ ]*$'

if printf '%s' "$lower" | grep -Eq "$GREETING_RE" \
  || printf '%s' "$lower" | grep -Eq "$ACK_RE" \
  || printf '%s' "$lower" | grep -Eq "$YESNO_RE" \
  || printf '%s' "$lower" | grep -Eq "$CONT_BARE_RE"; then
  exit 0
fi

# --- Step (c): TIER-B skip — anchored status/verification check, or a single short
# deterministic command (only when step (a) did not already fire).
STATUS_RE='^(what[[:punct:]]?s (running|left|next|the status)|did (it|that|.{0,25}) (work|finish|pass|run)|is .{0,30} (installed|running|done|ready|up)|are we|check (it|the status|my changes))\??$'
CMD_RE='^(rename|move|mv|delete|rm|open|run|install|cd|ls|cat|git|npm|node|python)\b'

if printf '%s' "$lower" | grep -Eq "$STATUS_RE"; then
  exit 0
fi

if printf '%s' "$lower" | grep -Eq "$CMD_RE" && [ "$words" -le 10 ]; then
  exit 0
fi

# --- Step (d): DEFAULT — inject. ---
emit
exit 0
