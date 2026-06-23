// Auto-generated Playwright script — TC-002_11062026_104205
// Generated: 2026-06-11 10:50:12
// Source: TC-002_11062026_104205.json
// Run: node TC-002_11062026_104205.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_playwright_scripts/screenshots/TC-002_11062026_104205', { recursive: true });

async function runTest() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();

  try {

    // Step 1: Menampilkan Halaman Login https://dev.itsaplic.com/login
    await page.goto("https://dev.itsaplic.com/login", { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});

    // Step 2: Mengisi Username → daniel.purba@is-gs.com
    await page.fill("//INPUT[@id=\"email\"]", "daniel.purba@is-gs.com");

    // Step 3: Mengisi Password → Password
    await page.fill("//INPUT[@id=\"password\"]", "Password");

    // Step 4: Klik Button Login
    await page.locator("//BUTTON[@id=\"loginBtn\"]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);

    // Step 5: Halaman Dashboard
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-002_11062026_104205/step_5.png" });

    // Step 6: Tutup Pop Up Message
    await page.keyboard.press("Escape");
    await page.waitForTimeout(1000);

    // Step 7: Klik Menu: Request Pada Sidebar
    await page.locator("//A[.//text()[normalize-space(.) = \"Request\"]]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(1000);

    // Step 8: Klik Submenu: My Request Pada Sidebar
    await page.evaluate((sel) => {
    const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
    	if (r.singleNodeValue) r.singleNodeValue.click();
    }, "//A[.//text()[normalize-space(.) = \"My Request\"]]");
    
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);

    // Step 9: Menampilkan Halaman My Request
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-002_11062026_104205/step_9.png" });

    // Step 10: Klik Tab Menu Other Claim
    await page.locator("//A[.//text()[normalize-space(.) = \"Other Claim\"]]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);

    // Step 11: Klik Button Add Other Claim
    await page.locator("//BUTTON[.//text()[normalize-space(.) = \"Add Other Claim\"]]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);

    // Step 12: Menampilkan Form Add Other Claim Request
    await page.locator("//A[.//text()[normalize-space(.) = \"Request\"]]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);

    // Step 13: Mengisi Claim Date → 31-August-2026
    await page.fill("//INPUT[@id=\"request_end\"]", "31-August-2026");

    // Step 14: Mengisi Start Date → 11-June-2026
    await page.fill("//INPUT[@id=\"request_start\"]", "11-June-2026");

    // Step 15: Mengisi End Date → 29-August-2026
    await page.fill("//INPUT[@id=\"request_end\"]", "29-August-2026");

    // Step 16: Klik Button Submit Request
    await page.locator("//BUTTON[@id=\"form-btn\"]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);

    // Step 17: VALID: Data Ditemukan → Other Claim / 31-August-2026
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-002_11062026_104205/step_17.png" });

    // Step 18: Klik Button Profile
    await page.locator("//BUTTON[@id=\"page-header-user-dropdown\"]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);

    // Step 19: Klik Button Logout
    await page.locator("//A[.//text()[normalize-space(.) = \"Logout\"]]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);

    // Step 20: Berhasil Logout Akun
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-002_11062026_104205/step_20.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();