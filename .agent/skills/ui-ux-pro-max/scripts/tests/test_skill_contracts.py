"""Distribution contracts for the merged `.agent/` skill set.

Two independent contracts are enforced:

1. `SkillInvocationContract` -- every script invocation documented in a shipped
   SKILL.md resolves to a real file.

   Two documented path forms are accepted in this distribution:

   a. Project-root relative -- ``python .agent/skills/<skill>/scripts/<file> ...``.
      Resolved against the distribution root (the directory that owns `.agent/`).
      This is the form used by ui-ux-pro-max, design and design-system so the
      command is unambiguous regardless of the working directory.
   b. Skill relative -- ``scripts/<file>`` for the skill's own scripts and
      ``../<skill>/scripts/<file>`` for a sibling sub-skill. Resolved against the
      directory containing the SKILL.md. This is the form used by brand,
      ui-styling and design-system, whose `## Script Paths` sections state the
      convention.

   No tool-specific variable form (`${CLAUDE_PLUGIN_ROOT}` or similar) is allowed:
   this set is deliberately tool independent.

2. `SkillDescriptionContract` -- every skill's `description` frontmatter follows
   the trigger contract defined in `rules/skill-trigger-routing.md` §E, so an
   agent can decide which skill to open from the description alone.
"""

import re
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]          # .../ui-ux-pro-max
SKILLS_ROOT = SKILL_DIR.parent                            # .../.agent/skills
DIST_ROOT = SKILLS_ROOT.parent.parent                     # directory that owns .agent/

INVOCATION = re.compile(
    r'(?<![\w/.-])(?:python3?|node|bash)\s+"?([^\s"`\'<]+\.(?:py|cjs|js|mjs|sh))'
)
TOOL_VARIABLE = re.compile(r'\$\{[A-Z_]+\}')
# Shell/CI variables are legitimate in prose and commands; only variables that
# denote a specific coding agent's installation root are a contract violation.
TOOL_SPECIFIC_VARIABLE = re.compile(
    r'\$\{(?:CLAUDE|CURSOR|CODEX|OPENCODE|WINDSURF|ANTIGRAVITY|ROOCODE|KILOCODE|QODER|DROID|ZCODE|CODEWHALE)[A-Z_]*\}'
)


def skill_dirs():
    return sorted(d for d in SKILLS_ROOT.iterdir() if (d / "SKILL.md").is_file())


def documented_invocations():
    for skill_dir in skill_dirs():
        for md in sorted(skill_dir.rglob("*.md")):
            for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
                for match in INVOCATION.finditer(line):
                    yield skill_dir, md, lineno, match.group(1)


def resolve(skill_dir, md, path):
    """Return (target, None) when the documented path resolves, else (None, reason)."""
    if TOOL_VARIABLE.search(path):
        return None, "tool-specific variable in path"
    if path.startswith(".agent/skills/"):
        return DIST_ROOT / path, None
    if path.startswith("scripts/"):
        return skill_dir / path, None
    if path.startswith("../"):
        parts = path.split("/")
        if len(parts) > 3 and parts[2] == "scripts" and (skill_dir.parent / parts[1]).is_dir():
            return skill_dir.parent / parts[1] / "/".join(parts[2:]), None
        return None, "a sibling invocation must be ../<skill>/scripts/<file> and the sibling must ship"
    return None, ("not resolvable (expected .agent/skills/<skill>/scripts/<file>, "
                  "scripts/<file> or ../<skill>/scripts/<file>)")


class SkillInvocationContract(unittest.TestCase):
    def test_every_documented_invocation_resolves(self):
        problems, seen = [], 0
        for skill_dir, md, lineno, path in documented_invocations():
            seen += 1
            target, reason = resolve(skill_dir, md, path)
            if reason is None and not target.is_file():
                reason = f"no such file: {target}"
            if reason:
                problems.append(f"{md.relative_to(DIST_ROOT)}:{lineno}: {path} -- {reason}")
        self.assertGreater(seen, 20, f"extractor found only {seen} invocations")
        self.assertEqual(problems, [], "\n" + "\n".join(problems))

    def test_no_tool_specific_variable_in_any_skill_markdown(self):
        offenders = []
        for skill_dir in skill_dirs():
            for md in sorted(skill_dir.rglob("*.md")):
                for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
                    if TOOL_SPECIFIC_VARIABLE.search(line):
                        offenders.append(f"{md.relative_to(DIST_ROOT)}:{lineno}: {line.strip()}")
        self.assertEqual(offenders, [], "\n" + "\n".join(offenders))


# --- description (trigger) contract -------------------------------------------
# rules/skill-trigger-routing.md §E

