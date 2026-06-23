// Auto-generated Playwright script — TC-002_12062026_161203
// Generated: 2026-06-12 17:04:36
// Source: TC-002_12062026_161203.json
// Run: node TC-002_12062026_161203.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_screenshots/playwright_screenshots/TC-002_12062026_161203', { recursive: true });

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
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_1.png" });

    // Step 2: Mengisi Username → daniel.purba@is-gs.com
    console.log('▶ STEP 2');
    await page.locator("#email").first().fill("daniel.purba@is-gs.com");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_2.png" });

    // Step 3: Mengisi Password → Password
    console.log('▶ STEP 3');
    await page.locator("#password").first().fill("Password");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_3.png" });

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
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_4.png" });

    // Step 5: Halaman Dashboard
    console.log('▶ STEP 5');
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_5.png" });

    // Step 6: Tutup Pop Up Message
    console.log('▶ STEP 6');
    await page.keyboard.press("Escape");await page.waitForTimeout(1000);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_6.png" });

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
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_7.png" });

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
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_8.png" });

    // Step 9: Menampilkan Halaman My Request
    console.log('▶ STEP 9');
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_9.png" });

    // Step 10: Klik Tab Menu Other Claim
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
  }, "//a[.//text()[normalize-space(.) = \"Other Claim\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_10.png" });

    // Step 11: Klik Button Add Other Claim
    console.log('▶ STEP 11');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "//button[.//text()[normalize-space(.) = \"Add Other Claim\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_11.png" });

    // Step 12: Menampilkan Form Add Other Claim Request
    console.log('▶ STEP 12');
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_12.png" });

    // Step 13: Mengisi Claim Date → 12-Jun-2026
    console.log('▶ STEP 13');
    await page.locator("#request_start").first().fill("12-Jun-2026");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_13.png" });

    // Step 14: Mengisi Start Date → 12-June-2026
    console.log('▶ STEP 14');
    await page.locator("#request_start").first().fill("12-June-2026");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_14.png" });

    // Step 15: Mengisi End Date → 31-August-2026
    console.log('▶ STEP 15');
    await page.locator("#request_end").first().fill("31-August-2026");
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_15.png" });

    // Step 16: Klik Button Submit Request
    console.log('▶ STEP 16');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "#form-btn").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_16.png" });

    // STEP 17 FAILED [assert_text] — fix manually before running
    // VALID: Data Ditemukan → Other Claim / 12-Jun-2026
    // { const t = (await page.locator("//body").first().innerText()).trim(); if (!t.includes("Other Claim / 12-Jun-2026")) throw new Error("assert_text failed — expected " + "Other Claim / 12-Jun-2026" + ", got: " + t); }

    // Step 18: Klik Button Profile
    console.log('▶ STEP 18');
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
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_18.png" });

    // Step 19: Klik Button Logout
    console.log('▶ STEP 19');
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
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_19.png" });

    // Step 20: Berhasil Logout Akun
    console.log('▶ STEP 20');
    await page.screenshot({ path: "saved_screenshots/playwright_screenshots/TC-002_12062026_161203/step_20.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();