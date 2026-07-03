# Auto-generated Playwright script — TC_LOGIN_01_02072026_174121
# Generated: 2026-07-02 17:42:09
# Source: TC_LOGIN_01_02072026_174121.json
# Run: python TC_LOGIN_01_02072026_174121.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC_LOGIN_01_02072026_174121'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: Navigate to https://tcm.testcasemanagement.site/login
            print('>> STEP 1')
            await page.goto('https://tcm.testcasemanagement.site/login', wait_until='domcontentloaded')
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_LOGIN_01_02072026_174121/step_1.png')

            # Step 2: Fill the username field with 'SuperAdmin'
            print('>> STEP 2')
            await page.locator('//input[@id="user_name"]').first.fill('SuperAdmin')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_LOGIN_01_02072026_174121/step_2.png')

            # Step 3: Fill the password field with 'P@ssw0rd'
            print('>> STEP 3')
            await page.locator('//input[@id="user_password"]').first.fill('P@ssw0rd')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_LOGIN_01_02072026_174121/step_3.png')

            # Step 4: Click the login button
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
            }""", '//button[text()[normalize-space(.) = "Log In"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_LOGIN_01_02072026_174121/step_4.png')

            # Step 5: Verify the presence of the dashboard header
            print('>> STEP 5')
            if not await page.locator('//a[.//text()[normalize-space(.) = "Dashboard"]]').first.is_visible():
                raise AssertionError(f"assert_visible failed: {'//a[.//text()[normalize-space(.) = "Dashboard"]]'}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_LOGIN_01_02072026_174121/step_5.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
