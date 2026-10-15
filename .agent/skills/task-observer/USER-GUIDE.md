# Getting Started with the task-observer meta-skill (aka "One skill to rule them all")

This guide includes practical tips for getting value out of the meta-skill. It's based on daily usage of the skill across AI coding assistants, agentic environments, and desktop tools.

The best way to get started with this work setup in any environment is to grab the skill, the user guide and the readme file and feed them to the AI of your choice. It should then be able to guide you towards the best equivalent of this setup for your particular environment, no matter which system you use. As long as skills are supported, this approach works with any AI system, with minimal adjustments.

## Where the skill runs

Once placed into your `.agent/skills/` directory (or equivalent agent capabilities setup), it is available across agent sessions, CLI tasks, and terminal workflows. Its full potential is exploited during multi-step, tool-assisted engineering tasks.

## Using the skill in chats / single turns

You can use the meta-skill in regular chats or single-session interactions: the meta-skill will log observations during the interaction, but without persistent workspace access, it won't write them directly to a shared storage.

In non-persistent environments, you can request a handoff doc at the end of the session, or the skill will guide the agent to offer one proactively as the interaction winds down. You can then take that handoff doc into your persistent workspace.

## Setting up your shared folder

When starting a persistent task session, ensure the agent has access to your workspace folder. The observer logs to:
`[workspace folder]/skill-observations/log.md` (or `.agent/observations/log.md`).

## Dual-layer activation

The task observer needs to be active at the start of a session to automatically log observations in the background, but you can always invoke it later and ask the agent to analyse the entire conversation for skill creation or improvement potentials. The skill can activate on its own by matching task descriptions against its triggers.

The more reliable approach is a dual-layer setup: the skill's own triggers plus a direct instruction in your `.agent/AGENTS.md` (or project instructions) telling the agent to keep the task observer loaded during task-oriented work.

## How the skill works during a session

Once the skill is loaded, it logs observations silently in the background without interrupting your work. This defensive design is intentional: the skill stays out of your way.

## Checking in on observations

Towards the end of a session, ask: "Any observations logged?" The agent will provide an overview of everything captured. You can also prompt the agent to perform a deeper analysis of the session to find observations that might have been missed.

## The cross-cutting principles file

As observations accumulate, some reveal principles that aren't specific to one skill but apply across the whole library (e.g. "every skill with rules should have an enforcement mechanism"). The task observer captures these in `cross-cutting-principles.md`. When skills are later created or updated, the agent checks them against these principles automatically.

## Open-source vs internal skills

The task observer distinguishes between two types of skills:
- **Open-source skills:** Methodology-driven and project-agnostic. No proprietary information, client names, or private credentials.
- **Internal skills:** Information specific to you, your organization, or your private projects.

## The weekly review

The skill has a built-in review cycle. If more than 7 days have passed since the last review and there are open observations waiting, the agent can trigger a comprehensive review at the start of a session, cross-checking all open observations against the skill set and applying updates.

---
Thanks for reading,
Eoghan (rebelytics.com)
