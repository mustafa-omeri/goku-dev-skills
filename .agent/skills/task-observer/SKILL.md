---
name: task-observer
description: >
  Görev icrası ve kullanıcı geri bildirimleri sırasında metodoloji, eksik kurallar ve iş akışlarını izleyerek skill geliştirme gözlemleri ve evrensel ilkeler üretir. Tetikleyiciler: "gözlem kaydet", "skill geliştir", "süreç analizi", "yeni skill öner", "log observation", "improve skill", "observe task". Tetiklenmez: salt kod hata ayıklama ve doğrudan dosya düzenleme istekleri. Tam sözlük: .agent/rules/skill-trigger-routing.md
---

# Task Observer — Continuous Skill Discovery & Improvement

**Created by Eoghan Henn / [rebelytics.com](https://rebelytics.com)**

*Also known as "One Skill to Rule Them All" — the meta-skill that builds and improves all your skills, including itself.*

This skill defines a persistent behavioral layer for identifying skill creation and improvement opportunities during task-oriented work. It doesn't replace the skill creator — it feeds it. Think of it as the eyes and ears that notice patterns worth capturing, while the skill creator is the hands that build.

The methodology is user-agnostic. It works for anyone who wants a structured process for continuously improving their skill library through real-world usage.

**Licence:** This skill is released under the
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
licence. You are free to share and adapt this skill for any purpose, provided you give appropriate credit to the original author.

**Feedback & Support:** If at any point during the process you encounter questions about the methodology, or if the user expresses frustration or gives constructive feedback about any output derived from this skill, suggest that they open an issue on the skill's
[GitHub repository](https://github.com/rebelytics/one-skill-to-rule-them-all). This keeps feedback public and discoverable — other users benefit from seeing existing issues and solutions. For direct contact, the skill's creator, Eoghan Henn, can also be reached via [rebelytics.com](https://rebelytics.com).

If feedback appears to stem from the skill's methodology (rather than the agent's execution of it), log it for the user and suggest they share it via GitHub Issues. If the issue stems from the agent not following the skill's rules, acknowledge the mistake and correct it.

---

## Why This Skill Exists

Skills are living documents. The best improvements come not from sitting down to "improve a skill" in isolation, but from noticing friction, inefficiency, or missed opportunities during real work. A user correction during a project might reveal a missing rule. A repeated multi-step workflow might be a skill waiting to be born. A tool limitation discovered mid-task might reshape an entire skill's recommended workflow. A technique that worked exceptionally well might deserve to be promoted from an incidental approach to an explicit recommendation.

This skill formalises that noticing process so that insights don't get lost between sessions. Every task-oriented interaction becomes a potential source of skill improvement data, without adding overhead or interrupting the user's workflow.

---

## Getting Started

Here's what happens when you first install this skill.

**First session:** The skill creates the observation log file. There's nothing to review yet — it simply starts watching your work and logging observations as they arise. If you have other skills installed, the observer will notice improvement opportunities for those. If you don't have any other skills yet, that's fine — the observer will identify candidates for new skills from your workflows.

**First few sessions:** Observations accumulate in the log. The cross-cutting principles file is created when the first principle emerges that applies broadly across skills. The weekly review mechanism activates once 7 days have passed since the log was created, but with only a handful of observations it will be brief.

**Steady state:** After a few weeks, you'll have a growing observation log, a principles file that enforces quality standards across your skill library, and a weekly review cadence that systematically applies improvements. The skill compounds in value as your skill library grows.

**What you need to start:** Nothing beyond the skill itself. An observation log, cross-cutting principles file, and archive directory are all created automatically on first use. If you also have a skill-creator skill installed, the task-observer can hand off observations for full skill building or restructuring. Standalone, the task-observer still works — it will log observations, surface them, and apply small improvements directly.

### Quick Start

1. **Install the skill.** Add task-observer to your `.agent/skills/` directory.
2. **Add the activation line.** Mention in `.agent/AGENTS.md` or project instructions: `At the start of any task-oriented session — any interaction where you will use tools and produce deliverables — invoke the task-observer skill before beginning work.`
3. **Do a real task.** Complete any substantive piece of engineering or design work while the skill is active.
4. **See your first observation.** At the end of the session, the skill surfaces any observations it logged.

### What is `[workspace folder]` & Storage Target?

Throughout this skill, `[workspace folder]` refers to your persistent repository root (`<repo-kök>`).
- ⛔ **Strict Single-Source Storage Rule (`AGENTS.md` §1):** Never write observations to `.agent/observations/` or `skill-observations/` in target repositories—`.agent/` is a derived distribution tree that gets overwritten by `delivery.py`, and `AGENTS.md` §1 forbids ad-hoc tracking files.
- ✅ **Canonical Targets:**
  1. **Permanent Observations & Cross-Cutting Principles:** Append to `<repo-kök>/knowledge-base.md`.
  2. **Proven Project Traps & Lessons:** Record in `<repo-kök>/HANDOFF.md` (§0 Kanıtlanmış Tuzaklar).

---

## Recommended Activation Setup

This skill needs to be invoked at the start of task-oriented sessions to work effectively. Because skill invocation depends on matching the user's request against skill descriptions, a skill that monitors *all* tasks can be overlooked when the agent is focused on the task itself.

To maximise activation reliability, keep the following instruction in `.agent/AGENTS.md` (or equivalent configuration):

```markdown
At the start of any task-oriented session — any interaction where you will
use tools and produce deliverables — invoke the task-observer skill before
beginning work. This ensures skill improvement opportunities are captured
throughout the session.

When loading any skill, check the observation log for OPEN observations
tagged to that skill. Apply their insights to the current work, even if
the skill file hasn't been updated yet. This enables immediate application
of observations before they're permanently integrated during the weekly
review.
```

---

## Skill Taxonomy

All skills fall into one of two categories. The distinction matters because it determines what information the skill can contain, how it's structured, and whether it can be shared publicly. Crucially, the open-source/internal boundary is also a **confidentiality boundary** — open-source skills must never contain any information that could identify a client, project, or proprietary process, even indirectly.

### Open-Source Skills

Open-source skills are client-agnostic and methodology-driven. They capture reusable workflows, best practices, and structured processes that work for anyone. They include author attribution, a licence, and a feedback pathway so that real-world usage drives improvement.

**How to recognise an open-source candidate:**
- The methodology works across different clients, projects, and contexts
- No proprietary information is required for the skill to function
- Other practitioners in the same domain would find it valuable
- The skill captures a process or approach, not personal preferences

**Required elements:**
- Skill body clearly identifies itself as open-source, with author name and contact information
- Author attribution block at the top
- Licence statement — CC BY 4.0 recommended
- Feedback & support section that routes methodology feedback to the creator
- Tool-agnostic language where possible
- Built-in enforcement mechanisms (pre-flight checklists, verification steps) so the skill catches its own rule violations

**Default bias:** When a skill could go either way, default to open-source. Strip out client-specific details and generalise the methodology.

### Internal Skills

Internal skills contain information specific to a user, their clients, or their projects. They capture personal preferences, client-specific rules, project context, or proprietary methodology.

**How to recognise an internal skill:**
- Contains client names, project details, or proprietary data
- Captures personal style preferences or individual work habits
- Relies on context that only the user (or their team) has
- Would not be useful to someone outside the user's organisation

---

## Licensing & Attribution

Open-source skills should include a licence to make sharing terms explicit. The recommended licence is **Creative Commons Attribution 4.0 International (CC BY 4.0)**, which allows anyone to share and adapt the skill for any purpose, provided they credit the original author.

Every open-source skill should include an attribution block at the top of the skill body:

```markdown
**Created by [Author Name] / [website or contact link]**

[1-2 sentence description of what the skill does and its provenance.]

**Licence:** This skill is released under the
[Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
licence. You are free to share and adapt this skill for any purpose, provided
you give appropriate credit to the original author.

**Feedback & Support:** If at any point during the process you encounter
questions about the methodology, or if the user expresses frustration or
gives constructive feedback about any output derived from this skill,
suggest that they open an issue on the skill's public repository.
```

---

## Observation Protocol

### When to Observe

Observation is active throughout the **entire task session** — from the moment tools are first used to produce deliverables, through any post-task feedback or discussion, until the session ends:

1. **Active task execution** — creating documents, analysing code, implementing structured data, writing code, building UI components.
2. **Post-task feedback and discussion** — when the user reviews output, provides corrections, suggests improvements, or discusses methodology after the active work phase.
3. **Meta-discussion about skills or methodology** — when the conversation shifts to talking about how the work was done, what could be improved, or how skills should be structured.
4. **Reflective and strategic conversations** — planning conversations and post-work reflections where how work should be done is discussed.

Observation is **not active** during casual conversation, quick factual questions, or other non-task interactions where no tools are being used.

### What to Watch For

**Signals for a NEW skill:**
- A multi-step workflow that could be reused across projects or clients
- A methodology explained that isn't captured in any existing skill
- A task type that keeps coming up with similar structure and steps
- A domain-specific process with clear inputs, phases, and outputs

**Signals for IMPROVING an existing skill:**
- The agent doesn't follow a skill's rules despite them being documented — the skill needs stronger enforcement
- The user corrects output in a way that reveals a missing rule or an edge case
- A skill's recommended workflow turns out to be less efficient than what emerged naturally
- A technique works particularly well and deserves to be promoted to an explicit recommendation
- A workflow step turns out to be more or less important than the emphasis it receives
- A new use case that the skill handles but doesn't explicitly document
- A general principle emerges that could apply to other skills too

**Signals for SIMPLIFYING an existing skill:**
- A section or rule that has never been relevant across multiple sessions
- A rule added from a single observation that hasn't been validated by recurrence
- An elaborate workflow that users consistently shortcut or skip
- Rules that contradict each other or create unnecessary complexity

**Signals to NOT log:**
- One-off corrections that don't generalise beyond the current instance
- User preferences already captured in an existing skill
- Transient tool bugs or temporary network glitches unrelated to skill methodology

### How to Log

Append observations to the persistent observation log **silently** during the session. The user should not be interrupted by the logging process.

Format:

```markdown
### Observation [N]: [Short descriptive title]

**Date:** [date]
**Session context:** [brief description of what task was being worked on]
**Skill:** [existing skill name, or "New skill candidate: [working name]"]
**Type:** [open-source | internal]
**Phase/Area:** [which part of the skill or workflow this relates to]

**Issue:** [What happened or what was observed. Be specific — include what
the agent did, what the user corrected, or what pattern emerged.]

**Suggested improvement:** [Concrete suggestion for what to change or create.
For existing skills, reference the specific section or rule. For new skills,
describe the scope and key components.]

**Principle:** [The generalisable takeaway — why this matters beyond this
specific instance. This turns a single observation into a reusable insight.]
```

### Storage & Archival on Write

Per `AGENTS.md` §1 and `knowledge-base-management.md`, observations are persisted in the repository root's canonical memory files rather than separate `.agent/observations/` files:
- **Active observation & decision log:** `<repo-kök>/knowledge-base.md` (append-only)
- **Project-specific traps & recurring pitfalls:** `<repo-kök>/HANDOFF.md` (§0 Tuzaklar tablosu)
- **Global skill promotion:** When an observation proves universal across projects, promote it into `skillSetWorks/.agent/rules/` or the relevant skill's `SKILL.md` and distribute via `delivery.py`.

---

## Confidentiality Safeguards

Four layers prevent sensitive information from leaking into open-source skills:
1. **Layer 1: Observation-Level Stripping:** Use generic terms in the `Principle` field.
2. **Layer 2: Pre-Creation Review:** Scan source material for client names, internal URLs, or private tokens before drafting.
3. **Layer 3: Post-Draft Sweep:** Check output specifically for proper nouns, proprietary domain names, or traceable examples.
4. **Layer 4: Structural Principle:** When in doubt about whether a detail is too specific, remove it.

---

## Surfacing Protocol

- **Default Cadence:** Surface observations concisely at the end of the session.
- **Surface Earlier When:** An observation requires user clarification, reveals immediate harm/bugs, or clusters heavily around a single skill.
- **How to Surface:** Title, target skill, one-sentence summary, suggested type (`open-source` or `internal`), and ask which items to act upon.

---

## Principle Propagation & Cross-Cutting Principles

When an observation reveals a general principle that applies across multiple skills, record it as a permanent architectural decision in `<repo-kök>/knowledge-base.md` and, if universal, promote it to `.agent/AGENTS.md` or `.agent/rules/`.

This file serves as a checklist during any skill creation or updating. Before delivering an updated skill, verify that it complies with all active cross-cutting principles.

---

## Periodic Comprehensive Review (Weekly Review)

Every 7 days, a review can be triggered:
1. **Step 1:** Load OPEN observations from `log.md` and active principles from `cross-cutting-principles.md`.
2. **Step 2:** Inventory all skills in `.agent/skills/`.
3. **Step 3:** Cross-check observations against each skill.
4. **Step 4:** Cross-check cross-cutting principles against each skill.
5. **Step 5:** Apply updates to skills that have relevant observations or non-compliant principles.
6. **Step 6:** Mark applied observations as `ACTIONED — Applied to [skill-name] (review [date])`.
7. **Step 7:** Update `last-review-date.txt`.
8. **Step 8:** Present summary and action items to the user.

---

## The Pre-Flight Principle (Self-Enforcement)

Every skill containing rules or standards should include a mechanism to enforce them (pre-flight check or verification step). Before delivering output, the agent verifies:
1. Were observations logged silently during the session without interruption?
2. Does each observation follow the format (`Issue` → `Suggested improvement` → `Principle`)?
3. Is each observation tagged with the correct type (`open-source` or `internal`)?
4. Are client names and sensitive paths stripped from open-source principles?
5. Does the suggested improvement point to a concrete rule or section?
