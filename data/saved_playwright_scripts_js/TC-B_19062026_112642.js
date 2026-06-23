// Auto-generated Playwright script — TC-B_19062026_112642
// Generated: 2026-06-19 11:26:47
// Source: TC-B_19062026_112642.json
// Run: node TC-B_19062026_112642.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('data/saved_playwright_scripts/screenshots/TC-B_19062026_112642', { recursive: true });

async function runTest() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();

  try {

    // Step 1: Menampilkan Halaman Login https://dev.itsaplic.com/login
    console.log('▶ STEP 1');
    await page.goto("https://dev.itsaplic.com/login", { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: "data/saved_playwright_scripts/screenshots/TC-B_19062026_112642/step_1.png" });

    // Step 2: VALID: Halaman Login → Login
    console.log('▶ STEP 2');
    { const t = (await page.locator("//body").first().innerText()).trim(); if (!t.includes("Login")) throw new Error("assert_text failed — expected " + "Login" + ", got: " + t); }
    await page.screenshot({ path: "data/saved_playwright_scripts/screenshots/TC-B_19062026_112642/step_2.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();