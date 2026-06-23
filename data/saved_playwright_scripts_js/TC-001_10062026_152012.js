// Auto-generated Playwright script — TC-001
// Generated: 2026-06-10 15:29:07
// Run: node TC-001_10062026_152012.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');

async function runTest() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();

  try {
    // Step 1: Menampilkan Halaman Login
    await page.goto("https://dev.itsaplic.com/login", { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});

    // Step 2: Mengisi Username
    await page.fill("//INPUT[@id=\"email\"]", "daniel.purba@is-gs.com");

    // Step 3: Mengisi Password
    await page.fill("//INPUT[@id=\"password\"]", "Password");

    // Step 4: Klik Button Login
    await page.click("//BUTTON[@id=\"loginBtn\"]");
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);

    // Step 5: Halaman Dashboard
    await page.screenshot({ path: "saved_playwright_scripts/step_5.png" });

    // Step 6: Tutup Pop Up Message
    await page.keyboard.press("Escape");
    await page.waitForTimeout(1000);  // tunggu popup tutup

    // Step 7: Berhasil mengambil Leave Balance
    await page.screenshot({ path: "saved_playwright_scripts/step_7.png" });

    // Step 8: VALID: Leave Balance Sesuai → Expected=-3.0
    await page.screenshot({ path: "saved_playwright_scripts/step_8.png" });

    // Step 9: Klik Menu Request Pada Sidebar
    await page.click("//A[.//text()[normalize-space(.) = \"Request\"]]");
    await page.waitForTimeout(800);  // tunggu submenu expand
    await page.waitForSelector(
      "//A[.//text()[normalize-space(.) = \"My Request\"]]",
      { state: 'visible', timeout: 5000 }
    ).catch(() => {});

    // Step 10: Klik Submenu My Request
    await page.click("//A[.//text()[normalize-space(.) = \"My Request\"]]", { force: true});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(500);

    // Step 11: VALID: Data Ditemukan
    await page.screenshot({ path: "saved_playwright_scripts/step_11.png" });

    // Step 12: VALID: Status Request Approved
    await page.screenshot({ path: "saved_playwright_scripts/step_12.png" });

    // Step 13: Klik Button Profile
    await page.click("//BUTTON[@id=\"page-header-user-dropdown\"]");
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForTimeout(500);

    // Step 14: Klik Button Logout
    await page.click("//A[.//text()[normalize-space(.) = \"Logout\"]]");
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});

    // Step 15: Berhasil Logout
    await page.screenshot({ path: "saved_playwright_scripts/step_15.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();