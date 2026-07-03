# Auto-generated Playwright script — TC_001_03072026_104751
# Generated: 2026-07-03 10:48:37
# Source: TC_001_03072026_104751.json
# Run: python TC_001_03072026_104751.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC_001_03072026_104751'
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_001_03072026_104751/step_1.png')

            # Step 2: Fill username field with 'SuperAdmin'
            print('>> STEP 2')
            await page.locator('//input[@id="user_name"]').first.fill('SuperAdmin')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_001_03072026_104751/step_2.png')

            # Step 3: Fill password field with 'P@ssw0rd'
            print('>> STEP 3')
            await page.locator('//input[@id="user_password"]').first.fill('P@ssw0rd')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_001_03072026_104751/step_3.png')

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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_001_03072026_104751/step_4.png')

            # Step 5: Click on the 'Project' dropdown in the navbar
            print('>> STEP 5')
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
            }""", '//button[.//text()[normalize-space(.) = "Choose a project"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC_001_03072026_104751/step_5.png')

            # STEP 6 FAILED [select_option] — fix manually before running
            # Select the project 'Aplicx Testing'
            # await page.evaluate("""({sel, val}) => {
            #   function isVisible(node) {
            #     const s = window.getComputedStyle(node);
            #     return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
            #   }
            #   let el;
            #   if (sel.startsWith('//') || sel.startsWith('xpath=')) {
            #     const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
            #     const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            #     for (let i = 0; i < r.snapshotLength; i++) {
            #         const node = r.snapshotItem(i);
            #         if (isVisible(node)) { el = node; break; }
            #     }
            #   } else {
            #     const nodes = document.querySelectorAll(sel);
            #     for (const node of nodes) {
            #         if (isVisible(node)) { el = node; break; }
            #     }
            #   }
            #   if (!el) return false;
            #   const opt = Array.from(el.options).find(o => o.value === val || o.text.trim() === val);
            #   if (!opt) return false;
            #   const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value');
            #   if (nativeSetter?.set) nativeSetter.set.call(el, opt.value);
            #   else el.value = opt.value;
            #   el.dispatchEvent(new Event('change', { bubbles: true }));
            #   el.dispatchEvent(new Event('input', { bubbles: true }));
            #   return true;
            # }""", {'sel': '//button[.//text()[normalize-space(.) = "Choose a project"]]', 'val': 'Aplicx Testing'})

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
