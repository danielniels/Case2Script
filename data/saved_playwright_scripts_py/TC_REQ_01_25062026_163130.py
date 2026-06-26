# Auto-generated Playwright script — TC_REQ_01_25062026_163130
# Generated: 2026-06-25 16:31:46
# Source: TC_REQ_01_25062026_163130.json
# Run: python TC_REQ_01_25062026_163130.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC_REQ_01_25062026_163130'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: Navigate to https://tcm.testcasemanagement.site/
            print('>> STEP 1')
            await page.goto('https://tcm.testcasemanagement.site/', wait_until='domcontentloaded')
            try:
                await page.wait_for_load_state('load')
            except Exception:
                pass
            try:
                await page.wait_for_load_state('networkidle')
            except Exception:
                pass
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_REQ_01_25062026_163130/step_1.png')

            # Step 2: Click on the 'Requirement' menu item in the sidebar
            print('>> STEP 2')

            # Step 3: Click on the 'Add Requirement' button
            print('>> STEP 3')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
