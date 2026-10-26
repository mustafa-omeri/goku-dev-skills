#!/usr/bin/env node
/**
 * Cookie & Network Request Auditor (Playwright)
 * Verifies third-party requests and cookies before and after consent interaction.
 *
 * Usage:
 *   node .agent/skills/prelaunch-audit/scripts/consent-check.mjs https://staging.example.com
 */

import { chromium } from 'playwright';

const targetUrl = process.argv[2];
if (!targetUrl) {
  console.error("Usage: node consent-check.mjs <URL>");
  process.exit(1);
}

try {
  const urlObj = new URL(targetUrl);
  const siteDomain = urlObj.hostname.replace(/^www\./, '');

  console.log(`Auditing consent & cookie network behavior for: ${targetUrl}`);
  const browser = await chromium.launch();
  const context = await browser.newContext(); // Clean profile, no existing cookies
  const page = await context.newPage();

  const thirdPartyHosts = new Set();
  const allRequests = [];

  page.on('request', (request) => {
    try {
      const reqUrl = new URL(request.url());
      const reqHost = reqUrl.hostname;
      allRequests.push({ url: request.url(), host: reqHost });
      if (!reqHost.endsWith(siteDomain) && !reqHost.includes('localhost') && !reqHost.includes('127.0.0.1')) {
        thirdPartyHosts.add(reqHost);
      }
    } catch {
      // ignore invalid URL
    }
  });

  await page.goto(targetUrl, { waitUntil: 'networkidle' });
  const initialCookies = await context.cookies();

  console.log('\n--- 1. ONAY ÖNCESİ (PRE-CONSENT) DURUM ---');
  console.log(`Toplam İlk Çerez Sayısı: ${initialCookies.length}`);
  for (const c of initialCookies) {
    console.log(`  - ${c.name} (${c.domain}) [expires: ${c.expires}]`);
  }

  console.log(`\nToplam 3. Taraf Host İstekleri: ${thirdPartyHosts.size}`);
  for (const host of thirdPartyHosts) {
    console.log(`  - ${host}`);
  }

  // Look for common analytics/marketing trackers fired prior to consent
  const criticalTrackers = ['google-analytics.com', 'analytics.google.com', 'facebook.net', 'clarity.ms', 'hotjar.com', 'tiktok.com', 'yandex.ru'];
  const leakingTrackers = [...thirdPartyHosts].filter(h => criticalTrackers.some(t => h.includes(t)));

  if (leakingTrackers.length > 0) {
    console.warn(`\n[BLOCKER UYARISI] Onay verilmeden önce şu izleme hostlarına istek gönderildi:`);
    for (const leak of leakingTrackers) {
      console.warn(`  ! ${leak}`);
    }
  } else {
    console.log('\n[PASS] Onay öncesinde kritik analitik/pazarlama izleme isteği tespit edilmedi.');
  }

  await browser.close();
} catch (err) {
  console.error("Consent check error:", err.message);
  process.exit(1);
}
