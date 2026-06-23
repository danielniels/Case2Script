# Auto-generated Playwright script — TC-002_23062026_161032
# Generated: 2026-06-23 16:16:41
# Source: TC-002_23062026_161032.json
# Run: python TC-002_23062026_161032.py
# Requires: pip install playwright && playwright install chromium

import asyncio
import os
from playwright.async_api import async_playwright

SCREENSHOT_DIR = 'data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


async def run_test():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()

        try:

            # Step 1: https://tcm.testcasemanagement.site/login
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_1.png')

            # Step 2: Type 'testerl1' in the username input box
            print('>> STEP 2')
            await page.locator('//input[@id="user_name"]').first.fill('testerl1')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_2.png')

            # Step 3: Type 'P@ssw0rd' in the password input box
            print('>> STEP 3')
            await page.locator('//input[@id="user_password"]').first.fill('P@ssw0rd')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_3.png')

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
            }""", '//button[.//text()[normalize-space(.) = "Test TCM"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_4.png')

            # Step 5: Click the button containing text 'Cancel'
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
            }""", '//button[text()[normalize-space(.) = "Cancel"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_5.png')

            # Step 6: Click 'Test Case' link
            print('>> STEP 6')
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
            }""", '//a[.//text()[normalize-space(.) = "Test Case"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_6.png')

            # Step 7: Click button containing text 'Add Test Case'
            print('>> STEP 7')
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
            }""", '//button[text()[normalize-space(.) = "Add Test Case"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_7.png')

            # Step 8: Type 'testcase' into input with placeholder 'Test Case name'
            print('>> STEP 8')
            await page.locator('//input[@placeholder="Test Case name"]').first.fill('testcase')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_8.png')

            # Step 9: Type 'MCP Flow Testing' in the Description textarea box
            print('>> STEP 9')
            await page.locator('//textarea[@placeholder="Enter a detailed description"]').first.fill('MCP Flow Testing')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_9.png')

            # Step 10: Click button 'Select requirement', then click link text 'Test Case' inside the dropdown overlay
            print('>> STEP 10')
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
            }""", '//button[.//text()[normalize-space(.) = "Select requirement"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_10.png')

            # Step 11: Click the tab button containing text 'Steps'
            print('>> STEP 11')
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
            }""", '//button[@id="radix-_r_2j_-trigger-steps"]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_11.png')

            # Step 12: Type 'Masukkan email yang valid (user@email.com) dan kata sandi yang benar (Sandi123!)' in the input with placeholder 'Step Description'
            print('>> STEP 12')
            await page.locator('//textarea[@placeholder="Enter a detailed description"]').first.fill('Masukkan email yang valid (user@email.com) dan kata sandi yang benar (Sandi123!)')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_12.png')

            # Step 13: Type 'Sistem berhasil melakukan autentikasi, mengarahkan pengguna ke halaman Dashboard Utama, dan menampilkan pesan sukses' in the input with placeholder 'Expected Result'
            print('>> STEP 13')
            await page.locator('//textarea[@placeholder="Enter a detailed description"]').first.fill('Sistem berhasil melakukan autentikasi, mengarahkan pengguna ke halaman Dashboard Utama, dan menampilkan pesan sukses')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_13.png')

            # Step 14: Click the '+' button to add a new step row
            print('>> STEP 14')

            # Step 15: Type 'Klik ikon Tempat Sampah (Hapus) pada produk Sepatu Lari yang ada di dalam daftar keranjang belanja.' into the newly appeared last 'Step Description' input field
            print('>> STEP 15')
            await page.locator('//input[@placeholder="Step Description"]').first.fill('Klik ikon Tempat Sampah (Hapus) pada produk Sepatu Lari yang ada di dalam daftar keranjang belanja.')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_15.png')

            # Step 16: Type 'Produk Sepatu Lari langsung terhapus dari daftar, dan total harga belanjaan otomatis berkurang secara real-time sesuai harga produk yang dihapus.' into the newly appeared last 'Expected Result' input field
            print('>> STEP 16')
            await page.locator('//input[@placeholder="Expected Result"]').first.fill('Produk Sepatu Lari langsung terhapus dari daftar, dan total harga belanjaan otomatis berkurang secara real-time sesuai harga produk yang dihapus.')
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_16.png')

            # Step 17: Click button containing text 'Save'
            print('>> STEP 17')
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
            }""", '//button[text()[normalize-space(.) = "Save"]]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_17.png')

            # STEP 18 FAILED [click_by_index] — fix manually before running
            # Click the button containing text 'Close'

            # Step 19: Click user profile or navigation dropdown icon menu
            print('>> STEP 19')
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
            }""", '//button[@id="radix-_r_0_"]')
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
            await page.screenshot(path='data/saved_playwright_scripts_py/screenshots/TC-002_23062026_161032/step_19.png')

            # STEP 20 FAILED [click] — fix manually before running
            # Click text 'Log Out'
            # try:
            #     await page.evaluate("""(sel) => {
            #   function isVisible(node) {
            #     const s = window.getComputedStyle(node);
            #     return s.display !== 'none' && s.visibility !== 'hidden' && node.offsetParent !== null;
            #   }
            #   let el;
            #   const xsel = sel.startsWith('xpath=') ? sel.slice(6) : sel;
            #   if (xsel.startsWith('//')) {
            #       const r = document.evaluate(xsel, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            #       for (let i = 0; i < r.snapshotLength; i++) {
            #           const node = r.snapshotItem(i);
            #           if (isVisible(node)) { el = node; break; }
            #       }
            #   } else {
            #       const nodes = document.querySelectorAll(xsel);
            #       for (const node of nodes) {
            #           if (isVisible(node)) { el = node; break; }
            #       }
            #   }
            #   if (el) el.click();
            # }""", '//a[.//text()[normalize-space(.) = "Log Out"]]')
            # except Exception:
            #     pass
            # try:
            #     await page.wait_for_load_state('load')
            # except Exception:
            #     pass
            # try:
            #     await page.wait_for_load_state('networkidle')
            # except Exception:
            #     pass
            # await page.wait_for_timeout(800)

            print('Test completed')
        except Exception as err:
            print(f'Test failed: {err}')
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_test())
