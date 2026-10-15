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
 *   npx goku-dev-skills init
 *   npx goku-dev-skills info <skill-name>
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const VERSION = '1.3.1';
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

// Available 18 skills with descriptions
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
  'musgoku-prd': {
    category: 'Compliance / Spec',
    desc: 'Product requirement documents with integrated KVKK / GDPR data privacy compliance checks.',
    triggers: 'PRD hazirla, KVKK denetimi, privacy compliance, feature spec',
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
};

// Component themes categories
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

// Helper: Copy directory recursively
function copyDirSync(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.name === '__pycache__' || entry.name === '.pytest_cache') continue;

    if (entry.isDirectory()) {
      copyDirSync(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
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

// Command: list
function cmdList() {
  console.log(`\n${c.bold}${c.cyan}Goku Dev Skills${c.reset} v${VERSION} — Available Skills & Themes\n`);
  console.log(`${c.bold}Available Skills (${Object.keys(SKILLS_MANIFEST).length}):${c.reset}`);
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
  console.log(`  npx goku-dev-skills add <skill>           Install a skill (e.g. frontend-design)`);
  console.log(`  npx goku-dev-skills add theme <cat>/<thm> Install a component theme`);
  console.log(`  npx goku-dev-skills init                  Install full .agent/ architecture\n`);
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

    // Copy rules if requested
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
    // Search across categories
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

// Command: init
function cmdInit(options) {
  const cwd = process.cwd();
  const destAgent = path.join(cwd, '.agent');

  console.log(`\nInitializing ${c.bold}${c.cyan}Goku Dev Skills${c.reset} full architecture in ${cwd}...`);

  if (HAS_LOCAL_AGENT) {
    copyDirSync(LOCAL_AGENT_DIR, destAgent);
    console.log(`✓ Created ${destAgent}`);
  }

  // Ensure root templates if missing
  const agentsMdDest = path.join(cwd, 'AGENTS.md');
  const handoffMdDest = path.join(cwd, 'HANDOFF.md');

  if (!fs.existsSync(agentsMdDest) && HAS_LOCAL_AGENT) {
    const srcAgents = path.join(LOCAL_AGENT_DIR, 'AGENTS.md');
    if (fs.existsSync(srcAgents)) fs.copyFileSync(srcAgents, agentsMdDest);
  }

  if (!fs.existsSync(handoffMdDest) && HAS_LOCAL_AGENT) {
    const templateHandoff = path.join(LOCAL_AGENT_DIR, 'templates', 'HANDOFF.template.md');
    if (fs.existsSync(templateHandoff)) fs.copyFileSync(templateHandoff, handoffMdDest);
  }

  console.log(`\n${c.green}${c.bold}Goku Dev Skills architecture successfully initialized!${c.reset}`);
  // Sayilar diskten olculur; elle yazilan sayi kural eklendikce bayatlar
  // (16 -> 17 oldugunda ekranda yanlis bilgi gosterdi).
  const countRules = () => {
    try {
      return fs.readdirSync(path.join(LOCAL_AGENT_DIR, 'rules'))
        .filter((f) => f.endsWith('.md')).length;
    } catch (_) { return '?'; }
  };
  // Biri tema = bir HTML bileseni. Klasor sayisi degil, dosya sayilir:
  // 8 klasor icinde 55 bilesen var (neden: tek klasorde birden fazla tema).
  const countThemes = () => {
    const base = path.join(LOCAL_AGENT_DIR, 'skills', 'frontend-design', 'component-themes');
    let total = 0;
    try {
      for (const entry of fs.readdirSync(base, { withFileTypes: true })) {
        if (entry.isDirectory()) {
          const stack = [path.join(base, entry.name)];
          while (stack.length) {
            const dir = stack.pop();
            for (const child of fs.readdirSync(dir, { withFileTypes: true })) {
              if (child.isDirectory()) stack.push(path.join(dir, child.name));
              else if (child.name.endsWith('.html')) total++;
            }
          }
        } else if (entry.name.endsWith('.html')) {
          total++;
        }
      }
    } catch (_) { return '?'; }
    return total;
  };

  console.log(`- ${Object.keys(SKILLS_MANIFEST).length} Production Skills available under ${c.cyan}.agent/skills/${c.reset}`);
  console.log(`- ${countRules()} Quality Rules & Validation Gates available under ${c.cyan}.agent/rules/${c.reset}`);
  console.log(`- ${countThemes()} Component Themes under ${c.cyan}.agent/skills/frontend-design/component-themes/${c.reset}`);
}

// Main CLI Router
function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('-h') || args.includes('--help')) {
    console.log(`
${c.bold}${c.cyan}Goku Dev Skills CLI${c.reset} v${VERSION}
Install battle-tested skills, rules, and component themes into any project.

${c.bold}Usage:${c.reset}
  npx goku-dev-skills <command> [options]

${c.bold}Commands:${c.reset}
  ${c.green}list${c.reset}                             List all available skills & component categories
  ${c.green}add <skill-name...>${c.reset}             Install one or more skills into your workspace
  ${c.green}add theme <category>/<theme>${c.reset}    Install a standalone HTML/CSS component theme
  ${c.green}init${c.reset}                             Install the complete .agent/ architecture
  ${c.green}info <skill-name>${c.reset}               Display triggers, documentation & details for a skill

${c.bold}Options:${c.reset}
  --agent <name>                  Target AI agent: antigravity (default), cursor, claude, windsurf
  --dest <path>                   Custom destination directory
  --with-rules                    Also copy .agent/rules/ quality validation gates
  -v, --version                   Show version number

${c.bold}Examples:${c.reset}
  npx goku-dev-skills list
  npx goku-dev-skills add frontend-design ui-ux-pro-max
  npx goku-dev-skills add musgoku --agent cursor
  npx goku-dev-skills add theme sidebars/violet-minimal-sidebar
  npx goku-dev-skills init
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
    withRules: false,
  };

  const cleanArgs = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--agent' && args[i + 1]) {
      options.agent = args[++i];
    } else if (args[i] === '--dest' && args[i + 1]) {
      options.dest = args[++i];
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
        cmdInit(options);
      } else {
        cmdAddSkill(cleanArgs.slice(1), options);
      }
      break;

    case 'init':
      cmdInit(options);
      break;

    default:
      console.error(`${c.red}Unknown command:${c.reset} ${command}`);
      console.log(`Run ${c.cyan}npx goku-dev-skills --help${c.reset} for usage instructions.`);
      process.exit(1);
  }
}

main();
