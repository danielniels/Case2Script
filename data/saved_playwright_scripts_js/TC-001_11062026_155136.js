// Auto-generated Playwright script — TC-001_11062026_155136
// Generated: 2026-06-11 15:59:42
// Source: TC-001_11062026_155136.json
// Run: node TC-001_11062026_155136.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_screenshots/playwright_screenshots/TC-001_11062026_155136', { recursive: true });

async function runTest() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();

  try {

    // Step 1: Menampilkan Halaman Login https://dev.itsaplic.com/login
    await page.goto("https://dev.itsaplic.com/login", { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_1.png" });

    // Step 2: Mengisi Username → daniel.purba@is-gs.com
    await page.fill("//INPUT[@id=\"email\"]", "daniel.purba@is-gs.com");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_2.png" });

    // Step 3: Mengisi Password → Password
    await page.fill("//INPUT[@id=\"password\"]", "Password");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_3.png" });

    // Step 4: Klik Button Login
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//BUTTON[@id=\"loginBtn\"]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_4.png" });

    // [Step 5] Halaman Dashboard [get_page_info] — MCP-only, skipped

    // Step 6: Tutup Pop Up Message
    await page.keyboard.press("Escape");await page.waitForTimeout(1000);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_6.png" });

    // Step 7: Berhasil mengambil Leave Balance: -2.0
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_7.png" });

    // Step 8: Klik Menu: Request Pada Sidebar
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Request\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_8.png" });

    // Step 9: Klik Submenu: My Request Pada Sidebar
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"My Request\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_9.png" });

    // Step 10: Menampilkan Halaman My Request
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_10.png" });

    // Step 11: Klik Tab Menu Leave Request
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Leave Request\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_11.png" });

    // Step 12: Klik Button Add Leave
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//BUTTON[.//text()[normalize-space(.) = \"Add Leave Request\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_12.png" });

    // Step 13: Memilih Type Leave → Annual Leave
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//SPAN[.//text()[normalize-space(.) = \"Annual Leave\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_13.png" });

    // Step 14: Mengisi Start Date → 30-Jul-2026
    await page.fill("//INPUT[@id=\"request_start\"]", "30-Jul-2026");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_14.png" });

    // Step 15: Mengisi End Date → 30-Jul-2026
    await page.fill("//INPUT[@id=\"request_end\"]", "30-Jul-2026");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_15.png" });

    // Step 16: Mengisi Detail Request → Cuti tahunan
    await page.fill("//TEXTAREA[@id=\"request_detail\"]", "Cuti tahunan");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_16.png" });

    // Step 17: Klik Button Submit
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//BUTTON[@id=\"form-btn\"]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_17.png" });

    // Step 18: VALID: Data Ditemukan → Annual Leave / 30-Jul-2026
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_18.png" });

    // Step 19: Klik Button Profile
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//BUTTON[@id=\"page-header-user-dropdown\"]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_19.png" });

    // Step 20: Klik Button Logout
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Logout\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_20.png" });

    // Step 21: Berhasil Logout Akun
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001_11062026_155136/step_21.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();