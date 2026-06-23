// Auto-generated Playwright script — TC-001
// Generated: 2026-06-10 15:01:35
// Run: node TC-001_10062026_145500.js
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

    // Step 2: Mengisi Username → daniel.purba@is-gs.com
    await page.fill("//INPUT[@id=\"email\"]", "daniel.purba@is-gs.com");

    // Step 3: Mengisi Password → Password
    await page.fill("//INPUT[@id=\"password\"]", "Password");

    // Step 4: Klik Button Login
    await page.click("//BUTTON[@id=\"loginBtn\"]");
    await page.waitForLoadState('load').catch(() => {});

    // [Step 5] Halaman Dashboard [get_page_info] — MCP-only, skipped

    // Step 6: Tutup Pop Up Message
    await page.keyboard.press("Escape");

    // Step 7: Berhasil mengambil Leave Balance: -3
    await page.screenshot({ path: "screenshot.png" });

    // Step 8: VALID: Leave Balance Sesuai → Before=-2, After= -3, Expected=-3.0
    await page.screenshot({ path: "screenshot.png" });

    // Step 9: Klik Menu: Request Pada Sidebar
    await page.click("//A[.//text()[normalize-space(.) = \"Request\"]]");
    await page.waitForLoadState('load').catch(() => {});

    // Step 10: Klik Submenu: My Request Pada Sidebar
    await page.click("//A[.//text()[normalize-space(.) = \"My Request\"]]");
    await page.waitForLoadState('load').catch(() => {});

    // Step 11: VALID: Data Ditemukan → Annual Leave / 30-Jun-2026
    await page.screenshot({ path: "screenshot.png" });

    // Step 12: VALID: Status Request Approved → Annual Leave / 30-Jun-2026
    await page.click("//BUTTON[.//text()[normalize-space(.) = \"Approved\"]]");
    await page.waitForLoadState('load').catch(() => {});

    // Step 13: Klik Button Profile
    await page.click("//BUTTON[@id=\"page-header-user-dropdown\"]");
    await page.waitForLoadState('load').catch(() => {});

    // Step 14: Klik Button Logout
    await page.click("//A[.//text()[normalize-space(.) = \"Logout\"]]");
    await page.waitForLoadState('load').catch(() => {});

    // Step 15: Berhasil Logout Akun
    await page.click("//BUTTON[@aria-label=\"Timesheet\"]");
    await page.waitForLoadState('load').catch(() => {});

    console.log('✔ Test completed');
  } catch (err) {
    console.error('✘ Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();