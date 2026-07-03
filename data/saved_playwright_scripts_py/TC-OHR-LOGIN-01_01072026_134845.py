# Auto-generated Playwright script — TC-OHR-LOGIN-01_01072026_134845
# Generated: 2026-07-01 13:49:58
# Source: TC-OHR-LOGIN-01_01072026_134845.json
# Run: python TC-OHR-LOGIN-01_01072026_134845.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC-OHR-LOGIN-01_01072026_134845'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: Navigate to https://opensource-demo.orangehrmlive.com/web/index.php/auth/login
            print('>> STEP 1')
            await page.goto('https://opensource-demo.orangehrmlive.com/web/index.php/auth/login', wait_until='domcontentloaded')
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-OHR-LOGIN-01_01072026_134845/step_1.png')

            # Step 2: Mengisi Username → Admin
            print('>> STEP 2')
            await page.locator('//input[@name="username"]').first.fill('Admin')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-OHR-LOGIN-01_01072026_134845/step_2.png')

            # Step 3: Mengisi Password → admin123
            print('>> STEP 3')
            await page.locator('xpath=//input[@name="password"]').first.fill('admin123')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-OHR-LOGIN-01_01072026_134845/step_3.png')

            # Step 4: Klik Login Button
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
            }""", '//button[text()[normalize-space(.) = "Login"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-OHR-LOGIN-01_01072026_134845/step_4.png')

            # Step 5: Halaman dashboard
            print('>> STEP 5')
            try:
                await page.wait_for_url('**/*dashboard*', timeout=8000)
            except Exception:
                pass
            if 'dashboard' not in page.url:
                raise AssertionError(f"assert_url failed — got: {page.url}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-OHR-LOGIN-01_01072026_134845/step_5.png')

            # Step 6: Screenshot
            print('>> STEP 6')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-OHR-LOGIN-01_01072026_134845/step_6.png')

            # Step 7: VALID: menu → Dashboard
            print('>> STEP 7')
            t = (await page.locator('//body').first.inner_text()).strip()
            if 'Dashboard' not in t:
                raise AssertionError(f"assert_text failed — expected 'Dashboard', got: {t}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-OHR-LOGIN-01_01072026_134845/step_7.png')

            # Step 8: Klik Leave
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
            }""", '//a[.//text()[normalize-space(.) = "Leave"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-OHR-LOGIN-01_01072026_134845/step_8.png')

            # Step 9: Screenshot
            print('>> STEP 9')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-OHR-LOGIN-01_01072026_134845/step_9.png')

            # Step 10: VALID: Leave → Leave List
            print('>> STEP 10')
            t = (await page.locator('//body').first.inner_text()).strip()
            if 'Leave List' not in t:
                raise AssertionError(f"assert_text failed — expected 'Leave List', got: {t}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-OHR-LOGIN-01_01072026_134845/step_10.png')

            # [Step 11] close session [close_session] — MCP-only, skipped

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
