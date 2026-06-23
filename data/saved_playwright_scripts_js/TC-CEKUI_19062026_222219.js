// Auto-generated Playwright script — TC-CEKUI_19062026_222219
// Generated: 2026-06-19 22:22:26
// Source: TC-CEKUI_19062026_222219.json
// Run: node TC-CEKUI_19062026_222219.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('data/saved_playwright_scripts/screenshots/TC-CEKUI_19062026_222219', { recursive: true });

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
    await page.screenshot({ path: "data/saved_playwright_scripts/screenshots/TC-CEKUI_19062026_222219/step_1.png" });

    // Step 2: Mengisi Username → daniel.purba@is-gs.com
    console.log('▶ STEP 2');
    await page.locator("xpath=//input[@id=\"email\"]").first().fill("daniel.purba@is-gs.com");
    await page.screenshot({ path: "data/saved_playwright_scripts/screenshots/TC-CEKUI_19062026_222219/step_2.png" });

    // Step 3: VALID: Halaman Login → Login
    console.log('▶ STEP 3');
    { const t = (await page.locator("//body").first().innerText()).trim(); if (!t.includes("Login")) throw new Error("assert_text failed — expected " + "Login" + ", got: " + t); }
    await page.screenshot({ path: "data/saved_playwright_scripts/screenshots/TC-CEKUI_19062026_222219/step_3.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();