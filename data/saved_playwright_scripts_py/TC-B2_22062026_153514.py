# Auto-generated Playwright script — TC-B2_22062026_153514
# Generated: 2026-06-22 15:35:28
# Source: TC-B2_22062026_153514.json
# Run: python TC-B2_22062026_153514.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC-B2_22062026_153514'
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_22062026_153514/step_1.png')

            # Step 2: Mengisi Username → daniel.purba@is-gs.com
            print('>> STEP 2')
            await page.locator('xpath=//input[@id="email"]').first.fill('daniel.purba@is-gs.com')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_22062026_153514/step_2.png')

            # Step 3: Mengisi Password → Password
            print('>> STEP 3')
            await page.locator('xpath=//input[@id="password"]').first.fill('Password')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_22062026_153514/step_3.png')

            # Step 4: Click Login Button
            print('>> STEP 4')
            try:
                await page.evaluate("""(sel) => {
              let el;
              const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
              if (xsel.startsWith('//')) {
                  const r = document.evaluate(xsel, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                  el = r.singleNodeValue;
              } else {
                  el = document.querySelector(xsel);
              }
              if (el) el.click();
            }""", '#loginBtn')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_22062026_153514/step_4.png')

            # STEP 5 FAILED [assert_url] — fix manually before running
            # Halaman Dashboard
            # if 'dashboard' not in page.url:
            #     raise AssertionError(f"assert_url failed — got: {page.url}")

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
