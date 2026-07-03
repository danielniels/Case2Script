# Auto-generated Playwright script — TC-NOMATCH-VERIFY-01_02072026_164401
# Generated: 2026-07-02 16:44:28
# Source: TC-NOMATCH-VERIFY-01_02072026_164401.json
# Run: python TC-NOMATCH-VERIFY-01_02072026_164401.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC-NOMATCH-VERIFY-01_02072026_164401'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: Buka halaman https://the-internet.herokuapp.com/login
            print('>> STEP 1')
            await page.goto('https://the-internet.herokuapp.com/login', wait_until='domcontentloaded')
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-NOMATCH-VERIFY-01_02072026_164401/step_1.png')

            # Step 2: Mengisi Username → tomsmith
            print('>> STEP 2')
            await page.locator('xpath=//input[@id="username"]').first.fill('tomsmith')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-NOMATCH-VERIFY-01_02072026_164401/step_2.png')

            # Step 3: Mengisi Password → SuperSecretPassword!
            print('>> STEP 3')
            await page.locator('xpath=//input[@id="password"]').first.fill('SuperSecretPassword!')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-NOMATCH-VERIFY-01_02072026_164401/step_3.png')

            # STEP 4 FAILED [no_match] — fix manually before running
            # Klik Tombol Ekspor Data Zebra Marsupial

            # Step 5: Klik Login Button
            print('>> STEP 5')
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
            }""", '//button[.//text()[normalize-space(.) = "Login"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-NOMATCH-VERIFY-01_02072026_164401/step_5.png')

            # Step 6: Halaman Secure
            print('>> STEP 6')
            try:
                await page.wait_for_url('**/*secure*', timeout=8000)
            except Exception:
                pass
            if 'secure' not in page.url:
                raise AssertionError(f"assert_url failed — got: {page.url}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-NOMATCH-VERIFY-01_02072026_164401/step_6.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
