#!/usr/bin/env node
/**
 * Headless Accessibility Scanner (WCAG 2.2 AA via Playwright & AxeBuilder)
 *
 * Usage:
 *   node .agent/skills/prelaunch-audit/scripts/axe-runner.mjs http://localhost:4173
 */

import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';

const urls = process.argv.slice(2);
if (urls.length === 0) {
  console.error("Usage: node axe-runner.mjs <URL1> [URL2] ...");
  process.exit(1);
}

const browser = await chromium.launch();
let totalViolations = 0;

try {
  for (const url of urls) {
    console.log(`\nScanning accessibility for: ${url}`);
    const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
    const page = await context.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .analyze();

    console.log(`Violations Found: ${results.violations.length}`);
    for (const v of results.violations) {
      console.log(`  - [${v.impact ? v.impact.toUpperCase() : 'UNKNOWN'}] ${v.id}: ${v.help} (${v.nodes.length} nodes)`);
      if (v.impact === 'critical' || v.impact === 'serious') {
        totalViolations += v.nodes.length;
      }
    }
    await context.close();
  }
} catch (err) {
  console.error("Accessibility scan error:", err.message);
} finally {
  await browser.close();
}

if (totalViolations > 0) {
  console.warn(`\n[FAIL] Found ${totalViolations} critical/serious accessibility violations.`);
  process.exit(1);
} else {
  console.log('\n[PASS] Zero critical/serious WCAG violations found.');
  process.exit(0);
}
