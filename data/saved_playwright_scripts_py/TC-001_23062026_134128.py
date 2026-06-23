# Auto-generated Playwright script — TC-001_23062026_134128
# Generated: 2026-06-23 15:11:53
# Source: TC-001_23062026_134128.json
# Run: python TC-001_23062026_134128.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: http://127.0.0.1:5501/POC%20-%20BKPM%20-%20OSS%20v2%20ProbisKAK.html
            print('>> STEP 1')
            await page.goto('http://127.0.0.1:5501/POC%20-%20BKPM%20-%20OSS%20v2%20ProbisKAK.html', wait_until='domcontentloaded')
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_1.png')

            # Step 2: Click: Masuk Sebagai Pelaku Usaha
            print('>> STEP 2')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Masuk sebagai Pelaku Usaha"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_2.png')

            # Step 3: Click Button: Klik Tambah Lokasi (1A)
            print('>> STEP 3')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Klik Tambah Lokasi (1A)"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_3.png')

            # Step 4: Pilih Jenis Matra Posisi: Darat
            print('>> STEP 4')
            await page.evaluate("""({sel, val}) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
                const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (let i = 0; i < r.snapshotLength; i++) {
                    const node = r.snapshotItem(i);
                    if (isVisible(node)) { el = node; break; }
                }
              } else {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (isVisible(node)) { el = node; break; }
                }
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
            }""", {'sel': '//select[@id="lo-matra"]', 'val': 'Darat'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_4.png')

            # Step 5: Fill Luas Lahan Digunakan: 15000
            print('>> STEP 5')
            await page.locator('//input[@id="lo-luas"]').first.fill('15000')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_5.png')

            # Step 6: Click Unggah Polygon Posisi Lokasi (.zip)
            print('>> STEP 6')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//div[@data-act="poly-upload" and .//*[.//text()[normalize-space(.) = "Klik untuk unggah berkas .zip"]]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_6.png')

            # Step 7: Mengisi Nama Lokasi -> Gudang Bekasi
            print('>> STEP 7')
            await page.locator('//input[@id="lo-nama"]').first.fill('Gudang Bekasi')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_7.png')

            # Step 8: Mengisi Alamat Lengkap -> Jl. Raya Cibitung No. 47, Kec. Cibitung, Kab. Bekasi, Jawa Barat 17520
            print('>> STEP 8')
            await page.locator('//textarea[@id="lo-alamat"]').first.fill('Jl. Raya Cibitung No. 47, Kec. Cibitung, Kab. Bekasi, Jawa Barat 17520')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_8.png')

            # Step 9: Mengisi Kabupaten/Kota -> Bekasi
            print('>> STEP 9')
            await page.locator('//input[@id="lo-kota"]').first.fill('Bekasi')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_9.png')

            # Step 10: Mengisi Kecamatan -> Cibitung
            print('>> STEP 10')
            await page.locator('//input[@id="lo-kec"]').first.fill('Cibitung')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_10.png')

            # Step 11: Mengisi Kelurahan -> Cibitung
            print('>> STEP 11')
            await page.locator('//input[@id="lo-kel"]').first.fill('Cibitung')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_11.png')

            # Step 12: Mengisi Kode Pos -> 17520
            print('>> STEP 12')
            await page.locator('//input[@id="lo-pos"]').first.fill('17520')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_12.png')

            # Step 13: Pilih Apakah Berada dalam Kawasan: Ya
            print('>> STEP 13')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//div[@id="kw-ya"]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_13.png')

            # Step 14: Pilih Nama Kawasan: Kawasan Industri Jababeka
            print('>> STEP 14')
            await page.evaluate("""({sel, val}) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
                const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (let i = 0; i < r.snapshotLength; i++) {
                    const node = r.snapshotItem(i);
                    if (isVisible(node)) { el = node; break; }
                }
              } else {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (isVisible(node)) { el = node; break; }
                }
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
            }""", {'sel': '//select[@id="lo-kawasan"]', 'val': 'Kawasan Industri Jababeka'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_14.png')

            # Step 15: Click Button: Klik Tambah Posisi Lokasi
            print('>> STEP 15')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Klik Tambah Button Posisi Lokasi"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_15.png')

            # Step 16: Click Button: Tidak - ke Daftar Lokasi
            print('>> STEP 16')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Tidak — ke Daftar Lokasi"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_16.png')

            # Step 17: Click Button: Lanjut Pilih Lokasi untuk Kegiatan
            print('>> STEP 17')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Lanjut: Pilih Lokasi untuk Kegiatan"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_17.png')

            # Step 18: Pilih Lokasi untuk Kegiatan: Gudang Bekasi
            print('>> STEP 18')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//div[@data-act="pick" and .//*[.//text()[normalize-space(.) = "Gudang Bekasi"]]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_18.png')

            # Step 19: Click Lanjut Detail Kegiatan
            print('>> STEP 19')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Klik Lanjut Detail Kegiatan"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_19.png')

            # Step 20: Pilih Status Objek Vital Nasional: Objek Vital Nasional
            print('>> STEP 20')
            await page.evaluate("""({sel, val}) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
                const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (let i = 0; i < r.snapshotLength; i++) {
                    const node = r.snapshotItem(i);
                    if (isVisible(node)) { el = node; break; }
                }
              } else {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (isVisible(node)) { el = node; break; }
                }
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
            }""", {'sel': '//select[@id="f-ovn"]', 'val': 'Objek Vital Nasional'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_20.png')

            # Step 21: Pilih Status Proyek Strategis Nasional (PSN): PSN
            print('>> STEP 21')
            await page.evaluate("""({sel, val}) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
                const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (let i = 0; i < r.snapshotLength; i++) {
                    const node = r.snapshotItem(i);
                    if (isVisible(node)) { el = node; break; }
                }
              } else {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (isVisible(node)) { el = node; break; }
                }
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
            }""", {'sel': '//select[@id="f-psn"]', 'val': 'PSN'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_21.png')

            # Step 22: Klik tombol Cek RDTR
            print('>> STEP 22')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Cek RDTR"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_22.png')

            # Step 23: Verifikasi: RDTR tersedia muncul di halaman
            print('>> STEP 23')
            if not await page.locator('//button[text()[normalize-space(.) = "Cek RDTR"]]').first.is_visible():
                raise AssertionError(f"assert_visible failed: '//button[text()[normalize-space(.) = "Cek RDTR"]]'")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_23.png')

            # Step 24: Pilih Jenis Kegiatan Usaha: Utama
            print('>> STEP 24')
            await page.evaluate("""({sel, val}) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
                const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (let i = 0; i < r.snapshotLength; i++) {
                    const node = r.snapshotItem(i);
                    if (isVisible(node)) { el = node; break; }
                }
              } else {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (isVisible(node)) { el = node; break; }
                }
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
            }""", {'sel': '//select[@id="k-jenis"]', 'val': 'Utama'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_24.png')

            # Step 25: Pilih Bidang Usaha (KBLI): 25120
            print('>> STEP 25')
            await page.evaluate("""({sel, val}) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
                const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (let i = 0; i < r.snapshotLength; i++) {
                    const node = r.snapshotItem(i);
                    if (isVisible(node)) { el = node; break; }
                }
              } else {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (isVisible(node)) { el = node; break; }
                }
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
            }""", {'sel': '//select[@id="k-kbli"]', 'val': '25120'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_25.png')

            # Step 26: Fill Nama Usaha/Kegiatan: teknologi maju
            print('>> STEP 26')
            await page.locator('//input[@id="k-nama"]').first.fill('teknologi maju')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_26.png')

            # Step 27: Pilih Skala Usaha (deklarasi): Besar
            print('>> STEP 27')
            await page.evaluate("""({sel, val}) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
                const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (let i = 0; i < r.snapshotLength; i++) {
                    const node = r.snapshotItem(i);
                    if (isVisible(node)) { el = node; break; }
                }
              } else {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (isVisible(node)) { el = node; break; }
                }
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
            }""", {'sel': '//select[@id="k-skala"]', 'val': 'Besar'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_27.png')

            # Step 28: Click button: Simpan Data (tambah ke Tabel List KBLI)
            print('>> STEP 28')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Simpan Data (tambah ke Tabel List KBLI)"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_28.png')

            # Step 29: Click button: Klik Proses
            print('>> STEP 29')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Klik Proses"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_29.png')

            # Step 30: Click button: KKPR Terbit (Verifikasi/RDTR Otomatis)
            print('>> STEP 30')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "KKPR Terbit (Verifikasi/RDTR Otomatis)"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_30.png')

            # Step 31: Click button: Lanjutkan Isi Data Kegiatan Usaha
            print('>> STEP 31')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = \'Klik "Lanjutkan Isi Data Kegiatan Usaha" (2A)\']]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_31.png')

            # Step 32: Isi Jangka Waktu Perkiraan Beroperasi/Berproduksi: 2026-06
            print('>> STEP 32')
            await page.locator('//input[@id="d-jangka"]').first.fill('2026-06')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_32.png')

            # Step 33: Fill Nilai Pembelian/Pematangan Tanah: 1000000
            print('>> STEP 33')
            await page.locator('//input[@id="i-tanah"]').first.fill('1000000')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_33.png')

            # Step 34: Fill Nilai Bangunan/Gedung: 20000000
            print('>> STEP 34')
            await page.locator('//input[@id="i-bangunan"]').first.fill('20000000')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_34.png')

            # Step 35: Fill Mesin/Peralatan Dalam Negeri: 500000
            print('>> STEP 35')
            await page.locator('//input[@id="i-mesindn"]').first.fill('500000')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_35.png')

            # Step 36: Fill Mesin/Peralatan Impor: 300000
            print('>> STEP 36')
            await page.locator('//input[@id="i-mesinimp"]').first.fill('300000')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_36.png')

            # Step 37: Isi Nilai Investasi Lain-Lain: 200000
            print('>> STEP 37')
            await page.locator('//input[@id="i-lain"]').first.fill('200000')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_37.png')

            # Step 38: Isi Modal Kerja 3 Bulan: 400000
            print('>> STEP 38')
            await page.locator('//input[@id="i-modalkerja"]').first.fill('400000')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_38.png')

            # Step 39: Isi TKI Laki-Laki: 10
            print('>> STEP 39')
            await page.locator('//input[@id="t-l"]').first.fill('10')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_39.png')

            # Step 40: Fill TKI Perempuan: 5
            print('>> STEP 40')
            await page.locator('//input[@id="t-p"]').first.fill('5')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_40.png')

            # Step 41: Fill Tenaga Kerja Asing: 2
            print('>> STEP 41')
            await page.locator('//input[@id="t-a"]').first.fill('2')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_41.png')

            # Step 42: Isi Jenis Produk/Jasa: Bejana Tekan
            print('>> STEP 42')
            await page.locator('//input[@id="p-nama"]').first.fill('Bejana Tekan')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_42.png')

            # Step 43: Isi Jumlah Kapasitas: 100
            print('>> STEP 43')
            await page.locator('//input[@id="p-kap"]').first.fill('100')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_43.png')

            # Step 44: Pilih Satuan: Unit/Tahun
            print('>> STEP 44')
            await page.evaluate("""({sel, val}) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
                const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (let i = 0; i < r.snapshotLength; i++) {
                    const node = r.snapshotItem(i);
                    if (isVisible(node)) { el = node; break; }
                }
              } else {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (isVisible(node)) { el = node; break; }
                }
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
            }""", {'sel': '//select[@id="p-sat"]', 'val': 'Unit/Tahun'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_44.png')

            # Step 45: Klik Button: Proses (tambah ke Tabel Produk/Jasa)
            print('>> STEP 45')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Button Proses (tambah ke Tabel Produk/Jasa)"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_45.png')

            # Step 46: Klik Button: Trigger Validasi Risiko & Skala Usaha
            print('>> STEP 46')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Button Trigger Validasi Risiko & Skala Usaha"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_46.png')

            # Step 47: Pilih Status Kepemilikan Perizinan Lingkungan: Sudah
            print('>> STEP 47')
            await page.evaluate("""({sel, val}) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
                const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (let i = 0; i < r.snapshotLength; i++) {
                    const node = r.snapshotItem(i);
                    if (isVisible(node)) { el = node; break; }
                }
              } else {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (isVisible(node)) { el = node; break; }
                }
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
            }""", {'sel': '//select[@id="l-status"]', 'val': 'Sudah'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_47.png')

            # Step 48: Pilih Jenis Kegiatan (Peruntukan Penggunaan Lingkungan): Perdagangan/Jasa
            print('>> STEP 48')
            await page.evaluate("""({sel, val}) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
                const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (let i = 0; i < r.snapshotLength; i++) {
                    const node = r.snapshotItem(i);
                    if (isVisible(node)) { el = node; break; }
                }
              } else {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (isVisible(node)) { el = node; break; }
                }
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
            }""", {'sel': '//select[@id="l-jenis"]', 'val': 'Perdagangan/Jasa'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_48.png')

            # Step 49: Pilih Parameter Lingkungan: Skala menengah
            print('>> STEP 49')
            await page.evaluate("""({sel, val}) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              if (sel.startsWith('//') || sel.startsWith('xpath=')) {
                const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
                const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for (let i = 0; i < r.snapshotLength; i++) {
                    const node = r.snapshotItem(i);
                    if (isVisible(node)) { el = node; break; }
                }
              } else {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (isVisible(node)) { el = node; break; }
                }
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
            }""", {'sel': '//select[@id="l-param"]', 'val': 'Skala menengah'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_49.png')

            # Step 50: Centang checkbox: Pernyataan K3L (Keselamatan, Kesehatan Kerja & Lingkungan)
            print('>> STEP 50')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", 'xpath=//input[@type="checkbox" and (@id=(//label[contains(., "Pernyataan K3L (Keselamatan, Kesehatan Kerja & Lingkungan)")]/@for) or ancestor::label[contains(., "Pernyataan K3L (Keselamatan, Kesehatan Kerja & Lingkungan)")])]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_50.png')

            # Step 51: Centang checkbox: Pernyataan Kesediaan Memenuhi Standar Usaha
            print('>> STEP 51')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", 'xpath=//input[@type="checkbox" and (@id=(//label[contains(., "Pernyataan Kesediaan Memenuhi Standar Usaha")]/@for) or ancestor::label[contains(., "Pernyataan Kesediaan Memenuhi Standar Usaha")])]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_51.png')

            # Step 52: Centang checkbox: Pernyataan SPPL
            print('>> STEP 52')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", 'xpath=//input[@type="checkbox" and (@id=(//label[contains(., "Pernyataan SPPL")]/@for) or ancestor::label[contains(., "Pernyataan SPPL")])]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_52.png')

            # Step 53: Click Button: Proses -> Penertiban NIB
            print('>> STEP 53')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Klik Proses → Penerbitan NIB"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_53.png')

            # Step 54: Click Button: Lanjut Perizinan Berusaha
            print('>> STEP 54')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Lanjut: Perizinan Berusaha"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_54.png')

            # Step 55: Klik untuk unggah Dokumen pemenuhan SNI wajib produk (bejana tekan)
            print('>> STEP 55')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", 'xpath=//div[@data-act="pb-upload" and .//b[contains(normalize-space(.), "Dokumen pemenuhan SNI wajib produk (bejana tekan)")]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_55.png')

            # Step 56: Klik untuk unggah Dokumen Sistem Manajemen K3
            print('>> STEP 56')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", 'xpath=//div[@data-act="pb-upload" and .//b[contains(normalize-space(.), "Dokumen Sistem Manajemen K3")]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_56.png')

            # Step 57: Klik untuk unggah Spesifikasi teknis & sertifikat material
            print('>> STEP 57')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", 'xpath=//div[@data-act="pb-upload" and .//b[contains(normalize-space(.), "Spesifikasi teknis & sertifikat material")]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_57.png')

            # Step 58: Klik untuk unggah Pernyataan pemenuhan standar pelaksanaan kegiatan usaha
            print('>> STEP 58')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", 'xpath=//div[@data-act="pb-upload" and .//b[contains(normalize-space(.), "Pernyataan pemenuhan standar pelaksanaan kegiatan usaha")]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_58.png')

            # Step 59: Click Button: Kirim untuk Verifikasi Perizinan Berusaha
            print('>> STEP 59')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Kirim untuk Verifikasi Perizinan Berusaha"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_59.png')

            # Step 60: Klik tab Petugas K/L
            print('>> STEP 60')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Petugas K/L · 1"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_60.png')

            # Step 61: Click Button: Memenuhi → Terbitkan
            print('>> STEP 61')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Memenuhi → Terbitkan"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_61.png')

            # Step 62: Click tab Pelaku Usaha
            print('>> STEP 62')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Pelaku Usaha"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_62.png')

            # Step 63: Click Button: Lihat Perizinan Terbit
            print('>> STEP 63')
            try:
                await page.evaluate("""(sel) => {
              function isVisible(node) {
                const s = window.getComputedStyle(node);
                return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
              }
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                  for (let i = 0; i < r.snapshotLength; i++) {
                      const node = r.snapshotItem(i);
                      if (isVisible(node)) { el = node; break; }
                  }
              } else {
                  const nodes = document.querySelectorAll(xsel);
                  for (const node of nodes) {
                      if (isVisible(node)) { el = node; break; }
                  }
              }
              if (el) el.click();
            }""", '//button[text()[normalize-space(.) = "Lihat Perizinan Terbit"]]')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.wait_for_timeout(800)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_63.png')

            # Step 64: Verifikasi muncul: Kegiatan usaha Industri Tangki, Tandon & Wadah Logam (Bejana Tekan) kini aktif dan dapat melaksanakan kegiatan operasional/komersial
            print('>> STEP 64')
            t = (await page.locator('//body').first.inner_text()).strip()
            if 'Kegiatan usaha Industri Tangki, Tandon & Wadah Logam (Bejana Tekan) kini aktif dan dapat melaksanakan kegiatan operasional/komersial' not in t:
                raise AssertionError(f"assert_text failed — expected 'Kegiatan usaha Industri Tangki, Tandon & Wadah Logam (Bejana Tekan) kini aktif dan dapat melaksanakan kegiatan operasional/komersial', got: {t}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-001_23062026_134128/step_64.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