DESCRIPTION_MIN_WORDS = 25
DESCRIPTION_MAX_WORDS = 70
# Every description must state, in this exact wording, when NOT to use the skill.
NEGATIVE_TRIGGER_MARKER = "Tetiklenmez:"
POSITIVE_TRIGGER_MARKER = "Tetikleyiciler:"
TURKISH_MARKERS = ("Tetikleyiciler", "Tetiklenmez", "tetiklenir", "tetikleyici")
ENGLISH_MARKER = re.compile(r'"[a-z][a-z ]{3,}"')
DICTIONARY_REF = ".agent/rules/skill-trigger-routing.md"
DICTIONARY_RULE = DIST_ROOT / ".agent" / "rules" / "skill-trigger-routing.md"


def frontmatter(skill_md):
    """Return the frontmatter block of a SKILL.md as a single string."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    return text[3:end] if end != -1 else ""


def description_of(skill_md):
    """Return the `description` value, unwrapping YAML folded (`>-`) blocks."""
    block = frontmatter(skill_md)
    if not block:
        return None
    lines = block.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("description:"):
            continue
        value = line[len("description:"):].strip()
        if value in (">-", ">", "|", "|-"):
            parts = []
            for follow in lines[index + 1:]:
                if not follow.startswith(("  ", "\t")):
                    break
                parts.append(follow.strip())
            return " ".join(parts)
        if value.startswith(('"', "'")) and value.endswith(('"', "'")) and len(value) > 1:
            return value[1:-1]
        return value
    return None


def description_words(skill_dir):
    desc = description_of(skill_dir / "SKILL.md") or ""
    return len(desc.split())


class SkillDescriptionContract(unittest.TestCase):
    """rules/skill-trigger-routing.md §E -- every description is usable as a trigger."""

    def setUp(self):
        self.skills = skill_dirs()

    def test_every_skill_ships_a_description(self):
        missing = [d.name for d in self.skills if not description_of(d / "SKILL.md")]
        self.assertEqual(missing, [], f"skills without a description: {missing}")

    def test_description_length_within_budget(self):
        problems = [
            f"{d.name}: {description_words(d)} words "
            f"(allowed {DESCRIPTION_MIN_WORDS}-{DESCRIPTION_MAX_WORDS})"
            for d in self.skills
            if not DESCRIPTION_MIN_WORDS <= description_words(d) <= DESCRIPTION_MAX_WORDS
        ]
        self.assertEqual(problems, [], "\n" + "\n".join(problems))

    def test_description_has_positive_and_negative_triggers(self):
        problems = []
        for d in self.skills:
            desc = description_of(d / "SKILL.md") or ""
            if POSITIVE_TRIGGER_MARKER not in desc:
                problems.append(f"{d.name}: no '{POSITIVE_TRIGGER_MARKER}' section")
            if NEGATIVE_TRIGGER_MARKER not in desc:
                problems.append(f"{d.name}: no '{NEGATIVE_TRIGGER_MARKER}' statement")
        self.assertEqual(problems, [], "\n" + "\n".join(problems))

    def test_description_has_both_turkish_and_english_triggers(self):
        problems = []
        for d in self.skills:
            desc = description_of(d / "SKILL.md") or ""
            if not any(marker in desc for marker in TURKISH_MARKERS):
                problems.append(f"{d.name}: no Turkish trigger wording")
            if not ENGLISH_MARKER.search(desc):
                problems.append(f"{d.name}: no English trigger example")
        self.assertEqual(problems, [], "\n" + "\n".join(problems))

    def test_description_points_at_the_central_dictionary(self):
        problems = [
            d.name for d in self.skills
            if DICTIONARY_REF not in (description_of(d / "SKILL.md") or "")
        ]
        self.assertEqual(problems, [], f"descriptions without a dictionary reference: {problems}")

    def test_description_names_no_tool_and_no_project(self):
        forbidden = re.compile(
            r"Claude Code|Cursor\b|Windsurf|Codex|Copilot|\.mdc|"
            r"\bocai\b|FEProject|bookmarkManager|kalansure"
        )
        problems = []
        for d in self.skills:
            desc = description_of(d / "SKILL.md") or ""
            match = forbidden.search(desc)
            if match:
                problems.append(f"{d.name}: tool/project name {match.group(0)!r}")
        self.assertEqual(problems, [], "\n" + "\n".join(problems))

    def test_dictionary_exists_and_lists_every_skill(self):
        self.assertTrue(DICTIONARY_RULE.is_file(), f"missing dictionary: {DICTIONARY_RULE}")
        text = DICTIONARY_RULE.read_text(encoding="utf-8")
        missing = [d.name for d in self.skills if d.name not in text]
        self.assertEqual(missing, [], f"skills absent from the dictionary: {missing}")

    def test_every_dictionary_section_is_reachable(self):
        """Each table row in §A must point at a SKILL.md that actually ships."""
        text = DICTIONARY_RULE.read_text(encoding="utf-8")
        targets = re.findall(r"`skills/([a-z0-9-]+)/SKILL\.md`", text)
        self.assertGreater(len(targets), 10, "dictionary lost its skill targets")
        broken = sorted({t for t in targets if not (SKILLS_ROOT / t / "SKILL.md").is_file()})
        self.assertEqual(broken, [], f"dictionary points at missing skills: {broken}")


if __name__ == "__main__":
    unittest.main()
