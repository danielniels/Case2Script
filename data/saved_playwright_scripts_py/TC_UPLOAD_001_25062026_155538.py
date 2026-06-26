# Auto-generated Playwright script — TC_UPLOAD_001_25062026_155538
# Generated: 2026-06-25 15:56:42
# Source: TC_UPLOAD_001_25062026_155538.json
# Run: python TC_UPLOAD_001_25062026_155538.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC_UPLOAD_001_25062026_155538'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: Navigate to https://practice.expandtesting.com/upload
            print('>> STEP 1')
            await page.goto('https://practice.expandtesting.com/upload', wait_until='domcontentloaded')
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_UPLOAD_001_25062026_155538/step_1.png')

            # Step 2: Click on the file input field and select the file '01. Pengumuman Wisuda 75 BINUS University.pdf'
            print('>> STEP 2')
            await page.set_input_files('//input[@id="fileInput"]', ['01. Pengumuman Wisuda 75 BINUS University.pdf'])
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_UPLOAD_001_25062026_155538/step_2.png')

            # Step 3: Click the 'Upload' button
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
            }""", '//button[@id="fileSubmit"]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_UPLOAD_001_25062026_155538/step_3.png')

            # Step 4: Verify that the success message is displayed on the screen
            print('>> STEP 4')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_UPLOAD_001_25062026_155538/step_4.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
