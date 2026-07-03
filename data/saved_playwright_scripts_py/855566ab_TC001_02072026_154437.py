# Auto-generated Playwright script — 855566ab_TC001_02072026_154437
# Generated: 2026-07-02 15:44:57
# Source: 855566ab_TC001_02072026_154437.json
# Run: python 855566ab_TC001_02072026_154437.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/855566ab_TC001_02072026_154437'
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/855566ab_TC001_02072026_154437/step_1.png')

            # Step 2: Mengisi Username → tomsmith
            print('>> STEP 2')
            await page.locator('xpath=//input[@id="username"]').first.fill('tomsmith')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/855566ab_TC001_02072026_154437/step_2.png')

            # Step 3: Mengisi Password → SuperSecretPassword!
            print('>> STEP 3')
            await page.locator('xpath=//input[@id="password"]').first.fill('SuperSecretPassword!')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/855566ab_TC001_02072026_154437/step_3.png')

            # Step 4: Klik Tombol Ekspor Data Zebra Marsupial
            print('>> STEP 4')

            # Step 5: Klik Login Button
            print('>> STEP 5')

            # Step 6: Halaman Secure
            print('>> STEP 6')
            try:
                await page.wait_for_url('**/*secure*', timeout=8000)
            except Exception:
                pass
            if 'secure' not in page.url:
                raise AssertionError(f"assert_url failed — got: {page.url}")
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/855566ab_TC001_02072026_154437/step_6.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
