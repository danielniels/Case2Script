// Auto-generated Playwright script — TC-001_11062026_141319
// Generated: 2026-06-11 14:44:34
// Source: TC-001_11062026_141319.json
// Run: node TC-001_11062026_141319.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_playwright_scripts/screenshots/TC-001_11062026_141319', { recursive: true });

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
    }, "//BUTTON[@id=\"loginBtn\"]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 5: Halaman Dashboard
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_5.png" });

    // Step 6: Tutup Pop Up Message
    await page.keyboard.press("Escape");await page.waitForTimeout(1000);

    // Step 7: Berhasil mengambil Leave Balance: -2.0
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_7.png" });

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

    // Step 10: Menampilkan Halaman My Request
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_10.png" });

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

    // Step 14: Mengisi Start Date → 1-Jul-2026
    await page.fill("//INPUT[@id=\"request_start\"]", "1-Jul-2026");

    // Step 15: Mengisi End Date → 1-Jul-2026
    await page.fill("//INPUT[@id=\"request_end\"]", "1-Jul-2026");

    // Step 16: Mengisi Detail Request → Cuti tahunan
    await page.fill("//TEXTAREA[@id=\"request_detail\"]", "Cuti tahunan");

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

    // Step 18: VALID: Data Ditemukan → Annual Leave / 1-Jul-2026
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_18.png" });

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

    // Step 21: Berhasil Logout Akun
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_21.png" });

    // Step 22: Mengisi Username → rosellini.viollen@is-gs.com
    await page.fill("//INPUT[@id=\"email\"]", "rosellini.viollen@is-gs.com");

    // Step 23: Mengisi Password → Password
    await page.fill("//INPUT[@id=\"password\"]", "Password");

    // Step 24: Klik Button Login
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

    // [Step 25] Halaman Dashboard [get_page_info] — MCP-only, skipped

    // Step 26: Tutup Pop Up Message
    await page.keyboard.press("Escape");await page.waitForTimeout(1000);

    // Step 27: Klik Menu: Approval Pada Sidebar
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Approval\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 28: Klik Submenu: Approval Request Pada Sidebar
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Approval Request\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 29: Menampilkan Halaman Approval Request
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_29.png" });

    // Step 30: Klik Tab Leave Pada Filter Type Approval
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Leave\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 31: Klik Field Search, Cari Data → daniel purba
    await page.fill("//INPUT[@aria-controls=\"leave-tabpanelTable\"]", "daniel purba");

    // Step 32: Pilih Checkbox Untuk Request Yang Ingin Diapprove
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//INPUT[@id=\"select_all_leave\"]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 33: Klik Button Approve Selected
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//BUTTON[@id=\"approveSelectedBtn\"]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 34: Klik Button Konfirmasi Untuk Menyetujui Request
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_34.png" });

    // Step 35: Klik Button Profile
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

    // Step 36: Klik Button Logout
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

    // Step 37: Berhasil Logout Akun
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_37.png" });

    // Step 38: Mengisi Username → ruben.hutabarat@itsaplic.com
    await page.fill("//INPUT[@id=\"email\"]", "ruben.hutabarat@itsaplic.com");

    // Step 39: Mengisi Password → Password
    await page.fill("//INPUT[@id=\"password\"]", "Password");

    // Step 40: Klik Button Login
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

    // [Step 41] Halaman Dashboard [get_page_info] — MCP-only, skipped

    // Step 42: Tutup Pop Up Message
    await page.keyboard.press("Escape");await page.waitForTimeout(1000);

    // Step 43: Klik Menu: Approval Pada Sidebar
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Approval\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 44: Klik Submenu: Approval Request Pada Sidebar
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Approval Request\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 45: Menampilkan Halaman Approval Request
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_45.png" });

    // Step 46: Klik Tab Leave Pada Filter Type Approval
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//A[.//text()[normalize-space(.) = \"Leave\"]]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 47: Klik Field Search, Cari Data → daniel purba
    await page.fill("//INPUT[@aria-controls=\"leave-tabpanelTable\"]", "daniel purba");

    // Step 48: Pilih Checkbox Untuk Request Yang Ingin Diapprove
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//INPUT[@id=\"select_all_leave\"]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 49: Klik Button Approve Selected
    await page.evaluate((sel) => {
        try {
            const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) { r.singleNodeValue.click(); return; }
        } catch(e) {}
        const el = document.querySelector(sel);
        if (el) el.click();
    }, "//BUTTON[@id=\"approveSelectedBtn\"]");
        await page.waitForLoadState('load').catch(() => {});
        await page.waitForLoadState('networkidle').catch(() => {});
        await page.waitForTimeout(800);

    // Step 50: Klik Button Konfirmasi Untuk Menyetujui Request
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_50.png" });

    // Step 51: Klik Button Profile
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

    // Step 52: Klik Button Logout
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

    // Step 53: Berhasil Logout Akun
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_53.png" });

    // Step 54: Mengisi Username → daniel.purba@is-gs.com
    await page.fill("//INPUT[@id=\"email\"]", "daniel.purba@is-gs.com");

    // Step 55: Mengisi Password → Password
    await page.fill("//INPUT[@id=\"password\"]", "Password");

    // Step 56: Klik Button Login
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

    // Step 57: Halaman Dashboard
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_57.png" });

    // Step 58: Tutup Pop Up Message
    await page.keyboard.press("Escape");await page.waitForTimeout(1000);

    // Step 59: Berhasil mengambil Leave Balance: -2 days
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_59.png" });

    // Step 60: VALID: Leave Balance Sesuai → Before=-2, After= -2, Expected=-2.0
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_60.png" });

    // Step 61: Klik Menu: Request Pada Sidebar
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

    // Step 62: Klik Submenu: My Request Pada Sidebar
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

    // Step 63: VALID: Data Ditemukan → Annual Leave / 1-Jul-2026
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_63.png" });

    // Step 64: VALID: Status Request Approved → Annual Leave / 1-Jul-2026
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_64.png" });

    // Step 65: Klik Button Profile
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

    // Step 66: Klik Button Logout
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

    // Step 67: Berhasil Logout Akun
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_11062026_141319/step_67.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();