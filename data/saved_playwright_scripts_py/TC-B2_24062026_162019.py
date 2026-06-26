# Auto-generated Playwright script — TC-B2_24062026_162019
# Generated: 2026-06-24 16:20:54
# Source: TC-B2_24062026_162019.json
# Run: python TC-B2_24062026_162019.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC-B2_24062026_162019'
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_24062026_162019/step_1.png')

            # Step 2: Mengisi Username → daniel.purba@is-gs.com
            print('>> STEP 2')
            await page.locator('xpath=//input[@id="email"]').first.fill('d.purba@is-gs.com')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_24062026_162019/step_2.png')

            # Step 3: Mengisi Password → Password
            print('>> STEP 3')
            await page.locator('xpath=//input[@id="password"]').first.fill('Password')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_24062026_162019/step_3.png')

            # Step 4: Click Login Button
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-B2_24062026_162019/step_4.png')

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
