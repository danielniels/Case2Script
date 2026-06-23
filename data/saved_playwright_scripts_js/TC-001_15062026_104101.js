// Auto-generated Playwright script — TC-001_15062026_104101
// Generated: 2026-06-15 10:41:02
// Source: TC-001_15062026_104101.json
// Run: node TC-001_15062026_104101.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_playwright_scripts/screenshots/TC-001_15062026_104101', { recursive: true });

async function runTest() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();

  try {

    // Step 1: http://127.0.0.1:5500/OSS_2.0_POC.html#/login
    console.log('▶ STEP 1');
    await page.goto("http://127.0.0.1:5500/OSS_2.0_POC.html#/login", { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_104101/step_1.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();