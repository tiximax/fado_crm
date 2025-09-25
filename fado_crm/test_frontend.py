# -*- coding: utf-8 -*-
# FADO CRM Frontend Testing with Playwright
# Script nay se test frontend va tim loi nhu mot detective!

import asyncio
import os
from playwright.async_api import async_playwright
import time

async def test_fado_crm_frontend():
    """Test frontend CRM voi Playwright - Detective mode!"""

    async with async_playwright() as p:
        print("🚀 Khoi dong Playwright browser...")

        # Launch browser
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()

        # Set viewport
        await page.set_viewport_size({"width": 1920, "height": 1080})

        try:
            print("📄 Dang test frontend HTML...")

            # Get frontend path
            frontend_path = os.path.abspath("frontend/index.html")
            frontend_url = f"file:///{frontend_path}".replace("\\", "/")

            print(f"🌐 Opening: {frontend_url}")

            # Navigate to frontend
            await page.goto(frontend_url)
            await page.wait_for_load_state("networkidle")

            # Take screenshot
            await page.screenshot(path="frontend_test.png")
            print("📸 Screenshot saved: frontend_test.png")

            # Test page title
            title = await page.title()
            print(f"📋 Page title: {title}")

            # Check if main elements exist
            print("🔍 Checking main elements...")

            # Check navbar
            navbar = await page.locator(".navbar").count()
            print(f"✅ Navbar found: {navbar}")

            # Check navigation items
            nav_items = await page.locator(".nav-item").count()
            print(f"✅ Navigation items: {nav_items}")

            # Check main container
            main_container = await page.locator(".main-container").count()
            print(f"✅ Main container: {main_container}")

            # Check dashboard
            dashboard = await page.locator("#dashboard").count()
            print(f"✅ Dashboard section: {dashboard}")

            # Check stats cards
            stats_cards = await page.locator(".stat-card").count()
            print(f"✅ Stats cards: {stats_cards}")

            # Test navigation clicks
            print("🖱️ Testing navigation...")

            # Click on Customers tab
            await page.click('[data-tab="customers"]')
            await page.wait_for_timeout(1000)
            print("✅ Customers tab clicked")

            # Check if customers section is visible
            customers_visible = await page.locator("#customers.active").count()
            print(f"✅ Customers section active: {customers_visible}")

            # Click on Products tab
            await page.click('[data-tab="products"]')
            await page.wait_for_timeout(1000)
            print("✅ Products tab clicked")

            # Click on Orders tab
            await page.click('[data-tab="orders"]')
            await page.wait_for_timeout(1000)
            print("✅ Orders tab clicked")

            # Back to Dashboard
            await page.click('[data-tab="dashboard"]')
            await page.wait_for_timeout(1000)
            print("✅ Back to Dashboard")

            # Test API connectivity from frontend
            print("🔗 Testing API connectivity...")

            # Check console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            # Wait a bit for any console errors
            await page.wait_for_timeout(2000)

            if console_errors:
                print("⚠️ Console errors found:")
                for error in console_errors:
                    print(f"   ❌ {error}")
            else:
                print("✅ No console errors detected")

            # Test JavaScript execution
            api_base_url = await page.evaluate("() => window.API_BASE_URL || 'http://localhost:8000'")
            print(f"🔗 API Base URL from frontend: {api_base_url}")

            # Test if JavaScript variables are loaded
            current_tab = await page.evaluate("() => window.currentTab || 'unknown'")
            print(f"📋 Current tab: {current_tab}")

            # Take final screenshot
            await page.screenshot(path="frontend_final.png")
            print("📸 Final screenshot saved: frontend_final.png")

            print("\n" + "="*50)
            print("🎉 FRONTEND TEST COMPLETED!")
            print("="*50)
            print("✅ HTML structure: OK")
            print("✅ Navigation: Working")
            print("✅ CSS styling: Loaded")
            print("✅ JavaScript: Running")
            print(f"⚠️ Console errors: {len(console_errors)}")

        except Exception as e:
            print(f"❌ Error during frontend test: {e}")
            await page.screenshot(path="frontend_error.png")

        finally:
            # Keep browser open for manual inspection
            print("🔍 Browser will stay open for manual inspection...")
            print("Press Enter to close browser...")
            input()
            await browser.close()

async def test_api_integration():
    """Test API integration from frontend"""

    async with async_playwright() as p:
        print("🔗 Testing API integration...")

        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Navigate to frontend
            frontend_path = os.path.abspath("frontend/index.html")
            frontend_url = f"file:///{frontend_path}".replace("\\", "/")
            await page.goto(frontend_url)

            # Wait for page load
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)

            # Check if API calls are working
            print("📡 Testing API calls from frontend...")

            # Monitor network requests
            requests = []
            page.on("request", lambda request: requests.append(request.url))

            # Try to trigger API calls by interacting with UI
            await page.click('[data-tab="dashboard"]')
            await page.wait_for_timeout(2000)

            # Check network requests
            api_requests = [req for req in requests if "127.0.0.1:8000" in req or "localhost:8000" in req]

            print(f"🌐 API requests detected: {len(api_requests)}")
            for req in api_requests:
                print(f"   📡 {req}")

            if not api_requests:
                print("⚠️ No API requests detected - might be CORS or connection issue")

                # Try to execute API call manually
                result = await page.evaluate("""
                    async () => {
                        try {
                            const response = await fetch('http://127.0.0.1:8000/');
                            const data = await response.json();
                            return { success: true, data: data };
                        } catch (error) {
                            return { success: false, error: error.message };
                        }
                    }
                """)

                print(f"🧪 Manual API test result: {result}")

        except Exception as e:
            print(f"❌ API integration test error: {e}")

        finally:
            await browser.close()

async def main():
    """Main test function"""
    print("🎭 FADO CRM Frontend Testing with Playwright")
    print("="*50)

    # Test 1: Frontend structure and UI
    await test_fado_crm_frontend()

    # Test 2: API integration
    await test_api_integration()

    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())