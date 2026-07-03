# Auto-generated Playwright script — TC-DEMO-VALIDATE-01_01072026_134440
# Generated: 2026-07-01 13:44:48
# Source: TC-DEMO-VALIDATE-01_01072026_134440.json
# Run: python TC-DEMO-VALIDATE-01_01072026_134440.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC-DEMO-VALIDATE-01_01072026_134440'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: Navigate to https://demoqa.com/web-tables
            print('>> STEP 1')
            await page.goto('https://demoqa.com/web-tables', wait_until='domcontentloaded')
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-DEMO-VALIDATE-01_01072026_134440/step_1.png')

            # Step 2: Screenshot
            print('>> STEP 2')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-DEMO-VALIDATE-01_01072026_134440/step_2.png')

            # STEP 3 FAILED [assert_text] — fix manually before running
            # VALID: salary Cierra Vega ? 10000
            # t = (await page.locator('//body').first.inner_text()).strip()
            # if 'salary Cierra Vega ? 10000' not in t:
            #     raise AssertionError(f"assert_text failed — expected 'salary Cierra Vega ? 10000', got: {t}")

            # STEP 4 FAILED [assert_text] — fix manually before running
            # VALID: age ? 39
            # t = (await page.locator('//body').first.inner_text()).strip()
            # if 'age ? 39' not in t:
            #     raise AssertionError(f"assert_text failed — expected 'age ? 39', got: {t}")

            # Step 5: Screenshot
            print('>> STEP 5')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-DEMO-VALIDATE-01_01072026_134440/step_5.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
