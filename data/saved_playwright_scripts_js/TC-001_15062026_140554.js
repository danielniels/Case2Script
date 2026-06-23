// Auto-generated Playwright script — TC-001_15062026_140554
// Generated: 2026-06-15 14:07:56
// Source: TC-001_15062026_140554.json
// Run: node TC-001_15062026_140554.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_playwright_scripts/screenshots/TC-001_15062026_140554', { recursive: true });

async function runTest() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();

  try {

    // Step 1: http://127.0.0.1:5500/OSS_2.0_POC.html#/login
    console.log('▶ STEP 1');
    await page.goto("http://127.0.0.1:5500/OSS_2.0_POC.html#/login", { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_1.png" });

    // Step 2: Click: Masuk Sebagai Pelaku Usaha
    console.log('▶ STEP 2');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "//button[.//text()[normalize-space(.) = \"Masuk sebagai Pelaku Usaha\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_2.png" });

    // Step 3: Click Menu: Kegiatan Usaha
    console.log('▶ STEP 3');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "//a[.//text()[normalize-space(.) = \"Kegiatan Usaha\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_3.png" });

    // Step 4: Click Button Tambah Kegiatan Usaha
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
  }, "//button[.//text()[normalize-space(.) = \"Tambah Kegiatan Usaha\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_4.png" });

    // Step 5: Click Button Tambah lokasi baru
    console.log('▶ STEP 5');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "button.card").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_5.png" });

    // Step 6: Gambar polygon batas lahan di zona Kawasan Industri [JS:drawPoly=[{x:100,y:80},{x:220,y:80},{x:160,y:220}];window._redrawMap();]
    console.log('▶ STEP 6');

    // Step 7: Mengisi Nama Lokasi -> Gudang Bekasi
    console.log('▶ STEP 7');
    await page.locator("#lo-nama").first().fill("Gudang Bekasi");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_7.png" });

    // Step 8: Mengisi Alamat Lengkap -> Jl. Raya Cibitung No. 47, Kec. Cibitung, Kab. Bekasi, Jawa Barat 17520
    console.log('▶ STEP 8');
    await page.locator("//textarea[@id=\"lo-alamat\"]").first().fill("Jl. Raya Cibitung No. 47, Kec. Cibitung, Kab. Bekasi, Jawa Barat 17520");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_8.png" });

    // Step 9: Mengisi Kabupaten/Kota -> Bekasi
    console.log('▶ STEP 9');
    await page.locator("#lo-kota").first().fill("Bekasi");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_9.png" });

    // Step 10: Click Button Simpan Lokasi
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
  }, "//button[.//text()[normalize-space(.) = \"Simpan Lokasi\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_10.png" });

    // Step 11: Click Menu: Kegiatan Usaha
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
  }, "//a[.//text()[normalize-space(.) = \"Kegiatan Usaha\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_11.png" });

    // Step 12: Click Button Tambah Kegiatan Usaha
    console.log('▶ STEP 12');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "//button[.//text()[normalize-space(.) = \"Tambah Kegiatan Usaha\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_12.png" });

    // Step 13: Click Card -> Gudang Bekasi
    console.log('▶ STEP 13');

    // Step 14: Pilih lokasi Gudang Bekasi
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
  }, "a.active").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_140554/step_14.png" });

    // Step 15: Klik tombol Lanjut
    console.log('▶ STEP 15');

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();