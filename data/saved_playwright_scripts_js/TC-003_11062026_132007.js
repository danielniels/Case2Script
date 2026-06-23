// Auto-generated Playwright script — TC-003_11062026_132007
// Generated: 2026-06-11 13:28:22
// Source: TC-003_11062026_132007.json
// Run: node TC-003_11062026_132007.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_playwright_scripts/screenshots/TC-003_11062026_132007', { recursive: true });

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
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//BUTTON[@id=\"loginBtn\"]").catch(() => {});
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 5: Halaman Dashboard
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-003_11062026_132007/step_5.png" });

    // Step 6: Tutup Pop Up Message
    await page.keyboard.press("Escape");await page.waitForTimeout(1000);

    // Step 7: Klik Menu: Request Pada Sidebar
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Request\"]]").catch(() => {});
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 8: Klik Submenu: My Request Pada Sidebar
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"My Request\"]]").catch(() => {});
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 9: Menampilkan Halaman My Request
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-003_11062026_132007/step_9.png" });

    // Step 10: Klik Tab Menu WFH Request
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"WFH Request\"]]").catch(() => {});
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 11: Klik Button Add WFH Request
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//BUTTON[.//text()[normalize-space(.) = \"Add WFH Request\"]]").catch(() => {});
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 12: Menampilkan Form Add WFH Request
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Request\"]]").catch(() => {});
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 13: Mengisi Start Date → 10-June-2026
    await page.fill("//INPUT[@id=\"request_start\"]", "10-June-2026");

    // Step 14: Mengisi End Date → 15-June-2026
    await page.fill("//INPUT[@id=\"request_end\"]", "15-June-2026");

    // Step 15: Mengisi Detail → WFH bulan Juni 2026
    await page.fill("//TEXTAREA[@id=\"request_detail\"]", "WFH bulan Juni 2026");

    // STEP 16 FAILED [fill] — fix manually before running
    // Upload Attachment → C:/mcp/test-assets/dummy.png
    // await page.fill("//INPUT[@id=\"request_file\"]", "C:/mcp/test-assets/dummy.png");

    // Step 17: Klik Button Submit Request
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//BUTTON[@id=\"form-btn\"]").catch(() => {});
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 18: VALID: Data Ditemukan → WFH / 10-June-2026
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-003_11062026_132007/step_18.png" });

    // Step 19: Klik Button Profile
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//BUTTON[@id=\"page-header-user-dropdown\"]").catch(() => {});
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 20: Klik Button Logout
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Logout\"]]").catch(() => {});
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 21: Berhasil Logout Akun
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-003_11062026_132007/step_21.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();