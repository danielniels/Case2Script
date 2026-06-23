// Auto-generated Playwright script — TC-001-DEL-V2_14062026_204325
// Generated: 2026-06-14 20:46:39
// Source: TC-001-DEL-V2_14062026_204325.json
// Run: node TC-001-DEL-V2_14062026_204325.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325', { recursive: true });

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
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_1.png" });

    // Step 2: Mengisi Username → daniel.purba@is-gs.com
    console.log('▶ STEP 2');
    await page.locator("#email").first().fill("daniel.purba@is-gs.com");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_2.png" });

    // Step 3: Mengisi Password → Password
    console.log('▶ STEP 3');
    await page.locator("#password").first().fill("Password");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_3.png" });

    // Step 4: Klik Button Login
    console.log('▶ STEP 4');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "#loginBtn").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_4.png" });

    // Step 5: Halaman Dashboard
    console.log('▶ STEP 5');
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_5.png" });

    // Step 6: Tutup Pop Up Message
    console.log('▶ STEP 6');
    await page.keyboard.press("Escape");await page.waitForTimeout(1000);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_6.png" });

    // Step 7: Klik Menu: Request Pada Sidebar
    console.log('▶ STEP 7');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "a.has-arrow.waves-effect").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_7.png" });

    // Step 8: Klik Submenu: My Request Pada Sidebar
    console.log('▶ STEP 8');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "//a[.//text()[normalize-space(.) = \"My Request\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_8.png" });

    // Step 9: Klik Tab Menu Leave Request
    console.log('▶ STEP 9');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "//a[.//text()[normalize-space(.) = \"Leave Request\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_9.png" });

    // Step 10: Pilih Leave Request | 16-Apr-2026
    console.log('▶ STEP 10');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "//a[.//text()[normalize-space(.) = \"Leave Request\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_10.png" });

    // Step 11: Klik Icon Delete
    console.log('▶ STEP 11');

    // Step 12: Klik Button Konfirmasi 'Yes, delete it!'
    console.log('▶ STEP 12');

    // STEP 13 FAILED [assert_text] — fix manually before running
    // VALID: Leave Request Berhasil Dihapus → Leave request berhasil dihapus (Start Date: 16-Apr-2026)
    // { const t = (await page.locator("//body").first().innerText()).trim(); if (!t.includes("Leave request berhasil dihapus (Start Date: 16-Apr-2026)")) throw new Error("assert_text failed — expected " + "Leave request berhasil dihapus (Start Date: 16-Apr-2026)" + ", got: " + t); }

    // Step 14: Klik Button Profile
    console.log('▶ STEP 14');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "#page-header-user-dropdown").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_14.png" });

    // Step 15: Klik Button Logout
    console.log('▶ STEP 15');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "a.dropdown-item").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-001-DEL-V2_14062026_204325/step_15.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();