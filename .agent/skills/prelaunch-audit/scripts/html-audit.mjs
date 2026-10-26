#!/usr/bin/env node
/**
 * Raw HTML Validator (SEO, Metadata, Headings, Images)
 * Inspects initial server-rendered or static HTML without relying on client-side JS.
 *
 * Usage:
 *   node .agent/skills/prelaunch-audit/scripts/html-audit.mjs https://example.com
 *   node .agent/skills/prelaunch-audit/scripts/html-audit.mjs ./dist/index.html
 */

import fs from 'fs';

const target = process.argv[2];
if (!target) {
  console.error("Usage: node html-audit.mjs <URL or local file path>");
  process.exit(1);
}

let htmlContent = '';

if (target.startsWith('http://') || target.startsWith('https://')) {
  try {
    const res = await fetch(target, { headers: { 'User-Agent': 'Mozilla/5.0 (PrelaunchAuditBot/1.0)' } });
    if (!res.ok) {
      console.error(`HTTP error: ${res.status} ${res.statusText}`);
      process.exit(1);
    }
    htmlContent = await res.text();
  } catch (err) {
    console.error(`Failed to fetch URL: ${err.message}`);
    process.exit(1);
  }
} else {
  try {
    htmlContent = fs.readFileSync(target, 'utf-8');
  } catch (err) {
    console.error(`Failed to read file: ${err.message}`);
    process.exit(1);
  }
}

console.log("=".repeat(60));
console.log(`RAW HTML AUDIT: ${target}`);
console.log("=".repeat(60));

const issues = [];
const passes = [];

// 1. Title
const titleMatch = htmlContent.match(/<title[^>]*>(.*?)<\/title>/is);
if (!titleMatch) {
  issues.push("BLOCKER: <title> tag missing in raw HTML.");
} else {
  const title = titleMatch[1].trim();
  const len = title.length;
  if (len < 20 || len > 70) {
    issues.push(`MAJOR: <title> length (${len} chars) is outside optimal range (20-65 chars): "${title}"`);
  } else {
    passes.push(`<title> optimal: "${title}" (${len} chars)`);
  }
}

// 2. Meta description
const descMatch = htmlContent.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']/i) ||
                  htmlContent.match(/<meta[^>]*content=["']([^"']*)["'][^>]*name=["']description["']/i);
if (!descMatch) {
  issues.push("MAJOR: <meta name='description'> missing in raw HTML.");
} else {
  const desc = descMatch[1].trim();
  const len = desc.length;
  if (len < 80 || len > 165) {
    issues.push(`MAJOR: Meta description length (${len} chars) is outside optimal range (110-160 chars).`);
  } else {
    passes.push(`Meta description optimal: "${desc.substring(0, 50)}..." (${len} chars)`);
  }
}

// 3. Canonical
const canonicalMatch = htmlContent.match(/<link[^>]*rel=["']canonical["'][^>]*href=["']([^"']*)["']/i) ||
                       htmlContent.match(/<link[^>]*href=["']([^"']*)["'][^>]*rel=["']canonical["']/i);
if (!canonicalMatch) {
  issues.push("MAJOR: <link rel='canonical'> missing in raw HTML.");
} else {
  const canonicalUrl = canonicalMatch[1].trim();
  if (!canonicalUrl.startsWith('https://')) {
    issues.push(`BLOCKER: Canonical URL is not absolute HTTPS: "${canonicalUrl}"`);
  } else {
    passes.push(`Canonical URL valid: ${canonicalUrl}`);
  }
}

// 4. h1 count
const h1Matches = htmlContent.match(/<h1[^>]*>/gi) || [];
if (h1Matches.length === 0) {
  issues.push("MAJOR: No <h1> tag found in raw HTML.");
} else if (h1Matches.length > 1) {
  issues.push(`WARNING: Multiple (${h1Matches.length}) <h1> tags found. Best practice is a single <h1> per page.`);
} else {
  passes.push("Single <h1> tag verified.");
}

// 5. Images missing alt
const imgTags = htmlContent.match(/<img[^>]*>/gi) || [];
let missingAlt = 0;
for (const img of imgTags) {
  if (!img.includes('alt=')) {
    missingAlt++;
  }
}
if (missingAlt > 0) {
  issues.push(`MAJOR: ${missingAlt} of ${imgTags.length} <img> tags are missing the alt attribute entirely.`);
} else if (imgTags.length > 0) {
  passes.push(`All ${imgTags.length} <img> tags have an alt attribute.`);
}

// 6. OpenGraph tags
const hasOgTitle = /<meta[^>]*property=["']og:title["']/i.test(htmlContent);
const hasOgImage = /<meta[^>]*property=["']og:image["']/i.test(htmlContent);
if (!hasOgTitle || !hasOgImage) {
  issues.push("MAJOR: Incomplete OpenGraph tags (og:title or og:image missing).");
} else {
  passes.push("OpenGraph basic tags present (og:title, og:image).");
}

console.log("\n[PASSES]");
for (const p of passes) {
  console.log(`  + ${p}`);
}

console.log("\n[ISSUES / FINDINGS]");
if (issues.length === 0) {
  console.log("  None! Raw HTML passed all primary checks.");
} else {
  for (const iss of issues) {
    console.log(`  - ${iss}`);
  }
}
console.log("=".repeat(60));
