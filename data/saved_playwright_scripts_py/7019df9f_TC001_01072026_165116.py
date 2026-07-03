# Auto-generated Playwright script — 7019df9f_TC001_01072026_165116
# Generated: 2026-07-01 16:52:24
# Source: 7019df9f_TC001_01072026_165116.json
# Run: python 7019df9f_TC001_01072026_165116.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/7019df9f_TC001_01072026_165116'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: Buka halaman https://wikipedia.org
            print('>> STEP 1')
            await page.goto('https://wikipedia.org', wait_until='domcontentloaded')
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7019df9f_TC001_01072026_165116/step_1.png')

            # Step 2: Verifikasi halaman Wikipedia muncul
            print('>> STEP 2')
            try:
                await page.wait_for_url('**/*wikipedia.org*', timeout=8000)
            except Exception:
                pass
            if 'wikipedia.org' not in page.url:
                raise AssertionError(f"assert_url failed — got: {page.url}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7019df9f_TC001_01072026_165116/step_2.png')

            # Step 3: Klik link English
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
            }""", '//a[@id="js-link-box-en"]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7019df9f_TC001_01072026_165116/step_3.png')

            # Step 4: Verifikasi halaman Wikipedia English muncul
            print('>> STEP 4')
            try:
                await page.wait_for_url('**/*en.wikipedia.org*', timeout=8000)
            except Exception:
                pass
            if 'en.wikipedia.org' not in page.url:
                raise AssertionError(f"assert_url failed — got: {page.url}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/7019df9f_TC001_01072026_165116/step_4.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
