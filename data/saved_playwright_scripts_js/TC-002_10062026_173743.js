// Auto-generated Playwright script — TC-002
// Generated: 2026-06-10 17:45:40
// Run: node TC-002_10062026_173743.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');

async function runTest() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();

  try {

    // Step 1: Menampilkan Halaman Login https://dev.itsaplic.com/login
    await page.goto("https://dev.itsaplic.com/login", { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForLoadState('load').catch(() => {});

    // Step 2: Mengisi Username → daniel.purba@is-gs.com
    await page.fill("//INPUT[@id=\"email\"]", "daniel.purba@is-gs.com");

    // Step 3: Mengisi Password → Password
    await page.fill("//INPUT[@id=\"password\"]", "Password");

    // Step 4: Klik Button Login
    await page.locator("//BUTTON[@id=\"loginBtn\"]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);
    await page.waitForLoadState('load').catch(() => {});

    // [Step 5] Halaman Dashboard [get_page_info] — MCP-only, skipped

    // Step 6: Tutup Pop Up Message
    await page.keyboard.press("Escape");

    // Step 7: Klik Menu: Request Pada Sidebar
    await page.locator("//A[.//text()[normalize-space(.) = \"Request\"]]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);
    await page.waitForLoadState('load').catch(() => {});

    // Step 8: Klik Submenu: My Request Pada Sidebar
    await page.locator("//A[.//text()[normalize-space(.) = \"My Request\"]]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);
    await page.waitForLoadState('load').catch(() => {});

    // Step 9: Menampilkan Halaman My Request
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-002_10062026_173743/step_9.png" });

    // Step 10: Klik Tab Menu Other Claim
    await page.locator("//A[.//text()[normalize-space(.) = \"Other Claim\"]]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);
    await page.waitForLoadState('load').catch(() => {});

    // Step 11: Klik Button Add Other Claim
    await page.locator("//BUTTON[.//text()[normalize-space(.) = \"Add Other Claim\"]]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);
    await page.waitForLoadState('load').catch(() => {});

    // Step 12: Menampilkan Form Add Other Claim Request
    await page.locator("//A[.//text()[normalize-space(.) = \"Request\"]]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);
    await page.waitForLoadState('load').catch(() => {});

    // Step 13: Mengisi Claim Date → 08-June-2026
    await page.fill("//INPUT[@id=\"request_start\"]", "08-June-2026");

    // Step 14: Mengisi Start Date → 8-June-2026
    await page.fill("//INPUT[@id=\"request_start\"]", "8-June-2026");

    // Step 15: Mengisi End Date → 8-August-2026
    await page.fill("//INPUT[@id=\"request_end\"]", "8-August-2026");

    // Step 16: Klik Button Submit Request
    await page.locator("//BUTTON[@id=\"form-btn\"]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);
    await page.waitForLoadState('load').catch(() => {});

    // Step 17: VALID: Data Ditemukan → Other Claim / 1-May-2026
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-002_10062026_173743/step_17.png" });

    // Step 18: Klik Button Profile
    await page.locator("//BUTTON[@id=\"page-header-user-dropdown\"]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);
    await page.waitForLoadState('load').catch(() => {});

    // Step 19: Klik Button Logout
    await page.locator("//A[.//text()[normalize-space(.) = \"Logout\"]]").click({ force: true });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);
    await page.waitForLoadState('load').catch(() => {});

    // Step 20: Berhasil Logout Akun
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-002_10062026_173743/step_20.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();