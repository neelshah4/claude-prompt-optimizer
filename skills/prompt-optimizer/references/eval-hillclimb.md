# Eval design and hillclimbing

Read this when a block's `<eval>` is in `hillclimb` mode, or when a `check`-mode eval
fails and the fix is not obvious. Distilled from Anthropic's "Automating eval design and
hillclimbing" post (claude.dev blog, read 2026-09-28). It ships the same method as the
`/claude-api build-eval` and `/claude-api hillclimb` commands in Claude Code.

Two terms. An **eval** is a fixed set of test cases plus a grader that turns each output
into pass or fail, so "better" becomes a number instead of an impression. **Hillclimbing**
is changing one thing, re-running the eval, and keeping the change only if the number
goes up on cases the optimizer never looked at.

## Which mode

| Mode | When | What it costs |
|------|------|---------------|
| `check` | Every triggered task. One-off deliverables: an email, an analysis, a deck, a code change. | 2–5 pass/fail checks, run once against the finished artifact before closeout. |
| `hillclimb` | The thing being built runs again: a skill, prompt, agent, tool description, hook, workflow script, pipeline, template, or extraction/classification step. Also any Workflow run, and any ask to optimize, iterate, improve, or make cheaper. | A case set, a grader, a baseline, then rounds until the score stalls. |

A one-off with no case set cannot be hillclimbed: there is nothing to split and nothing
to generalize to. Its eval is the `check` list. If a one-off turns out to be the first
instance of a recurring job, promote it: its checks become the grader and its output
becomes the first case.

## `check` mode

Write each check so the answer can be read off the artifact or a tool output: "all 12
rows have a source URL", "word count ≤ 300", "script exits 0 on the sample file", "every
aim names a primary endpoint". Never a 1–5 quality scale; a scale drifts run to run and
cannot fail. At least one check names an outside judge (`— judge: <what>`): a tool
run, a fetched source, a held-out set, or a reviewer that did not write the artifact;
see `depth-pass.md`. Run the checks before the closeout and state the tally ("4/4 checks
passed", or which failed and why). When the Completion Contract fires, its countable
done-condition is one of the checks.

## Building a `hillclimb` eval

1. **Cases from real use, in this order:** past outputs and transcripts of the thing
   (scrubbed of patient data and credentials); logged corrections and bug reports; 5–10
   hand-written cases; synthetic cases, but only when each is anchored to a real one.
   15–50 cases is enough to start.
2. **Pick hard cases by human judgment, not by what today's model gets wrong.** A set
   built from one model's failures measures that model's blind spots and flatters every
   change that happens to patch them.
3. **Grader.** Programmatic when the output is constrained: exact match, fixed label,
   JSON schema, tests pass, a gate script exits 0. Otherwise an LLM judge that answers a
   list of yes/no criteria per case, never a 1–5 score.
4. **Four properties to confirm before climbing:**
   - *Production-aligned:* the cases look like real use, not like what was easy to write.
   - *Scales:* a stronger model or higher effort scores higher. If it does not, the eval
     is measuring something other than quality.
   - *Headroom:* the best configuration scores well below 100%. Above ~95% at baseline,
     there is little left to measure; switch the goal to cost at the same score or add
     harder cases.
   - *Low variance:* repeat runs agree.
5. **Baseline diagnostics.** Run the baseline twice. Same output must get the same
   verdict (grader consistency). Timeouts, API errors, and truncations are excluded and
   reported, not scored as failures. A case that fails on every replicate is a suspect
   case or grader before it is a suspect system.

## The loop

1. Split the cases at random into train and test (about 2:1). The optimizer never reads
   test transcripts.
2. Read only train failures. Propose **one** focused change to **one** surface.
3. Run both sets.
4. **Keep** the change only if train and test both improve beyond run-to-run noise.
   **Revert** if only train improves (overfitting) or if either set regresses.
5. Log the round: change, train score, test score, cost per case, kept or reverted.
   A reverted change is not retried without a new reason. When two variants score
   within noise, keep the simpler one.
6. **Stop** after 2–3 rounds with no gain, when no single fix could move the score past
   the noise margin, or at the budget cap.
7. **At the stall, sort the remaining failures by root cause.** Some are real defects to
   fix next session. Others are an ambiguous case or a grader that contradicts itself;
   fix the eval, re-baseline, and only then resume.

**Surfaces, cheapest first:** prompt or skill text; tool descriptions; model, effort, and
API parameters (a cost climb holds the score and tries the cheaper model or lower
effort); harness code last.

**Guards against gaming the eval:**
- Never paste failure content or case text into the surface being tuned.
- The system under test never sees reference answers.
- No harness change that exists only to satisfy an eval quirk: a hardcoded edge case, a
  tool only the eval needs. Those do not carry to real use.
- One metric per climb: accuracy, or cost at fixed accuracy. "Make it better" is not an
  objective.

## Worked shapes

- **Cost climb (from the post):** a support-ticket classifier on 44 cases (30 train, 14
  test). Removing contradictory rules and ritual steps, then dropping to a smaller model
  at low effort, took held-out accuracy from 78.6% to 90.5% at about a fifth of the cost
  per ticket.
- **Stall analysis (from the post):** a docs-derived eval for an API skill climbed from
  66% to 77%, then sat flat for many rounds. Root-cause sorting showed the content was
  present but the model reached for deprecated patterns; a table mapping old to new
  patterns, plus fixing ambiguous tasks and a self-contradicting grader, took it to ~88%.
