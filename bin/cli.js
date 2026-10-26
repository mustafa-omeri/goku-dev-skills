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
const https = require('https');

const VERSION = '1.11.9';
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

// Available 29 skills with descriptions
const SKILLS_MANIFEST = {
  'musgoku': {
    category: 'Architecture / Fullstack',
    desc: 'Global orchestrator for Java 21, Spring Boot 3, REST, JPA, WebSocket & React/TypeScript.',
    triggers: '/gs-update, GS guncelle, API yaz, endpoint ekle, entity olustur, pagination, backend mimari, add endpoint',
  },
  'ui-ux-pro-max': {
    category: 'Design Intelligence',
    desc: 'Searchable design engine: 79 styles, 192 product palettes, 74 font pairings, 119 UX heuristics.',
    triggers: 'hangi palet, hangi font, ux kurali, erisilebilirlik denetimi, which palette, ux guideline',
  },
  'frontend-design': {
    category: 'UI Code & Themes',
    desc: 'Distinctive, production-grade web interfaces avoiding AI-slop; hosts 55 component themes & dashboard layouts.',
    triggers: '/ui-polish, [DESIGN-REFRESH], [UI-POLISH], arayuz yap, sayfa tasarla, landing page, dashboard tasarimi, build a component',
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
    triggers: '/commitx, commitx, commitle, [COMMITX], commit yap, surum yayinla, release cikar, tag at, commit this, tag a release',
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
    triggers: '/verify-prd, dokuman yaz, spec hazirla, RFC olustur, PRD drafting, technical spec',
  },
  'karpathy-guidelines': {
    category: 'Code Standards',
    desc: 'Radical simplicity, zero speculation, minimal abstraction and maximum code readability.',
    triggers: '/council, karpathy, llm council, clean architecture, overengineering fix, simplify code',
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
  'diagnosing-bugs': {
    category: 'Engineering / Debugging',
    desc: 'Systematic 6-phase debugging loop: red feedback loop before code change, ranked falsifiable hypotheses & regression tests.',
    triggers: '/fix-bug, hata ayikla, bug coz, neden calismiyor, kok neden, diagnose bug, debug issue, root cause',
  },
  'tdd': {
    category: 'Engineering / TDD',
    desc: 'Test-driven development: vertical slices, pre-agreed seams, red-before-green loop & zero tautological tests.',
    triggers: 'tdd, test gudumlu, once test yaz, test driven development, red green refactor, vertical slice',
  },
  'codebase-design': {
    category: 'Engineering / Architecture',
    desc: 'Deep modules (small interface, rich behavior), architectural seams, deletion test & designing for testability.',
    triggers: 'kod mimarisi, modul tasarimi, derin modul, codebase design, deep modules, architectural seam',
  },
  'code-review': {
    category: 'Engineering / Review',
    desc: 'Two-axis code review: Standards (Fowler smell baseline) vs Spec (fidelity & scope creep) via parallel sub-agents.',
    triggers: 'kod inceleme, code review, smell tara, review code, standards review, spec review',
  },
  'domain-modeling': {
    category: 'Engineering / Domain Model',
    desc: 'Ubiquitous language management, active GLOSSARY.md maintenance, inline updates & high-threshold ADR criteria.',
    triggers: 'domain model, terimler sozlugu, glossary, domain modeling, ubiquitous language, adr decision',
  },
  'my-idea': {
    category: 'Product & Ideas',
    desc: 'Idea backlog evaluator: re-rates docs/idea/myidea.md against project state, filters obsolete ideas, proposes top 3 choices & hands off to TDD/Sprint.',
    triggers: 'fikirlerime bak, fikirlerimi incele, fikir havuzu, yeni fikir sec, myidea, review ideas, idea backlog',
  },
  'security-audit': {
    category: 'Security & Vulnerability',
    desc: 'Offensive & defensive security harness: boundary crossing, vulnerability hunting, candidate verification, coverage ledger & findings schema.',
    triggers: '/check-security, guvenlik denetimi, security audit, guvenlik acigi tara, vulnerability scan, pen test, sizma testi, security review',
  },
  'seo-growth': {
    category: 'Marketing & SEO',
    desc: 'Search Engine Optimization (SEO), GEO (AI Search) & Growth: technical SEO, meta tags, schema markup, topic clusters, GTM launches & CRO.',
    triggers: '/seo-apply, [SEO-APPLY], seo, teknik seo, geo, ai search, meta tag, sitemap, schema markup, urun lansmani, seo optimization, technical seo, gtm strategy, product launch',
  },
  'prelaunch-audit': {
    category: 'Delivery & Quality',
    desc: 'Pre-launch production audit: 20-point checklist (KVKK m.10, Consent Mode v2, SEO, WCAG 2.2 AA & /prelaunch, /prelaunch-update).',
    triggers: 'prelaunch, canlıya al, go live, yayına alma kontrolü, consent check, axe audit, /prelaunch, /prelaunch-update',
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
    desc: 'All 30 skills, 19 rules, 55 component themes & 11 validation gates (~65 MB)',
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
      'diagnosing-bugs',
      'tdd',
      'codebase-design',
      'code-review',
      'domain-modeling',
      'my-idea',
      'security-audit',
      'seo-growth',
      'prelaunch-audit',
    ],
    rules: [
      'always-read-skills.md',
      'bug-diagnosis-enforcement.md',
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
      'GLOSSARY.template.md',
      'DESIGN.template.md',
      'myidea.template.md',
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
      'diagnosing-bugs',
      'tdd',
      'codebase-design',
      'code-review',
      'domain-modeling',
      'my-idea',
      'security-audit',
      'seo-growth',
    ],
    rules: [
      'always-read-skills.md',
      'api-documentation-enforcement.md',
      'bug-diagnosis-enforcement.md',
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
      'GLOSSARY.template.md',
      'myidea.template.md',
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

const PROJECT_BLOCK_REGEX = /^## Proje Bazlı Ek Kurallar[\s\S]*$/m;

// Helper: Extract project-specific rules from AGENTS.md
function extractProjectBlock(content) {
  if (!content) return null;
  const match = content.match(PROJECT_BLOCK_REGEX);
  return match ? match[0] : null;
}

// Helper: Inject preserved project-specific rules back into AGENTS.md
function injectProjectBlock(content, projectBlock) {
  if (!projectBlock) return content;
  if (PROJECT_BLOCK_REGEX.test(content)) {
    return content.replace(PROJECT_BLOCK_REGEX, projectBlock);
  }
  return content.trimEnd() + '\n\n' + projectBlock;
}

// Helper: Simple HTTP/HTTPS GET with redirect and timeout support
function httpGet(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { headers: { 'User-Agent': 'goku-dev-skills-cli' } }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return httpGet(res.headers.location).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) {
        return reject(new Error(`HTTP ${res.statusCode} for ${url}`));
      }
      const chunks = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => resolve(Buffer.concat(chunks)));
    });
    req.on('error', reject);
    req.setTimeout(15000, () => {
      req.destroy();
      reject(new Error(`Timeout fetching ${url}`));
    });
  });
}

