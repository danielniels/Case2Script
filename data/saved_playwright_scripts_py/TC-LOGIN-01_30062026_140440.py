# Auto-generated Playwright script — TC-LOGIN-01_30062026_140440
# Generated: 2026-06-30 14:05:20
# Source: TC-LOGIN-01_30062026_140440.json
# Run: python TC-LOGIN-01_30062026_140440.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_140440'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: Navigate to https://dev.itsaplic.com/login
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_140440/step_1.png')

            # Step 2: Fill username field with daniel.purba@is-gs.com
            print('>> STEP 2')
            await page.locator('//input[@id="email"]').first.fill('daniel.purba@is-gs.com')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_140440/step_2.png')

            # Step 3: Fill password field with Password
            print('>> STEP 3')
            await page.locator('//input[@id="password"]').first.fill('Password')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_140440/step_3.png')

            # Step 4: Click the Login button
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_140440/step_4.png')

            # Step 5: Verify dashboard page is visible
            print('>> STEP 5')
            try:
                await page.wait_for_url('**/*dashboard*', timeout=8000)
            except Exception:
                pass
            if 'dashboard' not in page.url:
                raise AssertionError(f"assert_url failed — got: {page.url}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_140440/step_5.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
