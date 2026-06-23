// Auto-generated Playwright script — TC-001_15062026_145927
// Generated: 2026-06-15 15:02:47
// Source: TC-001_15062026_145927.json
// Run: node TC-001_15062026_145927.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_playwright_scripts/screenshots/TC-001_15062026_145927', { recursive: true });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_1.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_2.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_3.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_4.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_5.png" });

    // Step 6: Gambar polygon batas lahan di zona Kawasan Industri [JS:drawPoly=[{x:100,y:80},{x:220,y:80},{x:160,y:220}];window._redrawMap();]
    console.log('▶ STEP 6');

    // Step 7: Mengisi Nama Lokasi -> Gudang Bekasi
    console.log('▶ STEP 7');
    await page.locator("#lo-nama").first().fill("Gudang Bekasi");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_7.png" });

    // Step 8: Mengisi Alamat Lengkap -> Jl. Raya Cibitung No. 47, Kec. Cibitung, Kab. Bekasi, Jawa Barat 17520
    console.log('▶ STEP 8');
    await page.locator("//textarea[@id=\"lo-alamat\"]").first().fill("Jl. Raya Cibitung No. 47, Kec. Cibitung, Kab. Bekasi, Jawa Barat 17520");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_8.png" });

    // Step 9: Mengisi Kabupaten/Kota -> Bekasi
    console.log('▶ STEP 9');
    await page.locator("#lo-kota").first().fill("Bekasi");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_9.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_10.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_11.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_12.png" });

    // Step 13: Pilih lokasi Gudang Bekasi
    console.log('▶ STEP 13');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "div.card").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_13.png" });

    // Step 14: Klik tombol Lanjut
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
  }, "//button[.//text()[normalize-space(.) = \"Lanjut\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_14.png" });

    // Step 15: Click Button Lanjut ke persetujuan
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
  }, "//button[.//text()[normalize-space(.) = \"Lanjut ke persetujuan\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_15.png" });

    // Step 16: Centang checkbox id w-s1: data yang diisi benar
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
  }, "#w-s1").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_16.png" });

    // Step 17: Centang checkbox id w-s2: kesanggupan memenuhi standar
    console.log('▶ STEP 17');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "#w-s2").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_17.png" });

    // Step 18: Click Button Daftarkan & Proses Klasifikasi
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
  }, "//button[.//text()[normalize-space(.) = \"Daftarkan & Proses Klasifikasi\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_18.png" });

    // Step 19: Click Tab Menu Persyaratan Dasar
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
  }, "//button[.//text()[normalize-space(.) = \"Persyaratan Dasar\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_19.png" });

    // Step 20: Click Unggah dokumen UKL-UPL
    console.log('▶ STEP 20');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "div.upload").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_20.png" });

    // Step 21: Klik Isi data & bayar retribusi
    console.log('▶ STEP 21');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "//button[.//text()[normalize-space(.) = \"Isi data & bayar retribusi\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_21.png" });

    // Step 22: Klik Jadwalkan inspeksi SLF
    console.log('▶ STEP 22');
    await page.evaluate((sel) => {
      let el;
      if (sel.startsWith('//')) {
          const r = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
          el = r.singleNodeValue;
      } else {
          el = document.querySelector(sel);
      }
      if (el) el.click();
  }, "//button[.//text()[normalize-space(.) = \"Jadwalkan inspeksi SLF\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_15062026_145927/step_22.png" });

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();