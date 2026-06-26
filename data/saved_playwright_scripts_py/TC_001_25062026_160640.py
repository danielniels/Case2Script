# Auto-generated Playwright script — TC_001_25062026_160640
# Generated: 2026-06-25 16:06:55
# Source: TC_001_25062026_160640.json
# Run: python TC_001_25062026_160640.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC_001_25062026_160640'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: Navigate to https://www.ilovepdf.com/pdf_to_word
            print('>> STEP 1')
            await page.goto('https://www.ilovepdf.com/pdf_to_word', wait_until='domcontentloaded')
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_001_25062026_160640/step_1.png')

            # Step 2: Click on the 'Select PDF' button or drag and drop the file '01. Pengumuman Wisuda 75 BINUS University.pdf'
            print('>> STEP 2')
            await page.set_input_files('//input[@id="html5_1jrv0g3ftvjk1sebovmrmkgqk4"]', ['01. Pengumuman Wisuda 75 BINUS University.pdf'])
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_001_25062026_160640/step_2.png')

            # Step 3: Verify that the filename '01. Pengumuman Wisuda 75 BINUS University.pdf' is displayed on the upload screen
            print('>> STEP 3')
            t = (await page.locator('//body').first.inner_text()).strip()
            if '01. Pengumuman Wisuda 75 BINUS University.pdf' not in t:
                raise AssertionError(f"assert_text failed — expected '01. Pengumuman Wisuda 75 BINUS University.pdf', got: {t}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_001_25062026_160640/step_3.png')

            # Step 4: Click the 'Convert to WORD' button
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
            }""", '//button[@id="processTask"]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_001_25062026_160640/step_4.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
