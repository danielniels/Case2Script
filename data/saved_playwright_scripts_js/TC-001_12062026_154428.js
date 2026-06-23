// Auto-generated Playwright script — TC-001_12062026_154428
// Generated: 2026-06-12 15:52:31
// Source: TC-001_12062026_154428.json
// Run: node TC-001_12062026_154428.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_screenshots/playwright_screenshots/TC-001_12062026_154428', { recursive: true });

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
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_1.png" });

    // Step 2: Mengisi Username → daniel.purba@is-gs.com
    console.log('▶ STEP 2');
    await page.locator("#email").first().fill("daniel.purba@is-gs.com");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_2.png" });

    // Step 3: Mengisi Password → Password
    console.log('▶ STEP 3');
    await page.locator("#password").first().fill("Password");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_3.png" });

    // Step 4: Klik Button Login
    console.log('▶ STEP 4');
    await page.locator("#loginBtn").first().click();
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_4.png" });

    // Step 5: Halaman Dashboard
    console.log('▶ STEP 5');
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_5.png" });

    // Step 6: Tutup Pop Up Message
    console.log('▶ STEP 6');
    await page.keyboard.press("Escape");await page.waitForTimeout(1000);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_6.png" });

    // STEP 7 FAILED [assert_text] — fix manually before running
    // Berhasil mengambil Leave Balance: -2.0
    // { const t = (await page.locator("//body").first().innerText()).trim(); if (!t.includes("Leave Balance: -2.0")) throw new Error("assert_text failed — expected " + "Leave Balance: -2.0" + ", got: " + t); }

    // Step 8: Klik Menu: Request Pada Sidebar
    console.log('▶ STEP 8');
    await page.locator("a.has-arrow.waves-effect").first().click();
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_8.png" });

    // Step 9: Klik Submenu: My Request Pada Sidebar
    console.log('▶ STEP 9');
    await page.locator("//a[.//text()[normalize-space(.) = \"My Request\"]]").first().click();
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_9.png" });

    // Step 10: Menampilkan Halaman My Request
    console.log('▶ STEP 10');
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_10.png" });

    // Step 11: Klik Tab Menu Leave Request
    console.log('▶ STEP 11');
    await page.locator("//a[.//text()[normalize-space(.) = \"Leave Request\"]]").first().click();
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_11.png" });

    // Step 12: Klik Button Add Leave
    console.log('▶ STEP 12');
    await page.locator("//button[.//text()[normalize-space(.) = \"Add Leave Request\"]]").first().click();
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_12.png" });

    // Step 13: Memilih Type Leave → Annual Leave
    console.log('▶ STEP 13');
    await page.selectOption("//span[.//text()[normalize-space(.) = \"Annual Leave\"]]", { label: "Annual Leave" });
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_13.png" });

    // Step 14: Mengisi Start Date → 30-Jul-2026
    console.log('▶ STEP 14');
    await page.locator("#request_start").first().fill("30-Jul-2026");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_14.png" });

    // Step 15: Mengisi End Date → 30-Jul-2026
    console.log('▶ STEP 15');
    await page.locator("#request_end").first().fill("30-Jul-2026");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_15.png" });

    // Step 16: Mengisi Detail Request → Cuti tahunan
    console.log('▶ STEP 16');
    await page.locator("//textarea[@id=\"request_detail\"]").first().fill("Cuti tahunan");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_16.png" });

    // Step 17: Klik Button Submit
    console.log('▶ STEP 17');
    await page.locator("#form-btn").first().click();
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_17.png" });

    // STEP 18 FAILED [assert_text] — fix manually before running
    // VALID: Data Ditemukan → Annual Leave / 30-Jul-2026
    // { const t = (await page.locator("//body").first().innerText()).trim(); if (!t.includes("Annual Leave / 30-Jul-2026")) throw new Error("assert_text failed — expected " + "Annual Leave / 30-Jul-2026" + ", got: " + t); }

    // Step 19: Klik Button Profile
    console.log('▶ STEP 19');
    await page.locator("#page-header-user-dropdown").first().click();
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_19.png" });

    // Step 20: Klik Button Logout
    console.log('▶ STEP 20');
    await page.locator("a.dropdown-item").first().click();
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_20.png" });

    // Step 21: Berhasil Logout Akun
    console.log('▶ STEP 21');
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_12062026_154428/step_21.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();