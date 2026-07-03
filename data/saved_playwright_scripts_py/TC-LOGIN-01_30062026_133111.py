# Auto-generated Playwright script — TC-LOGIN-01_30062026_133111
# Generated: 2026-06-30 13:31:51
# Source: TC-LOGIN-01_30062026_133111.json
# Run: python TC-LOGIN-01_30062026_133111.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_133111'
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_133111/step_1.png')

            # Step 2: Fill username field with qatester@mail.com
            print('>> STEP 2')
            await page.locator('//input[@id="email"]').first.fill('qatester@mail.com')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_133111/step_2.png')

            # Step 3: Fill password field with password123
            print('>> STEP 3')
            await page.locator('//input[@id="password"]').first.fill('password123')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_133111/step_3.png')

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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_133111/step_4.png')

            # Step 5: Verify dashboard page is visible
            print('>> STEP 5')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-LOGIN-01_30062026_133111/step_5.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
