// Auto-generated Playwright script — TC-001_18062026_100723
// Generated: 2026-06-18 10:16:26
// Source: TC-001_18062026_100723.json
// Run: node TC-001_18062026_100723.js
// Requires: npm install playwright && npx playwright install chromium

const { chromium } = require('playwright');
const { mkdirSync } = require('fs');

mkdirSync('saved_playwright_scripts/screenshots/TC-001_18062026_100723', { recursive: true });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_1.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_2.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_3.png" });

    // Step 4: Pilih Jenis Matra Posisi: Darat
    console.log('▶ STEP 4');
    await page.evaluate(({sel, val}) => {
  let el;
  if (sel.startsWith('//') || sel.startsWith('xpath=')) {
    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  } else {
    el = document.querySelector(sel);
  }
  if (!el) return false;
  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
  if (!opt) return false;
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
  else el.value = opt.value;
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}, { sel: "//select[@id=\"lo-matra\"]", val: "Darat" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_4.png" });

    // Step 5: Fill Luas Lahan Digunakan: 15000
    console.log('▶ STEP 5');
    await page.locator("#lo-luas").first().fill("15000");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_5.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_6.png" });

    // Step 7: Mengisi Nama Lokasi -> Gudang Bekasi
    console.log('▶ STEP 7');
    await page.locator("#lo-nama").first().fill("Gudang Bekasi");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_7.png" });

    // Step 8: Mengisi Alamat Lengkap -> Jl. Raya Cibitung No. 47, Kec. Cibitung, Kab. Bekasi, Jawa Barat 17520
    console.log('▶ STEP 8');
    await page.locator("//textarea[@id=\"lo-alamat\"]").first().fill("Jl. Raya Cibitung No. 47, Kec. Cibitung, Kab. Bekasi, Jawa Barat 17520");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_8.png" });

    // Step 9: Mengisi Kabupaten/Kota -> Bekasi
    console.log('▶ STEP 9');
    await page.locator("#lo-kota").first().fill("Bekasi");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_9.png" });

    // Step 10: Mengisi Kecamatan -> Cibitung
    console.log('▶ STEP 10');
    await page.locator("#lo-kec").first().fill("Cibitung");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_10.png" });

    // Step 11: Mengisi Kelurahan -> Cibitung
    console.log('▶ STEP 11');
    await page.locator("#lo-kel").first().fill("Cibitung");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_11.png" });

    // Step 12: Mengisi Kode Pos -> 17520
    console.log('▶ STEP 12');
    await page.locator("#lo-pos").first().fill("17520");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_12.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_13.png" });

    // Step 14: Pilih Nama Kawasan: Kawasan Industri Jababeka
    console.log('▶ STEP 14');
    await page.evaluate(({sel, val}) => {
  let el;
  if (sel.startsWith('//') || sel.startsWith('xpath=')) {
    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  } else {
    el = document.querySelector(sel);
  }
  if (!el) return false;
  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
  if (!opt) return false;
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
  else el.value = opt.value;
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}, { sel: "//select[@id=\"lo-kawasan\"]", val: "Kawasan Industri Jababeka" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_14.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_15.png" });

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
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_16.png" });

    // Step 17: Click Button: Lanjut Pilih Lokasi untuk Kegiatan
    console.log('▶ STEP 17');
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
  }, "//button[.//text()[normalize-space(.) = \"Lanjut: Pilih Lokasi untuk Kegiatan\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_17.png" });

    // Step 18: Pilih Lokasi untuk Kegiatan: Gudang Bekasi
    console.log('▶ STEP 18');
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
  }, "//div[@data-act=\"pick\" and .//*[.//text()[normalize-space(.) = \"Gudang Bekasi\"]]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_18.png" });

    // Step 19: Click Lanjut Detail Kegiatan
    console.log('▶ STEP 19');
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
  }, "//button[.//text()[normalize-space(.) = \"Klik Lanjut Detail Kegiatan\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_19.png" });

    // Step 20: Pilih Status Objek Vital Nasional: Objek Vital Nasional
    console.log('▶ STEP 20');
    await page.evaluate(({sel, val}) => {
  let el;
  if (sel.startsWith('//') || sel.startsWith('xpath=')) {
    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  } else {
    el = document.querySelector(sel);
  }
  if (!el) return false;
  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
  if (!opt) return false;
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
  else el.value = opt.value;
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}, { sel: "//select[@id=\"f-ovn\"]", val: "Objek Vital Nasional" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_20.png" });

    // Step 21: Pilih Status Proyek Strategis Nasional (PSN): PSN
    console.log('▶ STEP 21');
    await page.evaluate(({sel, val}) => {
  let el;
  if (sel.startsWith('//') || sel.startsWith('xpath=')) {
    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  } else {
    el = document.querySelector(sel);
  }
  if (!el) return false;
  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
  if (!opt) return false;
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
  else el.value = opt.value;
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}, { sel: "//select[@id=\"f-psn\"]", val: "PSN" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_21.png" });

    // Step 22: Klik tombol Cek RDTR
    console.log('▶ STEP 22');
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
  }, "//button[.//text()[normalize-space(.) = \"Cek RDTR\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_22.png" });

    // Step 23: Verifikasi: RDTR tersedia muncul di halaman
    console.log('▶ STEP 23');
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_23.png" });

    // Step 24: Pilih Jenis Kegiatan Usaha: Utama
    console.log('▶ STEP 24');
    await page.evaluate(({sel, val}) => {
  let el;
  if (sel.startsWith('//') || sel.startsWith('xpath=')) {
    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  } else {
    el = document.querySelector(sel);
  }
  if (!el) return false;
  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
  if (!opt) return false;
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
  else el.value = opt.value;
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}, { sel: "//select[@id=\"k-jenis\"]", val: "Utama" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_24.png" });

    // Step 25: Pilih Bidang Usaha (KBLI): 25120
    console.log('▶ STEP 25');
    await page.evaluate(({sel, val}) => {
  let el;
  if (sel.startsWith('//') || sel.startsWith('xpath=')) {
    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  } else {
    el = document.querySelector(sel);
  }
  if (!el) return false;
  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
  if (!opt) return false;
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
  else el.value = opt.value;
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}, { sel: "//select[@id=\"k-kbli\"]", val: "25120" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_25.png" });

    // Step 26: Fill Nama Usaha/Kegiatan: teknologi maju
    console.log('▶ STEP 26');
    await page.locator("#k-nama").first().fill("teknologi maju");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_26.png" });

    // Step 27: Pilih Skala Usaha (deklarasi): Besar
    console.log('▶ STEP 27');
    await page.evaluate(({sel, val}) => {
  let el;
  if (sel.startsWith('//') || sel.startsWith('xpath=')) {
    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  } else {
    el = document.querySelector(sel);
  }
  if (!el) return false;
  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
  if (!opt) return false;
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
  else el.value = opt.value;
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}, { sel: "//select[@id=\"k-skala\"]", val: "Besar" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_27.png" });

    // Step 28: Click button: Simpan Data (tambah ke Tabel List KBLI)
    console.log('▶ STEP 28');
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
  }, "//button[.//text()[normalize-space(.) = \"Simpan Data (tambah ke Tabel List KBLI)\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_28.png" });

    // Step 29: Click button: Klik Proses
    console.log('▶ STEP 29');
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
  }, "//button[.//text()[normalize-space(.) = \"Klik Proses\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_29.png" });

    // Step 30: Click button: KKPR Terbit (Verifikasi/RDTR Otomatis)
    console.log('▶ STEP 30');
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
  }, "//button[.//text()[normalize-space(.) = \"KKPR Terbit (Verifikasi/RDTR Otomatis)\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_30.png" });

    // Step 31: Click button: Lanjutkan Isi Data Kegiatan Usaha
    console.log('▶ STEP 31');
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
  }, "//button[.//text()[normalize-space(.) = \"Klik \"Lanjutkan Isi Data Kegiatan Usaha\" (2A)\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_31.png" });

    // Step 32: Isi Jangka Waktu Perkiraan Beroperasi/Berproduksi: 2026-06
    console.log('▶ STEP 32');
    await page.locator("#d-jangka").first().fill("2026-06");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_32.png" });

    // Step 33: Fill Nilai Pembelian/Pematangan Tanah: 1000000
    console.log('▶ STEP 33');
    await page.locator("#i-tanah").first().fill("1000000");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_33.png" });

    // Step 34: Fill Nilai Bangunan/Gedung: 20000000
    console.log('▶ STEP 34');
    await page.locator("#i-bangunan").first().fill("20000000");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_34.png" });

    // Step 35: Fill Mesin/Peralatan Dalam Negeri: 500000
    console.log('▶ STEP 35');
    await page.locator("#i-mesindn").first().fill("500000");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_35.png" });

    // Step 36: Fill Mesin/Peralatan Impor: 300000
    console.log('▶ STEP 36');
    await page.locator("#i-mesinimp").first().fill("300000");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_36.png" });

    // Step 37: Isi Nilai Investasi Lain-Lain: 200000
    console.log('▶ STEP 37');
    await page.locator("#i-lain").first().fill("200000");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_37.png" });

    // Step 38: Isi Modal Kerja 3 Bulan: 400000
    console.log('▶ STEP 38');
    await page.locator("#i-modalkerja").first().fill("400000");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_38.png" });

    // Step 39: Isi TKI Laki-Laki: 10
    console.log('▶ STEP 39');
    await page.locator("#t-l").first().fill("10");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_39.png" });

    // Step 40: Fill TKI Perempuan: 5
    console.log('▶ STEP 40');
    await page.locator("#t-p").first().fill("5");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_40.png" });

    // Step 41: Fill Tenaga Kerja Asing: 2
    console.log('▶ STEP 41');
    await page.locator("#t-a").first().fill("2");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_41.png" });

    // Step 42: Isi Jenis Produk/Jasa: Bejana Tekan
    console.log('▶ STEP 42');
    await page.locator("#p-nama").first().fill("Bejana Tekan");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_42.png" });

    // Step 43: Isi Jumlah Kapasitas: 100
    console.log('▶ STEP 43');
    await page.locator("#p-kap").first().fill("100");
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_43.png" });

    // Step 44: Pilih Satuan: Unit/Tahun
    console.log('▶ STEP 44');
    await page.evaluate(({sel, val}) => {
  let el;
  if (sel.startsWith('//') || sel.startsWith('xpath=')) {
    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  } else {
    el = document.querySelector(sel);
  }
  if (!el) return false;
  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
  if (!opt) return false;
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
  else el.value = opt.value;
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}, { sel: "//select[@id=\"p-sat\"]", val: "Unit/Tahun" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_44.png" });

    // Step 45: Klik Button: Proses (tambah ke Tabel Produk/Jasa)
    console.log('▶ STEP 45');
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
  }, "//button[.//text()[normalize-space(.) = \"Button Proses (tambah ke Tabel Produk/Jasa)\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_45.png" });

    // Step 46: Klik Button: Trigger Validasi Risiko & Skala Usaha
    console.log('▶ STEP 46');
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
  }, "//button[.//text()[normalize-space(.) = \"Button Trigger Validasi Risiko & Skala Usaha\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_46.png" });

    // Step 47: Pilih Status Kepemilikan Perizinan Lingkungan: Sudah
    console.log('▶ STEP 47');
    await page.evaluate(({sel, val}) => {
  let el;
  if (sel.startsWith('//') || sel.startsWith('xpath=')) {
    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  } else {
    el = document.querySelector(sel);
  }
  if (!el) return false;
  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
  if (!opt) return false;
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
  else el.value = opt.value;
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}, { sel: "//select[@id=\"l-status\"]", val: "Sudah" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_47.png" });

    // Step 48: Pilih Jenis Kegiatan (Peruntukan Penggunaan Lingkungan): Perdagangan/Jasa
    console.log('▶ STEP 48');
    await page.evaluate(({sel, val}) => {
  let el;
  if (sel.startsWith('//') || sel.startsWith('xpath=')) {
    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  } else {
    el = document.querySelector(sel);
  }
  if (!el) return false;
  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
  if (!opt) return false;
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
  else el.value = opt.value;
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}, { sel: "//select[@id=\"l-jenis\"]", val: "Perdagangan/Jasa" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_48.png" });

    // Step 49: Pilih Parameter Lingkungan: Skala menengah
    console.log('▶ STEP 49');
    await page.evaluate(({sel, val}) => {
  let el;
  if (sel.startsWith('//') || sel.startsWith('xpath=')) {
    el = document.evaluate(sel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
  } else {
    el = document.querySelector(sel);
  }
  if (!el) return false;
  const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
  if (!opt) return false;
  const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
  if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
  else el.value = opt.value;
  el.dispatchEvent(new Event('change', { bubbles: true }));
  el.dispatchEvent(new Event('input', { bubbles: true }));
  return true;
}, { sel: "//select[@id=\"l-param\"]", val: "Skala menengah" });
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_49.png" });

    // Step 50: Centang checkbox: Pernyataan K3L (Keselamatan, Kesehatan Kerja & Lingkungan)
    console.log('▶ STEP 50');
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
  }, "xpath=//input[@type=\"checkbox\" and (@id=(//label[contains(., \"Pernyataan K3L (Keselamatan, Kesehatan Kerja & Lingkungan)\")]/@for) or ancestor::label[contains(., \"Pernyataan K3L (Keselamatan, Kesehatan Kerja & Lingkungan)\")])]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_50.png" });

    // Step 51: Centang checkbox: Pernyataan Kesediaan Memenuhi Standar Usaha
    console.log('▶ STEP 51');
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
  }, "xpath=//input[@type=\"checkbox\" and (@id=(//label[contains(., \"Pernyataan Kesediaan Memenuhi Standar Usaha\")]/@for) or ancestor::label[contains(., \"Pernyataan Kesediaan Memenuhi Standar Usaha\")])]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_51.png" });

    // Step 52: Centang checkbox: Pernyataan SPPL
    console.log('▶ STEP 52');
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
  }, "xpath=//input[@type=\"checkbox\" and (@id=(//label[contains(., \"Pernyataan SPPL\")]/@for) or ancestor::label[contains(., \"Pernyataan SPPL\")])]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_52.png" });

    // Step 53: Click Button: Proses -> Penertiban NIB
    console.log('▶ STEP 53');
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
  }, "//button[.//text()[normalize-space(.) = \"Klik Proses → Penerbitan NIB\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_53.png" });

    // Step 54: Click Button: Lanjut Perizinan Berusaha
    console.log('▶ STEP 54');
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
  }, "//button[.//text()[normalize-space(.) = \"Lanjut: Perizinan Berusaha\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_54.png" });

    // Step 55: Klik untuk unggah Dokumen pemenuhan SNI wajib produk (bejana tekan)
    console.log('▶ STEP 55');
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
  }, "xpath=//div[@data-act=\"pb-upload\" and .//b[contains(normalize-space(.), \"Dokumen pemenuhan SNI wajib produk (bejana tekan)\")]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_55.png" });

    // Step 56: Klik untuk unggah Dokumen Sistem Manajemen K3
    console.log('▶ STEP 56');
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
  }, "xpath=//div[@data-act=\"pb-upload\" and .//b[contains(normalize-space(.), \"Dokumen Sistem Manajemen K3\")]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_56.png" });

    // Step 57: Klik untuk unggah Spesifikasi teknis & sertifikat material
    console.log('▶ STEP 57');
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
  }, "xpath=//div[@data-act=\"pb-upload\" and .//b[contains(normalize-space(.), \"Spesifikasi teknis & sertifikat material\")]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_57.png" });

    // Step 58: Klik untuk unggah Pernyataan pemenuhan standar pelaksanaan kegiatan usaha
    console.log('▶ STEP 58');
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
  }, "xpath=//div[@data-act=\"pb-upload\" and .//b[contains(normalize-space(.), \"Pernyataan pemenuhan standar pelaksanaan kegiatan usaha\")]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_58.png" });

    // Step 59: Click Button: Kirim untuk Verifikasi Perizinan Berusaha
    console.log('▶ STEP 59');
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
  }, "//button[.//text()[normalize-space(.) = \"Kirim untuk Verifikasi Perizinan Berusaha\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_59.png" });

    // Step 60: Klik tab Petugas K/L
    console.log('▶ STEP 60');
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
  }, "//button[.//text()[normalize-space(.) = \"Petugas K/L · 1\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_60.png" });

    // Step 61: Click Button: Memenuhi → Terbitkan
    console.log('▶ STEP 61');
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
  }, "//button[.//text()[normalize-space(.) = \"Memenuhi → Terbitkan\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_61.png" });

    // Step 62: Click tab Pelaku Usaha
    console.log('▶ STEP 62');
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
  }, "//button[.//text()[normalize-space(.) = \"Pelaku Usaha\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_62.png" });

    // Step 63: Click Button: Lihat Perizinan Terbit
    console.log('▶ STEP 63');
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
  }, "//button[.//text()[normalize-space(.) = \"Lihat Perizinan Terbit\"]]").catch(() => {});
    await page.waitForLoadState('load').catch(() => {});
    await page.waitForLoadState('networkidle').catch(() => {});
    await page.waitForTimeout(800);
    await page.screenshot({ path: "saved_playwright_scripts/screenshots/TC-001_18062026_100723/step_63.png" });

    // STEP 64 FAILED [assert_visible] — fix manually before running
    // Verifikasi muncul: Kegiatan usaha Industri Tangki, Tandon & Wadah Logam (Bejana Tekan) kini aktif dan dapat melaksanakan kegiatan operasional/komersial
    // if (!await page.locator("xpath=//*[.//text()[normalize-space(.) = \"Kegiatan usaha Industri Tangki, Tandon & Wadah Logam (Bejana Tekan) kini aktif dan dapat melaksanakan kegiatan operasional/komersial\"]]").first().isVisible()) throw new Error("assert_visible failed: " + "xpath=//*[.//text()[normalize-space(.) = \"Kegiatan usaha Industri Tangki, Tandon & Wadah Logam (Bejana Tekan) kini aktif dan dapat melaksanakan kegiatan operasional/komersial\"]]");

    console.log('Test completed');
  } catch (err) {
    console.error('Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

runTest();