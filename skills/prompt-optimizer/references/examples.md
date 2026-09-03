# Worked Examples

Load-on-demand reference for `prompt-optimizer`. Split out of `SKILL.md` 2026-07-24
(Opus 5 migration, progressive disclosure). Content is verbatim; no rule changed.
The trigger rules, skip list, closed schema, channel x score matrix, and handoff
selector all remain in `SKILL.md` and are authoritative there.

## Examples

### Example 1: Grant Aims (defer to grant-review, Document, 5 Q via handoff)

**User**: "Help me draft specific aims for my R01 on ML-based ventilator weaning in pediatric ARDS"

**Action**: Task = RESEARCH-DESIGN, mechanism = R01 → grant-review's intake
runs first (agency, mechanism, payoff aim, scope, timeline; 5 questions).
prompt-optimizer then synthesizes:

```
<optimized_prompt>
  <role>You are a senior PCCM physician-scientist drafting NIH R01 specific
  aims for an ML-based ventilator-weaning protocol in pediatric ARDS.</role>
  <inputs>Cohort details, model performance summary, feasibility data — to
  be supplied by user during drafting.</inputs>
  <instructions>
    1. Open with a one-paragraph storyboard establishing significance
       (mortality, weaning failure rates, current state-of-care gap).
    2. Structure 3 integrated-but-not-contingent aims: each independently
       fundable, together telling one cohesive story.
    3. For each aim include: hypothesis, approach summary, expected
       outcome, feasibility signal.
    4. Close with an impact statement framed in the reviewer's language.
  </instructions>
  <critical>Each aim must be independently fundable. Reviewer-script lens
  throughout. No aim depends on another succeeding.</critical>
</optimized_prompt>
```

### Example 2: Email (Chat channel, 2 Q after memory penalty)

**User**: "Write an email to my division chief about adding informatics FTE"

**Channel**: Chat. Task = COMMUNICATION. Raw scores: Goal=2, Format=2,
**Audience=3 (from memory of prior work)**, Constraints=1, Context=2 = **10
pre-penalty**. Apply the memory penalty to the memory-based Audience (3→2),
dropping the total to **9** → 2 Q for Chat channel.

1. "Tone and channel?" → Formal email / Casual Slack / Brief text
2. "Outcome?" → Request meeting / Propose idea / Follow up

```
<optimized_prompt>
  <role>You are drafting a formal email from a junior faculty member to
  their division chief proposing a new informatics FTE.</role>
  <inputs>Division chief = busy executive reader; user's role = proposer.</inputs>
  <instructions>
    1. Lead with the ask in the opening sentence (BLUF).
    2. Provide rationale in 2–3 sentences (clinical/operational impact,
       not technical detail).
    3. Close with a proposed next step (15-min meeting).
  </instructions>
  <critical>Under 150 words. Professional-collegial tone. No throat-clearing
  preamble.</critical>
</optimized_prompt>
```

### Example 3: Fully Specified Document (score 15 → 1 content-extending Q)

**User**: "Write a 500-word abstract for SCCM 2027. Topic: Neuro-SPARK
validation in ELSO. Audience: PCCM reviewers. Format: structured
(Background/Methods/Results/Conclusions). Include cohort size, AUROC with
CI, comparison to existing scores. 500 words max, no references."

**Channel**: Document. Task = WRITING. Scores all 3. Total = 15. At score
13+ for Document channel, ask 1 content-extending question (not a
dimensional gap):

1. "Reviewer lens to optimize for?" → Methods skeptic / Clinical pragmatist / Statistics reviewer / ML/AI reviewer

After the answer:

```
<optimized_prompt>
  <role>You are an ML clinical researcher writing a 500-word SCCM 2027
  abstract on Neuro-SPARK external validation in the ELSO registry.</role>
  <inputs>Cohort size, AUROC + 95% CI, comparison metrics vs. existing
  scores — supplied in the prompt.</inputs>
  <instructions>
    1. Background (≤80w): articulate the validation gap a [chosen-lens]
       reviewer cares about most.
    2. Methods (≤140w): cohort, derivation/validation split, comparator
       scores, statistical approach.
    3. Results (≤180w): cohort size, AUROC with CI, head-to-head numbers
       with existing scores. Lead with the strongest contrast.
    4. Conclusions (≤100w): emphasis chosen by user (e.g., external
       validity / deployment readiness / subgroup performance).
  </instructions>
  <critical>500 words max. Structured (Background/Methods/Results/
  Conclusions). No references. Reviewer lens consistent across all four
  sections.</critical>
</optimized_prompt>
```

*If the user picks "Methods skeptic,"* the placeholders resolve concretely, e.g.
instruction 1 becomes "Background (≤80w): articulate the derivation-vs-external-
validation gap a **Methods skeptic** cares about most," and `<critical>` names
"Methods-skeptic lens consistent across all four sections." The block always
ships with the chosen lens filled in, never the literal `[chosen-lens]` token.

### Example 4: Long Request (auto-trigger past one sentence)

**User** (140-word message describing a research question, available data,
preferred output, and deadline): "...Can you help me figure out whether to
pursue this?"

**Action**: Length > one sentence → trigger. Task = GENERAL. Channel = Chat. Scored
based on message content. Proceed with 0–2 Q depending on score. If the
message is rich with explicit context (score 13+), skip Phase 0 questions
and go straight to the optimized_prompt block.

### Example 5: Uncertainty Override Loop

**User**: "Build me a slide deck about pediatric ARDS for my division talk
next month."

**Channel**: Document. Initial scores: Goal=2, Format=1, Audience=2,
Constraints=1, Context=2. Total = 8 → 5 Q.

Initial batch: talk duration, audience level, template preference,
takeaway, visual style.

After answers, recompute: score rises to 12. Uncertainty = 30%, still
>20%. Continue with follow-up batch next turn:

Follow-up batch (2 more Q): which sub-topics to emphasize, data-to-
narrative ratio.

After follow-up: score = 14, uncertainty = 10%. Synthesize
`<optimized_prompt>` and proceed to build.
