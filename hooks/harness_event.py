#!/usr/bin/env python3
"""Shared UserPromptSubmit pre-filter (2026-11-16): is this prompt a harness event?

A harness event is anything the Claude Code harness wrote onto the user channel: a finished
background task, a subagent hand-back, a compaction summary, a scheduled-task start, a side-session
or CI event, local-command output. Nobody typed it, so the nudge hooks stay silent on it.

Markers are matched ONLY against the opening of the prompt (leading whitespace and a BOM are
ignored), never anywhere in the body, so a human who quotes a marker mid-message still gets each
hook's normal behavior. The openings below follow the shapes the harness writes onto the user channel:
  "Another Claude session sent a message:\n<agent-message from=...>\n[Subagent hand-back] ..."
  "This session is being continued from a previous conversation ..."
  "<scheduled-task name=... file=...>"      "<task-notification>\n<task-id>..."
  "<local-command-stdout>..."               "<system-reminder>\nThe session ... you started ..."
The <side-sessions-event> and <ci-monitor-event> tags are the documented forms.

Library use (python hooks):   from harness_event import is_harness_event
Shell use (one process, replaces the hook's own prompt extraction):
    prompt=$(printf '%s' "$input" | python3 -S "$(dirname "$0")/harness_event.py" extract); rc=$?
    [ "$rc" -eq 10 ] && exit 0
  extract prints the prompt field and exits 0; it exits 10 when the prompt is a harness event;
  unreadable stdin prints nothing and exits 0 (the hook's own empty-prompt rule then applies).
  A caller treats any other status (module missing, interpreter error) as "fall back to the old
  inline extraction", so a broken filter can never change a hook's normal behavior.
Check mode (no argument): exit 0 = harness event, exit 1 = not an event or unreadable.
"""
import json
import sys

MARKERS = (
    "<task-notification>",
    "[SYSTEM NOTIFICATION - NOT USER INPUT]",
    "[Subagent hand-back]",
    "Another Claude session sent a message",
    "<agent-message from=",
    "This session is being continued from a previous conversation",
    "<scheduled-task",
    "<side-sessions-event",
    "<ci-monitor-event",
    "<local-command-stdout>",
    "<local-command-caveat>",
    "<system-reminder>",
)


def is_harness_event(prompt):
    """True when the prompt OPENS with a harness marker. Any non-string is not an event."""
    if not isinstance(prompt, str):
        return False
    return prompt.lstrip("﻿ \t\r\n\x0b\x0c").startswith(MARKERS)


def _extract():
    try:
        data = json.loads(sys.stdin.read())
        prompt = data.get("prompt", "") if isinstance(data, dict) else ""
    except Exception:
        return 0
    if is_harness_event(prompt):
        return 10
    try:
        print(prompt)
    except Exception:
        pass
    return 0


def _main():
    if len(sys.argv) > 1 and sys.argv[1] == "extract":
        return _extract()
    try:
        data = json.loads(sys.stdin.read())
        prompt = data.get("prompt", "") if isinstance(data, dict) else ""
        return 0 if is_harness_event(prompt) else 1
    except Exception:
        return 1


if __name__ == "__main__":
    sys.exit(_main())
