// Auto-generated Playwright script — TC-B2_19062026_113549
// Generated: 2026-06-19 11:35:57
// Source: TC-B2_19062026_113549.json
// Run: node TC-B2_19062026_113549.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('data/saved_playwright_scripts/screenshots/TC-B2_19062026_113549', { recursive: true });

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
    await page.screenshot({ path: "data/saved_playwright_scripts/screenshots/TC-B2_19062026_113549/step_1.png" });

    // Step 2: Mengisi Username → daniel.purba@is-gs.com
    console.log('▶ STEP 2');
    await page.locator("#email").first().fill("daniel.purba@is-gs.com");
    await page.screenshot({ path: "data/saved_playwright_scripts/screenshots/TC-B2_19062026_113549/step_2.png" });

    // Step 3: VALID: Halaman Login → Login
    console.log('▶ STEP 3');
    { const t = (await page.locator("//body").first().innerText()).trim(); if (!t.includes("Login")) throw new Error("assert_text failed — expected " + "Login" + ", got: " + t); }
    await page.screenshot({ path: "data/saved_playwright_scripts/screenshots/TC-B2_19062026_113549/step_3.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();