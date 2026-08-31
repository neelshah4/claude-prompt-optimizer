# Question Banks by Task Type

Load-on-demand reference for `prompt-optimizer` Phase 0.E. Split out of `SKILL.md`
2026-07-24 (Opus 5 migration, progressive disclosure). Content is verbatim; no rule changed.
Read this only when Phase 0.D has determined a question count above 0.

#### E. Question Banks by Task Type

Use `ask_user_input_v0` with clickable options when choices are discrete.
Ask about dimensions scoring 1–2 first. For Document channel at score 13+,
the single question should sharpen output direction, not re-ask
already-specified content.

**Perspective-guided questions (STORM technique).** When a framing/emphasis
question is warranted — especially the score-13+ Document *content-extending*
question — make it **perspective-guided**: surface 2–4 concrete, task-relevant
perspectives / stakeholders / reviewer-lenses as the options rather than a vague
"what's the emphasis?" (e.g., reviewer lens in Example 3: Methods skeptic /
Clinical pragmatist / Statistics reviewer / ML reviewer; for an exec memo:
CFO / ops lead / skeptical board member; for a teaching deck: novice learner /
expert peer / cross-specialty). This borrows STORM's core move — discover the
distinct angles a deliverable must satisfy, then ask from those angles — and
yields sharper output direction than an open prompt. **Bounded by Economy:** it
*replaces* the framing question's options with concrete lenses; it does NOT add
questions beyond the channel × score matrix.

**How to read the banks below.** Every task type is scored on the same five
dimensions (Phase 0.C: Goal / Format / Audience / Constraints / Context). Ask the
weakest (1–2) dimensions first. The banks give only the **task-specific options**
for each dimension — the dimension names and scoring are the Phase 0.C rubric,
not repeated here. Rows marked *(doc only)* are the extra 4th/5th question a
Document task can spend when its score is low.

| Task type | Goal | Format | Audience / Context | Constraints | *(doc-only) 5th* |
|-----------|------|--------|--------------------|-------------|------------------|
| **WRITING** | Persuade / Inform / Request action / Document | Brief <500 / Standard 500–1500 / Long-form 1500+ | Peer expert / Leadership / Non-specialist / Journal reviewers | Word limit / Journal style / Template / None | *Structure:* IMRAD / Exec brief / Narrative / Memo |
| **ANALYSIS** | What question are you answering? *(free-text)* | Code+interpretation / Figures+narrative / Report / Slides | *Data shape:* CSV·Excel / REDCap / EHR extract / describe it | Stats: Frequentist / Bayesian / Descriptive / decide-for-me | *Comparator:* vs baseline / vs literature / vs competing method / none |
| **CODE** | What does it do when done? *(free-text)* | Python / R / JavaScript / Other | *(entry point)* CLI / Jupyter / Module / Streamlit / Colab | Specific library / Performance / Tests / None | *Error handling:* Fail loud / Retry / Log-and-skip / decide |
| **PRESENTATION** *(always Document)* | Audience takeaway? *(free-text)* | — | Research peers / Division / Leadership / Conference | Duration/template: 8-min / 15-min / Poster / Institutional / Other | *Opening + Closing:* data/narrative/case/question-first; takeaway+QR / Q&A / acks / CTA |
| **COMMUNICATION** | Request meeting / Propose collab / Follow up / Introduce | — | *Relationship:* Senior / Peer / External / Committee | Tone/channel: Formal email / Slack / Text / LinkedIn | *Length:* <100 / 100–200 / 200–400 / long |
| **RESEARCH-DESIGN** *(always Document)* | Stage: Concept / Aims / Protocol / Stats plan | Aims / Design critique / Power calc / Methods draft | *Funding:* R01 / R21 / K08–K23 / Foundation / not-grant / unsure | Scope: single aim / 3-aim cohesive / multi-project / exploratory | *Timeline:* <3mo / 3–6 / 6–12 / >12 |

**GENERAL**: pick options from whichever bank matches the gap dimensions.
