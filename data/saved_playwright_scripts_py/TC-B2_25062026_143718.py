# Auto-generated Playwright script — TC-B2_25062026_143718
# Generated: 2026-06-25 14:41:30
# Source: TC-B2_25062026_143718.json
# Run: python TC-B2_25062026_143718.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: Menampilkan Halaman Login https://dev.itsaplic.com/login
            print('>> STEP 1')
            await page.goto('https://dev.itsaplic.com/login', wait_until='domcontentloaded')
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_1.png')

            # Step 2: Mengisi Username → daniel.purba@is-gs.com
            print('>> STEP 2')
            await page.locator('xpath=//input[@id="email"]').first.fill('daniel.purba@is-gs.com')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_2.png')

            # Step 3: Mengisi Password → Password
            print('>> STEP 3')
            await page.locator('xpath=//input[@id="password"]').first.fill('Password')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_3.png')

            # Step 4: Klik Button Login
            print('>> STEP 4')
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
            }""", '//button[@id="loginBtn"]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_4.png')

            # Step 5: Halaman Dashboard
            print('>> STEP 5')
            try:
                await page.wait_for_url('**/*dashboard*', timeout=8000)
            except Exception:
                pass
            if 'dashboard' not in page.url:
                raise AssertionError(f"assert_url failed — got: {page.url}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_5.png')

            # Step 6: Tutup Pop Up Message
            print('>> STEP 6')
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(1000)
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_6.png')

            # STEP 7 FAILED [assert_text] — fix manually before running
            # VALID: Leave Balance -2.0
            # t = (await page.locator('//body').first.inner_text()).strip()
            # if 'Leave Balance -2.0' not in t:
            #     raise AssertionError(f"assert_text failed — expected 'Leave Balance -2.0', got: {t}")

            # Step 8: Klik Request Leave Pada Dashboard
            print('>> STEP 8')
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
            }""", '//a[text()[normalize-space(.) = "Request leave"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_8.png')

            # Step 9: Klik Tab Menu Leave Request
            print('>> STEP 9')
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
            }""", '//a[text()[normalize-space(.) = "Leave Request"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_9.png')

            # Step 10: Klik Button Add Leave
            print('>> STEP 10')
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
            }""", '//button[text()[normalize-space(.) = "Add Leave Request"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_10.png')

            # Step 11: Memilih Type Leave → Annual Leave
            print('>> STEP 11')
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
            }""", {'sel': '//span[.//text()[normalize-space(.) = "Annual Leave"]]', 'val': 'Annual Leave'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_11.png')

            # Step 12: Mengisi Start Date → 30-Jul-2026
            print('>> STEP 12')
            await page.locator('//input[@id="request_start"]').first.fill('30-Jul-2026')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_12.png')

            # Step 13: Mengisi End Date → 30-Jul-2026
            print('>> STEP 13')
            await page.locator('//input[@id="request_end"]').first.fill('30-Jul-2026')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_13.png')

            # Step 14: Mengisi Detail Request → Test request sakit leave
            print('>> STEP 14')
            await page.locator('//textarea[@id="request_detail"]').first.fill('Test request sakit leave')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_14.png')

            # Step 15: Upload Supporting File → dummy.png
            print('>> STEP 15')
            await page.set_input_files('xpath=//input[@id="request_file"]', ['dummy.png'])
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_15.png')

            # Step 16: Klik Button Submit
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
            }""", '//button[@id="form-btn"]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_16.png')

            # STEP 17 FAILED [assert_text] — fix manually before running
            # VALID: Data Ditemukan → Sick Leave / 30-Jul-2026
            # t = (await page.locator('//body').first.inner_text()).strip()
            # if 'Sick Leave / 30-Jul-2026' not in t:
            #     raise AssertionError(f"assert_text failed — expected 'Sick Leave / 30-Jul-2026', got: {t}")

            # Step 18: Klik Button Profile
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
            }""", '//button[@id="page-header-user-dropdown"]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_18.png')

            # Step 19: Klik Button Logout
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
            }""", '//a[.//text()[normalize-space(.) = "Logout"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_25062026_143718/step_19.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
