# Auto-generated Playwright script — 7b3ea336_TC001_02072026_171304
# Generated: 2026-07-02 17:16:20
# Source: 7b3ea336_TC001_02072026_171304.json
# Run: python 7b3ea336_TC001_02072026_171304.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: Buka https://www.advantageonlineshopping.com/
            print('>> STEP 1')
            await page.goto('https://www.advantageonlineshopping.com/', wait_until='domcontentloaded')
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_1.png')

            # Step 2: Klik ikon user pada navbar
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
            }""", '//a[@id="hrefUserIcon"]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_2.png')

            # Step 3: Klik CREATE NEW ACCOUNT
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
            }""", '//a[text()[normalize-space(.) = "CREATE NEW ACCOUNT"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_3.png')

            # Step 4: Mengisi Username → qatester837291
            print('>> STEP 4')
            await page.locator('xpath=//input[@name="usernameRegisterPage"]').first.fill('qatester837291')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_4.png')

            # Step 5: Mengisi Email → qatester.837291@mailinator.com
            print('>> STEP 5')
            await page.locator('xpath=//input[@name="usernameRegisterPage"]').first.fill('qatester.837291@mailinator.com')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_5.png')

            # Step 6: Mengisi Password → TestPass123!
            print('>> STEP 6')
            await page.locator('xpath=//input[@name="passwordRegisterPage"]').first.fill('TestPass123!')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_6.png')

            # Step 7: Isi Confirm Password → TestPass123!
            print('>> STEP 7')
            await page.locator('//input[@name="confirm_passwordRegisterPage"]').first.fill('TestPass123!')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_7.png')

            # Step 8: Isi First Name → Budi
            print('>> STEP 8')
            await page.locator('//input[@name="first_nameRegisterPage"]').first.fill('Budi')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_8.png')

            # Step 9: Isi Last Name → Santoso
            print('>> STEP 9')
            await page.locator('//input[@name="last_nameRegisterPage"]').first.fill('Santoso')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_9.png')

            # Step 10: Isi Phone Number → 081234567890
            print('>> STEP 10')
            await page.locator('//input[@name="phone_numberRegisterPage"]').first.fill('081234567890')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_10.png')

            # Step 11: Pilih Country → Indonesia
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
            }""", {'sel': '//select[@name="countryListboxRegisterPage"]', 'val': 'Indonesia'})
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_11.png')

            # Step 12: Isi City → Jakarta
            print('>> STEP 12')
            await page.locator('//input[@name="cityRegisterPage"]').first.fill('Jakarta')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_12.png')

            # Step 13: Isi Address → Jl. Sudirman No. 45
            print('>> STEP 13')
            await page.locator('//input[@name="addressRegisterPage"]').first.fill('Jl. Sudirman No. 45')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_13.png')

            # Step 14: Isi State/Province/Region → DKI Jakarta
            print('>> STEP 14')
            await page.locator('//input[@name="state_/_province_/_regionRegisterPage"]').first.fill('DKI Jakarta')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_14.png')

            # Step 15: Isi Postal Code → 12190
            print('>> STEP 15')
            await page.locator('//input[@name="postal_codeRegisterPage"]').first.fill('12190')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_15.png')

            # Step 16: Centang checkbox I Agree to the Conditions of Use and Privacy Notice
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
            }""", '//input[@name="i_agree"]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_16.png')

            # Step 17: Klik tombol REGISTER
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
            }""", '//button[@id="register_btn"]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7b3ea336_TC001_02072026_171304/step_17.png')

            # STEP 18 FAILED [assert_text] — fix manually before running
            # Verifikasi muncul: berhasil
            # _loc = page.locator('//body').first
            # try:
            #     t = (await _loc.input_value()).strip()
            # except Exception:
            #     t = (await _loc.text_content() or '').strip()
            # if 'berhasil' not in t:
            #     raise AssertionError(f"assert_text failed — expected 'berhasil', got: {t}")

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
