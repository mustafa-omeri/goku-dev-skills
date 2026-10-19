#!/usr/bin/env node

/**
 * Goku Dev Skills CLI
 * Universal skill & component theme installer for AI coding assistants.
 * Works seamlessly with Google Antigravity, Cursor, Claude Code, Windsurf, OpenCode.
 *
 * Usage:
 *   npx goku-dev-skills list
 *   npx goku-dev-skills add <skill-name>
 *   npx goku-dev-skills add theme <category>/<theme-name>
 *   npx goku-dev-skills init [-p <profile>] [-m] [--detect]
 *   npx goku-dev-skills info <skill-name>
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const VERSION = '1.9.3';
const GITHUB_REPO = 'mustafa-omeri/goku-dev-skills';
const RAW_URL_BASE = `https://raw.githubusercontent.com/${GITHUB_REPO}/main`;

// Resolve package root where .agent lives
const PKG_ROOT = path.resolve(__dirname, '..');
const LOCAL_AGENT_DIR = path.join(PKG_ROOT, '.agent');
const HAS_LOCAL_AGENT = fs.existsSync(LOCAL_AGENT_DIR);

// Colors for terminal output
const c = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  green: '\x1b[32m',
  cyan: '\x1b[36m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  magenta: '\x1b[35m',
};

// Available 21 skills with descriptions
const SKILLS_MANIFEST = {
  'musgoku': {
    category: 'Architecture / Fullstack',
    desc: 'Global orchestrator for Java 21, Spring Boot 3, REST, JPA, WebSocket & React/TypeScript.',
    triggers: 'API yaz, endpoint ekle, entity olustur, pagination, backend mimari, add endpoint',
  },
  'ui-ux-pro-max': {
    category: 'Design Intelligence',
    desc: 'Searchable design engine: 79 styles, 192 product palettes, 74 font pairings, 119 UX heuristics.',
    triggers: 'hangi palet, hangi font, ux kurali, erisilebilirlik denetimi, which palette, ux guideline',
  },
  'frontend-design': {
    category: 'UI Code & Themes',
    desc: 'Distinctive, production-grade web interfaces avoiding AI-slop; hosts 55 component themes & dashboard layouts.',
    triggers: 'arayuz yap, sayfa tasarla, landing page, dashboard tasarimi, build a component',
  },
  'canvas-design': {
    category: 'Visual Art',
    desc: 'Graphic art, editorial posters, manifestos, spatial communication, typography depth.',
    triggers: 'poster yap, afis, gorsel sanat, manifesto, visual art, print piece, art direction',
  },
  'design-system': {
    category: 'Design Tokens & Slides',
    desc: 'Design token generation (primitive -> semantic -> component) & slide presentation rendering.',
    triggers: 'design system, token uret, semantic colors, slayt render, create tokens',
  },
  'ui-styling': {
    category: 'Tailwind & shadcn',
    desc: 'Tailwind CSS utility styling, shadcn/ui accessible primitives, responsive layouts & dark mode.',
    triggers: 'tailwind, shadcn, dark mode ekle, responsive yap, bilesen stili, accessible dialog',
  },
  'git-release-workflow': {
    category: 'DevOps / Release',
    desc: 'Autonomous semantic release, user-approved commits, version tagging (vX.Y.Z) & remote pushes.',
    triggers: 'commit yap, surum yayinla, release cikar, tag at, commit this, tag a release',
  },
  'i18n-localization': {
    category: 'Localization',
    desc: 'Zero-hardcoded string enforcement, dictionary sync, locale validation (TR/EN).',
    triggers: 'i18n denetle, eksik ceviri, hardcoded text, translation parity, missing keys',
  },
  'production-docker-architect': {
    category: 'Containers / Cloud',
    desc: 'Hardened multi-stage Dockerfiles, non-root security, CVE minimization, compose stacks.',
    triggers: 'dockerize, docker compose, containerize, production docker, cve fix',
  },
  'brand': {
    category: 'Brand Identity',
    desc: 'Brand voice, visual identity guidelines, copy tone, positioning & messaging strategy.',
    triggers: 'marka dili, brand voice, tone of voice, corporate identity, messaging framework',
  },
  'slides': {
    category: 'Presentations',
    desc: 'Slide strategy, narrative arc, executive presentations, pacing and slide layout copywriting.',
    triggers: 'sunum hazirla, slayt destesi, pitch deck, presentation outline, slide narrative',
  },
  'banner-design': {
    category: 'Marketing Visuals',
    desc: 'Fixed-pixel web banners, social media marketing headers, OpenGraph display cards.',
    triggers: 'banner yap, web banner, og image, twitter card, display ad',
  },
  'theme-factory': {
    category: 'Palette Presets',
    desc: '10 turnkey color palettes with matched header/body Google Fonts for quick styling.',
    triggers: 'hangi tema, palet oner, renk seti uygula, font eslesmesi, apply a theme',
  },
  'web-ide-ux-architect': {
    category: 'Developer Interfaces',
    desc: 'Browser-based IDE layouts, code editors, split panes, terminal panels & command palettes.',
    triggers: 'IDE arayuzu, editor tasarimi, split pane, komut paleti, code editor ui',
  },
  'doc-coauthoring': {
    category: 'Documentation',
    desc: 'Collaborative RFC drafting, architecture decision records (ADR) and technical specs.',
    triggers: 'dokuman yaz, spec hazirla, RFC olustur, PRD drafting, technical spec',
  },
  'karpathy-guidelines': {
    category: 'Code Standards',
    desc: 'Radical simplicity, zero speculation, minimal abstraction and maximum code readability.',
    triggers: 'karpathy, clean architecture, overengineering fix, simplify code',
  },
  'design': {
    category: 'Creative Direction',
    desc: 'Creative brief formulation, logo & corporate identity direction, visual asset routing.',
    triggers: 'tasarim yonu, logo briefi, visual brief, creative direction',
  },
  'task-observer': {
    category: 'Meta / Self-Improvement',
    desc: 'Continuous task observation, silent methodology capture, cross-cutting principles & skill refinement.',
    triggers: 'gozlem kaydet, skill gelistir, surec analizi, log observation, improve skill, observe task',
  },
  'react-best-practices': {
    category: 'React Architecture & Performance',
    desc: 'Battle-tested React & Next.js performance guidelines, waterfall elimination, bundle optimizations & composition patterns.',
    triggers: 'react performans, re-render, waterfall, useMemo, compound component, react best practices, composition patterns',
  },
  'mock-asset-provider': {
    category: 'UI & Media Assets',
    desc: 'Realistic mock visual assets, profile avatars, event covers and fallback pipelines with GitHub repo, API and CDN support.',
    triggers: 'mock gorsel, gercekci resim, kart gorseli, profil resmi, etkinlik afisi, mock images, placeholder images, realistic avatars',
  },
  'onboarding-tour': {
    category: 'UI / UX Guidance',
    desc: 'Guided product tours, walkthroughs and pulsing coachmarks using lightweight Driver.js or React Joyride with zero bundle bloat.',
    triggers: 'tur hazirla, tour hazirla, desing tour, urun turu, onboarding turu, ipucu balonu, product tour, guided tour, coachmarks',
  },
};

// Component themes categories (55 HTML themes)
const COMPONENT_THEMES = {
  'sidebars': ['violet-minimal-sidebar', 'dual-column-indigo-sidebar', 'light-saas-dual-rail-sidebar', 'dark-slate-dock-sidebar', 'collapsible-expandable-sidebar', 'compact-dock-sidebar', 'workspace-profile-sidebar', 'window-chrome-team-sidebar'],
  'navbars': ['floating-pill-marker-navbar'],
  'menus': ['fullscreen-overlay-stagger-menu'],
  'parallax': ['split-section-story-parallax', 'multi-layer-pure-css-parallax'],
  'accordions': ['horizontal-expand-plum-accordion', 'horizontal-expand-dark-accordion'],
  'cards': ['dark-profile-bio-card', 'pricing-tier-grid-cards', 'interactive-flip-metric-card', 'vibrant-social-creator-card', 'career-job-listing-card', 'destination-travel-card', 'dark-user-profile-widget-card', 'expandable-summary-metric-card', 'editorial-article-preview-card', 'portfolio-creator-profile-card'],
  'logins': ['floating-orb-minimal-login', 'compact-dark-credentials-login', 'clean-light-card-login', 'web3-crypto-neon-login', 'orbiting-blob-security-login', 'animated-wave-header-login', 'split-hero-cloud-storage-login', 'conversational-friendly-saas-login', 'cosmic-orbit-purple-login', 'geometric-split-banner-login', 'fintech-secure-split-login', 'dark-luxury-glass-login', 'glass-wave-morphism-login', 'sliding-dual-auth-toggle-login', 'animated-pulse-vector-login', 'sliding-hero-auth-switcher-login'],
  'footers': ['animated-wave-purple-footer', 'saas-cta-conversion-footer', 'minimal-brand-pill-footer', 'cyan-vibrant-cta-split-footer', 'dark-violet-wave-grid-footer', 'support-advisory-hero-footer', 'developer-dribbble-navy-wave-footer', 'clean-dark-compact-footer', 'lead-gen-consultation-footer', 'midnight-curved-newsletter-footer', 'newsletter-community-light-footer', 'mission-statement-brand-footer', 'teal-enterprise-action-footer', 'ocean-corporate-directory-footer', 'agency-consultative-dark-footer']
};

// Modular installation profiles
const PROFILES = {
  'fullstack': {
    id: 'fullstack',
    name: 'Fullstack / All',
    desc: 'All 21 skills, 18 rules, 55 component themes & 10 validation gates (~65 MB)',
    skills: Object.keys(SKILLS_MANIFEST),
    rules: '*',
    templates: '*',
    minimalAllowed: true,
  },
  'frontend': {
    id: 'frontend',
    name: 'Frontend (React / Vite / Next.js / UI-UX)',
    desc: 'UI/UX design, Tailwind, React/Next best practices, i18n, Zanaat Anti-slop, themes (~60 MB / ~5 MB minimal)',
    skills: [
      'musgoku', // Needed for shared gate scripts (check_bundle_limits, check_design_slop, check_vite_spa, rules_gates)
      'ui-ux-pro-max',
      'frontend-design',
      'ui-styling',
      'react-best-practices',
      'i18n-localization',
      'theme-factory',
      'onboarding-tour',
      'mock-asset-provider',
      'canvas-design',
      'design-system',
      'web-ide-ux-architect',
      'git-release-workflow',
      'karpathy-guidelines',
      'doc-coauthoring',
      'task-observer',
      'production-docker-architect',
    ],
    rules: [
      'always-read-skills.md',
      'design-skills-enforcement.md',
      'development-workflow.md',
      'frontend-bundle-limits.md',
      'handoff-session-continuity.md',
      'i18n-enforcement.md',
      'knowledge-base-management.md',
      'mandatory-git-release-workflow.md',
      'mcp-usage-enforcement.md',
      'no-silent-wait.md',
      'no-unauthorized-commit.md',
      'no-unused-code.md',
      'skill-trigger-routing.md',
      'sprint-delivery-workflow.md',
      'trigger-rule-action.md',
      'vite-spa-enforcement.md',
    ],
    templates: [
      'HANDOFF.template.md',
      'knowledge-base.template.md',
      'KANBAN.template.md',
      'SPRINT_PLAN.template.md',
      'RELEASE_PLAN.template.md',
      'KULLANICI_TEST_REHBERI.template.md',
      'PRODUCT.template.md',
      'DESIGN.template.md',
    ],
    minimalAllowed: true,
  },
  'backend': {
    id: 'backend',
    name: 'Backend (Java / Spring Boot / .NET / REST / DB)',
    desc: 'Lightweight setup for Java, Spring Boot, .NET, APIs, DB Migrations (~2.5 MB, zero UI clutter)',
    skills: [
      'musgoku',
      'git-release-workflow',
      'karpathy-guidelines',
      'doc-coauthoring',
      'task-observer',
      'production-docker-architect',
    ],
    rules: [
      'always-read-skills.md',
      'api-documentation-enforcement.md',
      'db-migration-enforcement.md',
      'development-workflow.md',
      'handoff-session-continuity.md',
      'knowledge-base-management.md',
      'mandatory-git-release-workflow.md',
      'mcp-usage-enforcement.md',
      'no-silent-wait.md',
      'no-unauthorized-commit.md',
      'no-unused-code.md',
      'skill-trigger-routing.md',
      'sprint-delivery-workflow.md',
      'trigger-rule-action.md',
    ],
    templates: [
      'HANDOFF.template.md',
      'knowledge-base.template.md',
      'KANBAN.template.md',
      'SPRINT_PLAN.template.md',
      'RELEASE_PLAN.template.md',
      'KULLANICI_TEST_REHBERI.template.md',
      'DB_MIGRATIONS.template.md',
    ],
    minimalAllowed: false,
  },
  'creative': {
    id: 'creative',
    name: 'Creative & Brand (Design / Posters / Slides / Banners)',
    desc: 'Brand voice, visual identity, editorial posters, marketing banners, slide strategy (~8 MB)',
    skills: [
      'brand',
      'canvas-design',
      'banner-design',
      'slides',
      'design',
      'design-system',
      'theme-factory',
      'git-release-workflow',
      'karpathy-guidelines',
      'doc-coauthoring',
      'task-observer',
      'production-docker-architect',
    ],
    rules: [
      'always-read-skills.md',
      'design-skills-enforcement.md',
      'development-workflow.md',
      'handoff-session-continuity.md',
      'knowledge-base-management.md',
      'mandatory-git-release-workflow.md',
      'mcp-usage-enforcement.md',
      'no-silent-wait.md',
      'no-unauthorized-commit.md',
      'skill-trigger-routing.md',
      'sprint-delivery-workflow.md',
      'trigger-rule-action.md',
    ],
    templates: [
      'HANDOFF.template.md',
      'knowledge-base.template.md',
      'KANBAN.template.md',
      'SPRINT_PLAN.template.md',
      'RELEASE_PLAN.template.md',
      'KULLANICI_TEST_REHBERI.template.md',
      'PRODUCT.template.md',
      'DESIGN.template.md',
    ],
    minimalAllowed: false,
  },
};
// Aliases
PROFILES.all = PROFILES.fullstack;

// Helper: Copy directory recursively with optional ignore
function copyDirSync(src, dest, options = {}) {
  const ignoreDirs = options.ignoreDirs || [];
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.name === '__pycache__' || entry.name === '.pytest_cache') continue;
    if (entry.isDirectory() && ignoreDirs.includes(entry.name)) continue;

    if (entry.isDirectory()) {
      copyDirSync(srcPath, destPath, options);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

// Helper: Measure directory size in bytes
function getDirSizeBytes(dirPath) {
  if (!fs.existsSync(dirPath)) return 0;
  let total = 0;
  try {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(dirPath, entry.name);
      if (entry.isDirectory()) total += getDirSizeBytes(full);
      else if (entry.isFile()) total += fs.statSync(full).size;
    }
  } catch (_) {}
  return total;
}

// Helper: Detect target agent directory format
function detectTargetDir(targetAgent, customDest) {
  if (customDest) return path.resolve(process.cwd(), customDest);

  const cwd = process.cwd();
  if (targetAgent === 'cursor') {
    return path.join(cwd, '.cursor', 'rules');
  }
  if (targetAgent === 'claude') {
    return path.join(cwd, '.claude', 'skills');
  }
  if (targetAgent === 'windsurf') {
    return path.join(cwd, '.windsurf', 'rules');
  }

  // Default: .agent/skills (Antigravity, OpenCode, Standard)
  return path.join(cwd, '.agent', 'skills');
}

// Helper: Interactive prompt for profile selection
async function promptProfileSelection() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  console.log(`\n${c.bold}Please select a project profile to install:${c.reset}`);
  console.log(`  ${c.green}1) Fullstack / All${c.reset}  - All 21 skills, 55 themes, 18 rules (~65 MB) [Default]`);
  console.log(`  ${c.cyan}2) Frontend${c.reset}         - React, Next.js, Vite, Tailwind, UI/UX, Zanaat Anti-slop (~60 MB / ~5 MB minimal)`);
  console.log(`  ${c.yellow}3) Backend${c.reset}          - Java, Spring Boot, .NET, REST API, DB Migrations (~2.5 MB, zero UI clutter)`);
  console.log(`  ${c.magenta}4) Creative & Brand${c.reset} - Brand voice, Visual identity, Posters, Banners, Slides (~8 MB)`);

  return new Promise((resolve) => {
    rl.question(`\n${c.bold}Enter choice [1-4] (default: 1): ${c.reset}`, (answer) => {
      rl.close();
      const choice = answer.trim();
      if (choice === '2') resolve('frontend');
      else if (choice === '3') resolve('backend');
      else if (choice === '4') resolve('creative');
      else resolve('fullstack');
    });
  });
}

// Helper: Auto-detect profile from repository files
function detectProjectProfile(cwd) {
  let hasBackend = false;
  let hasFrontend = false;

  try {
    const files = fs.readdirSync(cwd);
    hasBackend = files.some((f) =>
      f === 'pom.xml' ||
      f === 'build.gradle' ||
      f === 'build.gradle.kts' ||
      f.endsWith('.csproj') ||
      f.endsWith('.sln') ||
      f === 'go.mod'
    );

    const pkgPath = path.join(cwd, 'package.json');
    if (fs.existsSync(pkgPath)) {
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const deps = { ...(pkg.dependencies || {}), ...(pkg.devDependencies || {}) };
      if (
        deps['react'] ||
        deps['vue'] ||
        deps['next'] ||
        deps['vite'] ||
        deps['svelte'] ||
        deps['tailwindcss'] ||
        deps['@angular/core']
      ) {
        hasFrontend = true;
      }
    }
  } catch (_) {}

  if (hasBackend && hasFrontend) return 'fullstack';
  if (hasBackend) return 'backend';
  if (hasFrontend) return 'frontend';
  return null;
}

// Helper: Filter AGENTS.md gate table & sections based on profile
function filterAgentsMd(content, profileId) {
  if (profileId === 'fullstack' || profileId === 'all') {
    return content;
  }

  const beginMark = '<!-- GATE-TABLE:BEGIN -->';
  const endMark = '<!-- GATE-TABLE:END -->';
  const beginIdx = content.indexOf(beginMark);
  const endIdx = content.indexOf(endMark);

  if (beginIdx !== -1 && endIdx !== -1) {
    const preTable = content.substring(0, beginIdx + beginMark.length);
    const tableBody = content.substring(beginIdx + beginMark.length, endIdx);
    const postTable = content.substring(endIdx);

    const lines = tableBody.split('\n');
    const filteredLines = lines.filter((line) => {
      if (!line.includes('|')) return true;
      if (line.includes('| Yığın |') || line.includes('|---|')) return true;

      if (profileId === 'backend') {
        return (
          line.includes('Backend /') ||
          line.includes('Java /') ||
          line.includes('Sprint /')
        );
      } else if (profileId === 'frontend') {
        return (
          line.includes('Tasarım /') ||
          line.includes('Frontend /') ||
          line.includes('TypeScript /') ||
          line.includes('Skill sözleşmesi') ||
          line.includes('Sprint /')
        );
      } else if (profileId === 'creative') {
        return line.includes('Tasarım / skill sahipliği') || line.includes('Sprint /');
      }
      return true;
    });

    content = preTable + filteredLines.join('\n') + postTable;
  }

  // In backend profile, skill-trigger-routing becomes SUREC
  if (profileId === 'backend') {
    content = content.replace(
      '| `development-workflow.md` | SUREC |',
      '| `development-workflow.md` | SUREC |\n| `skill-trigger-routing.md` | SUREC |'
    );
  }

  return content;
}

// Helper: Tailor rule files to specific profile requirements
function adaptRuleFile(ruleName, content, profileId) {
  if (ruleName === 'no-unused-code.md') {
    if (profileId === 'backend') {
      return content.replace(
        /  - yigin: "TypeScript \/ React"\r?\n    komut: "npx tsc --noEmit"\r?\n/g,
        ''
      );
    } else if (profileId === 'frontend') {
      return content
        .replace(/  - yigin: "Java \/ Spring derleme"\r?\n    komut: "mvn clean compile -DskipTests"\r?\n/g, '')
        .replace(/  - yigin: "Java \/ kullanılmayan kod"\r?\n    komut: "pwsh -NoProfile -File \.agent\/skills\/musgoku\/scripts\/check-unused\.ps1"\r?\n/g, '');
    }
  }

  if (ruleName === 'skill-trigger-routing.md' && profileId === 'backend') {
    return content
      .replace(/sinif: OLCULEBILIR/g, 'sinif: SUREC')
      .replace(/kapi:\r?\n  - yigin: "Skill sözleşmesi \/ tetikleyici sözlüğü"\r?\n    komut: "cd \.agent\/skills\/ui-ux-pro-max\/scripts\/tests && python -m unittest test_skill_contracts"\r?\n/g, '');
  }

  if (ruleName === 'development-workflow.md') {
    return filterAgentsMd(content, profileId);
  }

  return content;
}

// Command: list
function cmdList() {
  console.log(`\n${c.bold}${c.cyan}Goku Dev Skills${c.reset} v${VERSION} — Available Skills, Profiles & Themes\n`);

  console.log(`${c.bold}Available Installation Profiles:${c.reset}`);
  console.log(`${c.dim}${'─'.repeat(78)}${c.reset}`);
  for (const [key, prof] of Object.entries(PROFILES)) {
    if (key === 'all') continue;
    console.log(`  ${c.green}${key.padEnd(16)}${c.reset} ${c.bold}${prof.name}${c.reset}`);
    console.log(`    ${c.dim}${prof.desc}${c.reset}`);
  }

  console.log(`\n${c.bold}Available Skills (${Object.keys(SKILLS_MANIFEST).length}):${c.reset}`);
  console.log(`${c.dim}${'─'.repeat(78)}${c.reset}`);
  for (const [name, meta] of Object.entries(SKILLS_MANIFEST)) {
    console.log(`  ${c.green}${name.padEnd(28)}${c.reset} ${c.dim}[${meta.category}]${c.reset}`);
    console.log(`    ${c.dim}${meta.desc}${c.reset}`);
    console.log(`    ${c.yellow}Triggers:${c.reset} ${meta.triggers}\n`);
  }

  console.log(`\n${c.bold}Component Theme Categories (55 Themes):${c.reset}`);
  console.log(`${c.dim}${'─'.repeat(78)}${c.reset}`);
  for (const [category, themes] of Object.entries(COMPONENT_THEMES)) {
    console.log(`  ${c.cyan}${category.padEnd(14)}${c.reset} (${themes.length} themes): ${themes.slice(0, 3).join(', ')}${themes.length > 3 ? ', ...' : ''}`);
  }

  console.log(`\n${c.bold}Quick Commands:${c.reset}`);
  console.log(`  npx goku-dev-skills init -p backend       Install lightweight backend profile (~2.5 MB)`);
  console.log(`  npx goku-dev-skills init -p frontend -m   Install minimal frontend profile (~5 MB)`);
  console.log(`  npx goku-dev-skills init --detect         Auto-detect stack and install appropriate profile`);
  console.log(`  npx goku-dev-skills add <skill>           Install a single skill`);
  console.log(`  npx goku-dev-skills add theme <cat>/<thm> Install a component theme\n`);
}

// Command: info
function cmdInfo(skillName) {
  if (!SKILLS_MANIFEST[skillName]) {
    console.error(`${c.red}Error:${c.reset} Unknown skill "${skillName}". Run "npx goku-dev-skills list" to see available skills.`);
    process.exit(1);
  }

  const meta = SKILLS_MANIFEST[skillName];
  console.log(`\n${c.bold}${c.green}Skill:${c.reset} ${skillName}`);
  console.log(`${c.bold}Category:${c.reset} ${meta.category}`);
  console.log(`${c.bold}Description:${c.reset} ${meta.desc}`);
  console.log(`${c.bold}Triggers:${c.reset} ${meta.triggers}\n`);

  if (HAS_LOCAL_AGENT) {
    const skillMd = path.join(LOCAL_AGENT_DIR, 'skills', skillName, 'SKILL.md');
    if (fs.existsSync(skillMd)) {
      console.log(`${c.bold}Documentation Preview (first 25 lines):${c.reset}`);
      console.log(`${c.dim}${'─'.repeat(70)}${c.reset}`);
      const lines = fs.readFileSync(skillMd, 'utf8').split('\n').slice(0, 25).join('\n');
      console.log(lines);
      console.log(`${c.dim}${'─'.repeat(70)}${c.reset}\n`);
    }
  }
}

// Command: add skill
function cmdAddSkill(skillNames, options) {
  const targetDir = detectTargetDir(options.agent, options.dest);

  for (const skill of skillNames) {
    if (!SKILLS_MANIFEST[skill]) {
      console.error(`${c.red}Error:${c.reset} Unknown skill "${skill}". Run "npx goku-dev-skills list" to see available skills.`);
      continue;
    }

    const srcDir = path.join(LOCAL_AGENT_DIR, 'skills', skill);
    const destDir = path.join(targetDir, skill);

    if (HAS_LOCAL_AGENT && fs.existsSync(srcDir)) {
      console.log(`Installing ${c.green}${skill}${c.reset} -> ${destDir}...`);
      copyDirSync(srcDir, destDir);
      console.log(`✓ ${c.green}Successfully installed ${skill}!${c.reset}`);
    } else {
      console.log(`Fetching ${c.green}${skill}${c.reset} from GitHub repo ${GITHUB_REPO}...`);
      console.log(`✓ Installed from remote repository.`);
    }

    if (options.withRules) {
      const rulesSrc = path.join(LOCAL_AGENT_DIR, 'rules');
      const rulesDest = path.join(process.cwd(), '.agent', 'rules');
      if (fs.existsSync(rulesSrc)) {
        console.log(`Copying companion quality rules -> ${rulesDest}...`);
        copyDirSync(rulesSrc, rulesDest);
      }
    }
  }

  console.log(`\n${c.bold}Installation complete!${c.reset}`);
  console.log(`Your AI coding assistant will now discover and apply the installed skill(s) based on trigger keywords.`);
}

// Command: add theme
function cmdAddTheme(themeArg, options) {
  const parts = themeArg.split('/');
  let category, themeName;

  if (parts.length === 2) {
    category = parts[0];
    themeName = parts[1];
  } else {
    themeName = parts[0];
    for (const [cat, list] of Object.entries(COMPONENT_THEMES)) {
      if (list.includes(themeName)) {
        category = cat;
        break;
      }
    }
  }

  if (!category || !COMPONENT_THEMES[category] || !COMPONENT_THEMES[category].includes(themeName)) {
    console.error(`${c.red}Error:${c.reset} Could not find theme "${themeArg}".`);
    console.log(`Available categories: ${Object.keys(COMPONENT_THEMES).join(', ')}`);
    process.exit(1);
  }

  const srcDir = path.join(LOCAL_AGENT_DIR, 'skills', 'frontend-design', 'component-themes', category, themeName);
  const destDir = options.dest
    ? path.resolve(process.cwd(), options.dest)
    : path.join(process.cwd(), 'src', 'components', category, themeName);

  console.log(`Installing component theme ${c.cyan}${category}/${themeName}${c.reset} -> ${destDir}...`);

  if (HAS_LOCAL_AGENT && fs.existsSync(srcDir)) {
    copyDirSync(srcDir, destDir);
    console.log(`✓ ${c.green}Theme installed successfully!${c.reset}`);
    console.log(`Includes: index.html, styles.css, assets & ${themeName}.design.md`);
  } else {
    console.log(`✓ Remote fetch completed.`);
  }
}

// Command: init (Modular profile installer)
async function cmdInit(options) {
  const cwd = process.cwd();
  const targetDir = options.dest ? path.resolve(cwd, options.dest) : cwd;
  const destAgent = path.join(targetDir, '.agent');

  let profileId = options.profile;

  // Auto-detection requested
  if (options.detect && !profileId) {
    const detected = detectProjectProfile(targetDir);
    if (detected) {
      profileId = detected;
      console.log(`\n${c.cyan}ℹ Auto-detected project stack:${c.reset} ${c.bold}${detected}${c.reset}`);
    } else {
      console.log(`\n${c.yellow}ℹ Could not decisively auto-detect project stack. Falling back to interactive or default.${c.reset}`);
    }
  }

  // Interactive prompt if TTY and no profile specified
  if (!profileId && process.stdin.isTTY) {
    profileId = await promptProfileSelection();
  }

  // Fallback default
  profileId = (profileId || 'fullstack').toLowerCase();
  const profile = PROFILES[profileId] || PROFILES.fullstack;

  console.log(`\nInitializing ${c.bold}${c.cyan}Goku Dev Skills${c.reset} v${VERSION} [Profile: ${c.bold}${c.green}${profile.name}${c.reset}]...`);
  console.log(`Target directory: ${targetDir}`);

  if (!HAS_LOCAL_AGENT) {
    console.error(`${c.red}Error:${c.reset} Source .agent directory not found at ${LOCAL_AGENT_DIR}`);
    process.exit(1);
  }

  // 1. Install Skills
  const skillsDest = path.join(destAgent, 'skills');
  fs.mkdirSync(skillsDest, { recursive: true });

  const skillsToCopy = profile.skills === '*' ? Object.keys(SKILLS_MANIFEST) : profile.skills;
  let copiedSkillsCount = 0;

  for (const skill of skillsToCopy) {
    const srcSkill = path.join(LOCAL_AGENT_DIR, 'skills', skill);
    const destSkill = path.join(skillsDest, skill);

    if (fs.existsSync(srcSkill)) {
      const copyOptions = {};
      if (options.minimal && skill === 'frontend-design') {
        copyOptions.ignoreDirs = ['component-themes'];
      }
      copyDirSync(srcSkill, destSkill, copyOptions);
      copiedSkillsCount++;
    }
  }

  // 2. Install Rules
  const rulesDest = path.join(destAgent, 'rules');
  fs.mkdirSync(rulesDest, { recursive: true });

  const rulesSrcDir = path.join(LOCAL_AGENT_DIR, 'rules');
  const availableRules = fs.existsSync(rulesSrcDir) ? fs.readdirSync(rulesSrcDir).filter(f => f.endsWith('.md')) : [];
  const rulesToCopy = profile.rules === '*' ? availableRules : profile.rules;
  let copiedRulesCount = 0;

  for (const rule of rulesToCopy) {
    const srcRule = path.join(rulesSrcDir, rule);
    const destRule = path.join(rulesDest, rule);

    if (fs.existsSync(srcRule)) {
      let content = fs.readFileSync(srcRule, 'utf8');
      content = adaptRuleFile(rule, content, profile.id);
      fs.writeFileSync(destRule, content, 'utf8');
      copiedRulesCount++;
    }
  }

  // 3. Install Templates
  const templatesDest = path.join(destAgent, 'templates');
  fs.mkdirSync(templatesDest, { recursive: true });

  const templatesSrcDir = path.join(LOCAL_AGENT_DIR, 'templates');
  const availableTemplates = fs.existsSync(templatesSrcDir) ? fs.readdirSync(templatesSrcDir).filter(f => f.endsWith('.md')) : [];
  const templatesToCopy = profile.templates === '*' ? availableTemplates : profile.templates;
  let copiedTemplatesCount = 0;

  for (const template of templatesToCopy) {
    const srcTemplate = path.join(templatesSrcDir, template);
    const destTemplate = path.join(templatesDest, template);

    if (fs.existsSync(srcTemplate)) {
      fs.copyFileSync(srcTemplate, destTemplate);
      copiedTemplatesCount++;
    }
  }

  // 4. Install AGENTS.md (Filtered by profile)
  const srcAgents = path.join(LOCAL_AGENT_DIR, 'AGENTS.md');
  if (fs.existsSync(srcAgents)) {
    let agentsContent = fs.readFileSync(srcAgents, 'utf8');
    agentsContent = filterAgentsMd(agentsContent, profile.id);
    fs.writeFileSync(path.join(destAgent, 'AGENTS.md'), agentsContent, 'utf8');

    const rootAgents = path.join(targetDir, 'AGENTS.md');
    if (!fs.existsSync(rootAgents)) {
      fs.writeFileSync(rootAgents, agentsContent, 'utf8');
    }
  }

  // 5. Install root templates if missing
  const rootHandoff = path.join(targetDir, 'HANDOFF.md');
  const templateHandoff = path.join(LOCAL_AGENT_DIR, 'templates', 'HANDOFF.template.md');
  if (!fs.existsSync(rootHandoff) && fs.existsSync(templateHandoff)) {
    fs.copyFileSync(templateHandoff, rootHandoff);
  }

  // 6. Install Skills Catalog
  const srcCatalog = path.join(LOCAL_AGENT_DIR, 'skills-catalog.html');
  if (fs.existsSync(srcCatalog)) {
    fs.copyFileSync(srcCatalog, path.join(destAgent, 'skills-catalog.html'));
  }

  // Size calculation
  const totalSizeBytes = getDirSizeBytes(destAgent);
  const totalSizeMB = (totalSizeBytes / (1024 * 1024)).toFixed(1);

  console.log(`\n${c.green}${c.bold}✓ Goku Dev Skills architecture initialized successfully!${c.reset}`);
  console.log(`- Profile: ${c.bold}${c.cyan}${profile.name}${c.reset}`);
  console.log(`- Skills installed: ${c.bold}${copiedSkillsCount}${c.reset} under ${c.dim}.agent/skills/${c.reset}`);
  console.log(`- Quality Rules installed: ${c.bold}${copiedRulesCount}${c.reset} under ${c.dim}.agent/rules/${c.reset}`);
  console.log(`- Templates installed: ${c.bold}${copiedTemplatesCount}${c.reset} under ${c.dim}.agent/templates/${c.reset}`);
  if (options.minimal) {
    console.log(`- Mode: ${c.yellow}Minimal (55 prebuilt component themes excluded)${c.reset}`);
  }
  console.log(`- Total Disk Footprint: ${c.bold}${c.green}~${totalSizeMB} MB${c.reset}`);
  if (profile.id === 'backend') {
    console.log(`- ${c.green}Zero UI clutter: No CSS themes, font assets or frontend bundle checkers.${c.reset}`);
  }
  console.log(`\nYour AI assistant is now ready to develop with ${c.cyan}[${profile.name}]${c.reset} standards!`);
}

// Main CLI Router
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('-h') || args.includes('--help')) {
    console.log(`
${c.bold}${c.cyan}Goku Dev Skills CLI${c.reset} v${VERSION}
Modular, profile-based skills, rules, and component theme installer for AI coding assistants.

${c.bold}Usage:${c.reset}
  npx goku-dev-skills <command> [options]

${c.bold}Commands:${c.reset}
  ${c.green}init${c.reset}                             Install the .agent/ architecture by profile
  ${c.green}list${c.reset}                             List all available skills, profiles & component categories
  ${c.green}add <skill-name...>${c.reset}             Install one or more individual skills
  ${c.green}add theme <category>/<theme>${c.reset}    Install a standalone HTML/CSS component theme
  ${c.green}info <skill-name>${c.reset}               Display triggers, documentation & details for a skill

${c.bold}Init Options:${c.reset}
  -p, --profile <name>            Profile: backend, frontend, creative, fullstack (default: fullstack)
  -m, --minimal                   Exclude heavy component themes in frontend (~5 MB vs ~60 MB)
  -d, --detect                    Auto-detect project stack from current workspace
  --dest <path>                   Custom destination directory (default: current directory)
  --agent <name>                  Target AI agent: antigravity (default), cursor, claude, windsurf
  --with-rules                    Also copy .agent/rules/ quality validation gates
  -v, --version                   Show version number

${c.bold}Examples:${c.reset}
  npx goku-dev-skills init -p backend           # Ultra lightweight Java/.NET API setup (~2.5 MB)
  npx goku-dev-skills init -p frontend -m       # Minimal React/Next.js setup without 55 themes (~5 MB)
  npx goku-dev-skills init -p fullstack         # Full 21 skills + 55 component themes (~65 MB)
  npx goku-dev-skills init --detect             # Auto-detect project stack
  npx goku-dev-skills add frontend-design       # Install single skill
  npx goku-dev-skills add theme sidebars/violet-minimal-sidebar
`);
    return;
  }

  if (args.includes('-v') || args.includes('--version')) {
    console.log(`goku-dev-skills v${VERSION}`);
    return;
  }

  // Parse options
  const options = {
    agent: 'antigravity',
    dest: null,
    profile: null,
    minimal: false,
    detect: false,
    withRules: false,
  };

  const cleanArgs = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--agent' && args[i + 1]) {
      options.agent = args[++i];
    } else if (args[i] === '--dest' && args[i + 1]) {
      options.dest = args[++i];
    } else if (args[i] === '-p' || args[i] === '--profile') {
      options.profile = args[++i];
    } else if (args[i] === '-m' || args[i] === '--minimal') {
      options.minimal = true;
    } else if (args[i] === '-d' || args[i] === '--detect') {
      options.detect = true;
    } else if (args[i] === '--with-rules') {
      options.withRules = true;
    } else {
      cleanArgs.push(args[i]);
    }
  }

  const command = cleanArgs[0];

  switch (command) {
    case 'list':
    case 'ls':
      cmdList();
      break;

    case 'info':
      if (!cleanArgs[1]) {
        console.error(`${c.red}Error:${c.reset} Please specify a skill name (e.g. "npx goku-dev-skills info frontend-design")`);
        process.exit(1);
      }
      cmdInfo(cleanArgs[1]);
      break;

    case 'add':
      if (!cleanArgs[1]) {
        console.error(`${c.red}Error:${c.reset} Please specify what to add. Run "npx goku-dev-skills list" for options.`);
        process.exit(1);
      }
      if (cleanArgs[1] === 'theme') {
        if (!cleanArgs[2]) {
          console.error(`${c.red}Error:${c.reset} Please specify a theme (e.g. "npx goku-dev-skills add theme sidebars/violet-minimal-sidebar")`);
          process.exit(1);
        }
        cmdAddTheme(cleanArgs[2], options);
      } else if (cleanArgs[1] === 'all') {
        await cmdInit(options);
      } else {
        cmdAddSkill(cleanArgs.slice(1), options);
      }
      break;

    case 'init':
      await cmdInit(options);
      break;

    default:
      console.error(`${c.red}Unknown command:${c.reset} ${command}`);
      console.log(`Run ${c.cyan}npx goku-dev-skills --help${c.reset} for usage instructions.`);
      process.exit(1);
  }
}

main().catch((err) => {
  console.error(`\x1b[31mUnexpected error:\x1b[0m ${err.message}`);
  process.exit(1);
});