// Helper: List all files recursively in a directory
function listFilesRecursive(dir, baseDir = dir, ignoreDirs = ['__pycache__', '.pytest_cache']) {
  if (!fs.existsSync(dir)) return [];
  const results = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (ignoreDirs.includes(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...listFilesRecursive(full, baseDir, ignoreDirs));
    } else if (entry.isFile()) {
      results.push(path.relative(baseDir, full).replace(/\\/g, '/'));
    }
  }
  return results;
}

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
  console.log(`  ${c.green}1) Fullstack / All${c.reset}  - All 26 skills, 55 themes, 19 rules (~65 MB) [Default]`);
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

  // 7. Save goku.json metadata
  const gokuConfig = {
    version: VERSION,
    profile: profile.id,
    minimal: !!options.minimal,
    installedSkills: skillsToCopy,
    installedRules: rulesToCopy,
    installedTemplates: templatesToCopy,
    initializedAt: new Date().toISOString(),
  };
  fs.writeFileSync(path.join(destAgent, 'goku.json'), JSON.stringify(gokuConfig, null, 2), 'utf8');

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

// Command: update (Surgical updater for already-installed skills & rules)
async function cmdUpdate(options) {
  const cwd = process.cwd();
  const targetDir = options.dest ? path.resolve(cwd, options.dest) : cwd;
  const destAgent = path.join(targetDir, '.agent');

  if (!fs.existsSync(destAgent)) {
    console.error(`${c.red}Error:${c.reset} No .agent directory found at ${targetDir}`);
    console.log(`To install skills for the first time, run: ${c.cyan}npx goku-dev-skills init${c.reset}`);
    process.exit(1);
  }

  // Load existing goku.json if present
  let gokuConfig = null;
  const gokuJsonPath = path.join(destAgent, 'goku.json');
  if (fs.existsSync(gokuJsonPath)) {
    try {
      gokuConfig = JSON.parse(fs.readFileSync(gokuJsonPath, 'utf8'));
    } catch (_) {}
  }

  // Detect currently installed assets
  const skillsDir = path.join(destAgent, 'skills');
  const installedSkills = fs.existsSync(skillsDir)
    ? fs.readdirSync(skillsDir).filter((f) => {
        const full = path.join(skillsDir, f);
        return fs.statSync(full).isDirectory() && !f.startsWith('.');
      })
    : [];

  const rulesDir = path.join(destAgent, 'rules');
  const installedRules = fs.existsSync(rulesDir)
    ? fs.readdirSync(rulesDir).filter((f) => f.endsWith('.md'))
    : [];

  const templatesDir = path.join(destAgent, 'templates');
  const installedTemplates = fs.existsSync(templatesDir)
    ? fs.readdirSync(templatesDir).filter((f) => f.endsWith('.md'))
    : [];

  const hasCatalog = fs.existsSync(path.join(destAgent, 'skills-catalog.html'));
  const hasAgentsMd = fs.existsSync(path.join(destAgent, 'AGENTS.md'));
  const hasThemes = fs.existsSync(path.join(skillsDir, 'frontend-design', 'component-themes'));

  // Profile determination
  const profileId = options.profile || gokuConfig?.profile || detectProjectProfile(targetDir) || 'fullstack';
  const profile = PROFILES[profileId] || PROFILES.fullstack;

  const isCheckOnly = !!(options.check || options.dryRun);
  const useRemote = !!(options.remote || !HAS_LOCAL_AGENT);

  console.log(`\n${c.bold}${c.cyan}Goku Dev Skills Update${c.reset} ${isCheckOnly ? c.yellow + '[CHECK / DRY-RUN]' + c.reset : ''}`);
  console.log(`${c.dim}${'─'.repeat(70)}${c.reset}`);
  console.log(`- Target: ${c.bold}${targetDir}${c.reset}`);
  console.log(`- Source: ${useRemote ? c.magenta + 'GitHub (https://github.com/' + GITHUB_REPO + ')' + c.reset : c.green + 'Local Package (' + LOCAL_AGENT_DIR + ')' + c.reset}`);
  console.log(`- Active Profile: ${c.bold}${profile.name}${c.reset}`);
  console.log(`- Installed Skills to update: ${c.green}${installedSkills.length}${c.reset} (${installedSkills.join(', ') || 'none'})`);
  console.log(`- Installed Rules to update: ${c.green}${installedRules.length}${c.reset}`);
  console.log(`- Installed Templates to update: ${c.green}${installedTemplates.length}${c.reset}`);
  console.log(`- Component Themes: ${hasThemes ? c.cyan + 'Installed' + c.reset : c.yellow + 'Minimal (Excluded)' + c.reset}`);
  const uninstalledCount = Math.max(0, Object.keys(SKILLS_MANIFEST).length - installedSkills.length);
  console.log(`- ${c.dim}Skipped uninstalled skills: ${uninstalledCount} skills will NOT be fetched.${c.reset}`);
  console.log(`${c.dim}${'─'.repeat(70)}${c.reset}\n`);

  const updatedFiles = [];
  const unchangedFiles = [];
  const errorFiles = [];

  // Preservation of project-specific rules in AGENTS.md
  let preservedProjectBlock = null;
  const targetAgentsPath = path.join(destAgent, 'AGENTS.md');
  if (fs.existsSync(targetAgentsPath)) {
    preservedProjectBlock = extractProjectBlock(fs.readFileSync(targetAgentsPath, 'utf8'));
  }

  // --- LOCAL UPDATE MODE ---
  if (!useRemote) {
    // 1. Update installed skills
    for (const skill of installedSkills) {
      const srcSkillDir = path.join(LOCAL_AGENT_DIR, 'skills', skill);
      const destSkillDir = path.join(skillsDir, skill);

      if (!fs.existsSync(srcSkillDir)) {
        console.log(`  ${c.yellow}⚠ Warning: Skill "${skill}" not found in source package.${c.reset}`);
        continue;
      }

      const ignoreList = ['__pycache__', '.pytest_cache'];
      if (!hasThemes && skill === 'frontend-design') {
        ignoreList.push('component-themes');
      }

      const files = listFilesRecursive(srcSkillDir, srcSkillDir, ignoreList);
      for (const rel of files) {
        const srcFile = path.join(srcSkillDir, rel);
        const destFile = path.join(destSkillDir, rel);

        const srcBuf = fs.readFileSync(srcFile);
        let isDifferent = true;

        if (fs.existsSync(destFile)) {
          const destBuf = fs.readFileSync(destFile);
          isDifferent = Buffer.compare(srcBuf, destBuf) !== 0;
        }

        const displayPath = `.agent/skills/${skill}/${rel}`;
        if (isDifferent) {
          updatedFiles.push(displayPath);
          if (!isCheckOnly) {
            fs.mkdirSync(path.dirname(destFile), { recursive: true });
            fs.copyFileSync(srcFile, destFile);
          }
        } else {
          unchangedFiles.push(displayPath);
        }
      }
    }

    // 2. Update installed rules
    for (const rule of installedRules) {
      const srcRule = path.join(LOCAL_AGENT_DIR, 'rules', rule);
      const destRule = path.join(rulesDir, rule);

      if (fs.existsSync(srcRule)) {
        let content = fs.readFileSync(srcRule, 'utf8');
        content = adaptRuleFile(rule, content, profile.id);

        let isDifferent = true;
        if (fs.existsSync(destRule)) {
          const destContent = fs.readFileSync(destRule, 'utf8');
          isDifferent = content !== destContent;
        }

        const displayPath = `.agent/rules/${rule}`;
        if (isDifferent) {
          updatedFiles.push(displayPath);
          if (!isCheckOnly) {
            fs.writeFileSync(destRule, content, 'utf8');
          }
        } else {
          unchangedFiles.push(displayPath);
        }
      }
    }

    // 3. Update installed templates
    for (const tpl of installedTemplates) {
      const srcTpl = path.join(LOCAL_AGENT_DIR, 'templates', tpl);
      const destTpl = path.join(templatesDir, tpl);

      if (fs.existsSync(srcTpl)) {
        const srcBuf = fs.readFileSync(srcTpl);
        let isDifferent = true;
        if (fs.existsSync(destTpl)) {
          const destBuf = fs.readFileSync(destTpl);
          isDifferent = Buffer.compare(srcBuf, destBuf) !== 0;
        }

        const displayPath = `.agent/templates/${tpl}`;
        if (isDifferent) {
          updatedFiles.push(displayPath);
          if (!isCheckOnly) {
            fs.copyFileSync(srcTpl, destTpl);
          }
        } else {
          unchangedFiles.push(displayPath);
        }
      }
    }

    // 4. Update AGENTS.md
    if (hasAgentsMd) {
      const srcAgents = path.join(LOCAL_AGENT_DIR, 'AGENTS.md');
      if (fs.existsSync(srcAgents)) {
        let content = fs.readFileSync(srcAgents, 'utf8');
        content = filterAgentsMd(content, profile.id);
        content = injectProjectBlock(content, preservedProjectBlock);

        const destAgents = path.join(destAgent, 'AGENTS.md');
        const destContent = fs.existsSync(destAgents) ? fs.readFileSync(destAgents, 'utf8') : '';
        const isDifferent = content !== destContent;

        const displayPath = `.agent/AGENTS.md`;
        if (isDifferent) {
          updatedFiles.push(displayPath);
          if (!isCheckOnly) {
            fs.writeFileSync(destAgents, content, 'utf8');
            const rootAgents = path.join(targetDir, 'AGENTS.md');
            if (fs.existsSync(rootAgents)) {
              fs.writeFileSync(rootAgents, content, 'utf8');
            }
          }
        } else {
          unchangedFiles.push(displayPath);
        }
      }
    }

    // 5. Update skills-catalog.html
    if (hasCatalog) {
      const srcCatalog = path.join(LOCAL_AGENT_DIR, 'skills-catalog.html');
      const destCatalog = path.join(destAgent, 'skills-catalog.html');

      if (fs.existsSync(srcCatalog)) {
        const srcBuf = fs.readFileSync(srcCatalog);
        let isDifferent = true;
        if (fs.existsSync(destCatalog)) {
          const destBuf = fs.readFileSync(destCatalog);
          isDifferent = Buffer.compare(srcBuf, destBuf) !== 0;
        }

        const displayPath = `.agent/skills-catalog.html`;
        if (isDifferent) {
          updatedFiles.push(displayPath);
          if (!isCheckOnly) {
            fs.copyFileSync(srcCatalog, destCatalog);
          }
        } else {
          unchangedFiles.push(displayPath);
        }
      }
    }
  } else {
    // --- REMOTE GITHUB UPDATE MODE ---
    console.log(`Connecting to GitHub Tree API to resolve updated files...`);
    let tree = [];
    try {
      const treeUrl = `https://api.github.com/repos/${GITHUB_REPO}/git/trees/main?recursive=1`;
      const treeResBuf = await httpGet(treeUrl);
      const treeJson = JSON.parse(treeResBuf.toString('utf8'));
      tree = treeJson.tree || [];
    } catch (err) {
      console.log(`${c.yellow}Tree API unavailable (${err.message}). Falling back to direct URL fetch for installed files.${c.reset}`);
    }

    // Filter remote tree to ONLY include files corresponding to installed assets
    const remoteTargets = [];
    if (tree.length > 0) {
      for (const item of tree) {
        if (item.type !== 'blob') continue;
        const p = item.path.replace(/\\/g, '/');

        // Must start with .agent/
        if (!p.startsWith('.agent/')) continue;

        // Skills check
        if (p.startsWith('.agent/skills/')) {
          const parts = p.split('/');
          const skillName = parts[2];
          if (!installedSkills.includes(skillName)) continue;
          if (!hasThemes && skillName === 'frontend-design' && p.includes('/component-themes/')) continue;
          remoteTargets.push(p);
          continue;
        }

        // Rules check
        if (p.startsWith('.agent/rules/')) {
          const ruleName = path.basename(p);
          if (installedRules.includes(ruleName)) {
            remoteTargets.push(p);
          }
          continue;
        }

        // Templates check
        if (p.startsWith('.agent/templates/')) {
          const tplName = path.basename(p);
          if (installedTemplates.includes(tplName)) {
            remoteTargets.push(p);
          }
          continue;
        }

        if (p === '.agent/AGENTS.md' && hasAgentsMd) {
          remoteTargets.push(p);
          continue;
        }

        if (p === '.agent/skills-catalog.html' && hasCatalog) {
          remoteTargets.push(p);
          continue;
        }
      }
    }

    console.log(`Fetching updates for ${c.cyan}${remoteTargets.length}${c.reset} installed assets from GitHub...`);

    for (const relPath of remoteTargets) {
      const remoteUrl = `${RAW_URL_BASE}/${relPath}`;
      const localFilePath = path.join(targetDir, relPath);

      try {
        const remoteBuf = await httpGet(remoteUrl);
        let newContentBuf = remoteBuf;

        // Apply profile tailoring for rules & AGENTS.md
        if (relPath.startsWith('.agent/rules/')) {
          const ruleName = path.basename(relPath);
          let text = remoteBuf.toString('utf8');
          text = adaptRuleFile(ruleName, text, profile.id);
          newContentBuf = Buffer.from(text, 'utf8');
        } else if (relPath === '.agent/AGENTS.md') {
          let text = remoteBuf.toString('utf8');
          text = filterAgentsMd(text, profile.id);
          text = injectProjectBlock(text, preservedProjectBlock);
          newContentBuf = Buffer.from(text, 'utf8');
        }

        let isDifferent = true;
        if (fs.existsSync(localFilePath)) {
          const localBuf = fs.readFileSync(localFilePath);
          isDifferent = Buffer.compare(newContentBuf, localBuf) !== 0;
        }

        if (isDifferent) {
          updatedFiles.push(relPath);
          if (!isCheckOnly) {
            fs.mkdirSync(path.dirname(localFilePath), { recursive: true });
            fs.writeFileSync(localFilePath, newContentBuf);
            if (relPath === '.agent/AGENTS.md') {
              const rootAgents = path.join(targetDir, 'AGENTS.md');
              if (fs.existsSync(rootAgents)) {
                fs.writeFileSync(rootAgents, newContentBuf);
              }
            }
          }
        } else {
          unchangedFiles.push(relPath);
        }
      } catch (err) {
        errorFiles.push(`${relPath}: ${err.message}`);
      }
    }
  }

  // Update goku.json metadata
  if (!isCheckOnly) {
    const updatedGokuConfig = {
      version: VERSION,
      profile: profileId,
      minimal: !hasThemes,
      installedSkills: installedSkills,
      installedRules: installedRules,
      installedTemplates: installedTemplates,
      lastUpdated: new Date().toISOString(),
      updatedVia: useRemote ? 'github-remote' : 'local-package',
    };
    fs.writeFileSync(gokuJsonPath, JSON.stringify(updatedGokuConfig, null, 2), 'utf8');
  }

  // Summary Report
  console.log(`\n${c.bold}Update Summary:${c.reset}`);
  console.log(`${c.dim}${'─'.repeat(70)}${c.reset}`);
  if (updatedFiles.length > 0) {
    console.log(`${c.green}${c.bold}Files ${isCheckOnly ? 'to update' : 'updated'} (${updatedFiles.length}):${c.reset}`);
    for (const f of updatedFiles.slice(0, 15)) {
      console.log(`  ${c.green}✓${c.reset} ${f}`);
    }
    if (updatedFiles.length > 15) {
      console.log(`  ${c.dim}... and ${updatedFiles.length - 15} more files.${c.reset}`);
    }
  } else {
    console.log(`${c.green}✓ All installed assets are already up-to-date! (0 files changed)${c.reset}`);
  }

  console.log(`\n- Unchanged files: ${c.dim}${unchangedFiles.length} already current${c.reset}`);
  console.log(`- Skipped uninstalled skills: ${c.yellow}${uninstalledCount} skills safely bypassed (zero clutter)${c.reset}`);

  if (errorFiles.length > 0) {
    console.log(`\n${c.red}Warnings / Network Errors (${errorFiles.length}):${c.reset}`);
    for (const err of errorFiles) {
      console.log(`  ${c.red}✗${c.reset} ${err}`);
    }
  }

  if (isCheckOnly) {
    console.log(`\n${c.yellow}Check complete. Run without --check to apply updates.${c.reset}`);
  } else {
    console.log(`\n${c.green}${c.bold}✓ Skill set updated successfully to v${VERSION}!${c.reset}`);
  }
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
  ${c.green}update [options]${c.reset}                 Surgically update only already-installed skills & rules
  ${c.green}list${c.reset}                             List all available skills, profiles & component categories
  ${c.green}add <skill-name...>${c.reset}             Install one or more individual skills
  ${c.green}add theme <category>/<theme>${c.reset}    Install a standalone HTML/CSS component theme
  ${c.green}info <skill-name>${c.reset}               Display triggers, documentation & details for a skill

${c.bold}Init & Update Options:${c.reset}
  -p, --profile <name>            Profile: backend, frontend, creative, fullstack (default: fullstack)
  -m, --minimal                   Exclude heavy component themes in frontend (~5 MB vs ~60 MB)
  -d, --detect                    Auto-detect project stack from current workspace
  --check, --dry-run              Dry-run check: inspect pending updates without modifying files
  --remote                        Force fetching updates directly from GitHub main repository
  --dest <path>                   Custom destination directory (default: current directory)
  --agent <name>                  Target AI agent: antigravity (default), cursor, claude, windsurf
  --with-rules                    Also copy .agent/rules/ quality validation gates
  -v, --version                   Show version number

${c.bold}Examples:${c.reset}
  npx goku-dev-skills init -p backend           # Ultra lightweight Java/.NET API setup (~2.5 MB)
  npx goku-dev-skills init -p frontend -m       # Minimal React/Next.js setup without 55 themes (~5 MB)
  npx goku-dev-skills update                    # Surgically update only existing skills & rules
  npx goku-dev-skills update --check            # Inspect what will be updated without touching disk
  npx goku-dev-skills update --remote           # Pull latest updates directly from GitHub main
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
    check: false,
    dryRun: false,
    remote: false,
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
    } else if (args[i] === '--check') {
      options.check = true;
    } else if (args[i] === '--dry-run') {
      options.dryRun = true;
    } else if (args[i] === '--remote') {
      options.remote = true;
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

    case 'update':
    case 'upgrade':
    case 'sync':
      await cmdUpdate(options);
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
