// Auto-generated Playwright script — TC-RETRY2_19062026_225901
// Generated: 2026-06-19 22:59:24
// Source: TC-RETRY2_19062026_225901.json
// Run: node TC-RETRY2_19062026_225901.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('data/saved_playwright_scripts/screenshots/TC-RETRY2_19062026_225901', { recursive: true });

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
    await page.screenshot({ path: "data/saved_playwright_scripts/screenshots/TC-RETRY2_19062026_225901/step_1.png" });

    // Step 2: Klik Elemen Dengan ID css-selector-tidak-pernah-ada-zzz999xyz
    console.log('▶ STEP 2');

    // Step 3: VALID: Halaman Login → Login
    console.log('▶ STEP 3');
    { const t = (await page.locator("//body").first().innerText()).trim(); if (!t.includes("Login")) throw new Error("assert_text failed — expected " + "Login" + ", got: " + t); }
    await page.screenshot({ path: "data/saved_playwright_scripts/screenshots/TC-RETRY2_19062026_225901/step_3.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();