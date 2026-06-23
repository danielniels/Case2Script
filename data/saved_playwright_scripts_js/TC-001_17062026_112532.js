// Auto-generated Playwright script — TC-001_17062026_112532
// Generated: 2026-06-17 11:26:30
// Source: TC-001_17062026_112532.json
// Run: node TC-001_17062026_112532.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_playwright_scripts/screenshots/TC-001_17062026_112532', { recursive: true });

async function runTest() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ ignoreHTTPSErrors: true });
  const page = await context.newPage();

  try {

    // Step 1: http://127.0.0.1:5500/POC%20-%20BKPM%20-%20OSS%20v2%20ProbisKAK.html
    console.log('▶ STEP 1');
    await page.goto("http://127.0.0.1:5500/POC%20-%20BKPM%20-%20OSS%20v2%20ProbisKAK.html", { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_1.png" });

    // Step 2: Click: Masuk Sebagai Pelaku Usaha
    console.log('▶ STEP 2');
    await page.evaluate((sel) => {
      let el;
      const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
      if (xsel.startsWith('//')) {
          const r = document.evaluate(xsel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(xsel);
      }
      if (el) el.click();
  }, "//button[.//text()[normalize-space(.) = \"Masuk sebagai Pelaku Usaha\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_2.png" });

    // Step 3: Click Button: Klik Tambah Lokasi (1A)
    console.log('▶ STEP 3');
    await page.evaluate((sel) => {
      let el;
      const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
      if (xsel.startsWith('//')) {
          const r = document.evaluate(xsel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(xsel);
      }
      if (el) el.click();
  }, "//button[.//text()[normalize-space(.) = \"Klik Tambah Lokasi (1A)\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_3.png" });

    // Step 4: Pilih Jenis Matra Posisi: Darat
    console.log('▶ STEP 4');
    await page.selectOption("//select[@id=\"lo-matra\"]", { label: "Darat" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_4.png" });

    // Step 5: Fill Luas Lahan Digunakan: 15000
    console.log('▶ STEP 5');
    await page.locator("#lo-luas").first().fill("15000");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_5.png" });

    // Step 6: Click Unggah Polygon Posisi Lokasi (.zip)
    console.log('▶ STEP 6');
    await page.evaluate((sel) => {
      let el;
      const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
      if (xsel.startsWith('//')) {
          const r = document.evaluate(xsel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(xsel);
      }
      if (el) el.click();
  }, "//div[@data-act=\"poly-upload\" and .//*[.//text()[normalize-space(.) = \"Klik untuk unggah berkas .zip\"]]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_6.png" });

    // Step 7: Mengisi Nama Lokasi -> Gudang Bekasi
    console.log('▶ STEP 7');
    await page.locator("#lo-nama").first().fill("Gudang Bekasi");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_7.png" });

    // Step 8: Mengisi Alamat Lengkap -> Jl. Raya Cibitung No. 47, Kec. Cibitung, Kab. Bekasi, Jawa Barat 17520
    console.log('▶ STEP 8');
    await page.locator("//textarea[@id=\"lo-alamat\"]").first().fill("Jl. Raya Cibitung No. 47, Kec. Cibitung, Kab. Bekasi, Jawa Barat 17520");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_8.png" });

    // Step 9: Mengisi Kabupaten/Kota -> Bekasi
    console.log('▶ STEP 9');
    await page.locator("#lo-kota").first().fill("Bekasi");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_9.png" });

    // Step 10: Mengisi Kecamatan -> Cibitung
    console.log('▶ STEP 10');
    await page.locator("#lo-kec").first().fill("Cibitung");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_10.png" });

    // Step 11: Mengisi Kelurahan -> Cibitung
    console.log('▶ STEP 11');
    await page.locator("#lo-kel").first().fill("Cibitung");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_11.png" });

    // Step 12: Mengisi Kode Pos -> 17520
    console.log('▶ STEP 12');
    await page.locator("#lo-pos").first().fill("17520");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_12.png" });

    // Step 13: Pilih Apakah Berada dalam Kawasan: Ya
    console.log('▶ STEP 13');
    await page.evaluate((sel) => {
      let el;
      const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
      if (xsel.startsWith('//')) {
          const r = document.evaluate(xsel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(xsel);
      }
      if (el) el.click();
  }, "#kw-ya").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_13.png" });

    // Step 14: Pilih Nama Kawasan: Kawasan Industri Jababeka
    console.log('▶ STEP 14');
    await page.selectOption("//select[@id=\"lo-kawasan\"]", { label: "Kawasan Industri Jababeka" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_14.png" });

    // Step 15: Click Button: Klik Tambah Posisi Lokasi
    console.log('▶ STEP 15');
    await page.evaluate((sel) => {
      let el;
      const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
      if (xsel.startsWith('//')) {
          const r = document.evaluate(xsel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(xsel);
      }
      if (el) el.click();
  }, "//button[.//text()[normalize-space(.) = \"Klik Tambah Button Posisi Lokasi\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_15.png" });

    // Step 16: Click Button: Tidak - ke Daftar Lokasi
    console.log('▶ STEP 16');
    await page.evaluate((sel) => {
      let el;
      const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
      if (xsel.startsWith('//')) {
          const r = document.evaluate(xsel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(xsel);
      }
      if (el) el.click();
  }, "//button[.//text()[normalize-space(.) = \"Tidak — ke Daftar Lokasi\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_17062026_112532/step_16.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();