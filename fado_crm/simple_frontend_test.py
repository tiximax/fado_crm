# -*- coding: utf-8 -*-
# FADO CRM Frontend Testing with Playwright
# Simple version without emojis for Windows compatibility

import asyncio
import os
from playwright.async_api import async_playwright

async def test_frontend_simple():
    """Test frontend CRM with Playwright"""

    async with async_playwright() as p:
        print("Starting Playwright browser...")

        # Launch browser - visible mode
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        try:
            print("Testing frontend HTML...")

            # Get frontend path
            frontend_path = os.path.abspath("frontend/index.html")
            frontend_url = f"file:///{frontend_path}".replace("\\", "/")

            print(f"Opening: {frontend_url}")

            # Navigate to frontend
            await page.goto(frontend_url, wait_until="networkidle")

            # Take screenshot
            await page.screenshot(path="frontend_test.png", full_page=True)
            print("Screenshot saved: frontend_test.png")

            # Test page title
            title = await page.title()
            print(f"Page title: {title}")

            # Check main elements
            print("Checking main elements...")

            # Check navbar
            navbar_count = await page.locator(".navbar").count()
            print(f"Navbar found: {navbar_count}")

            # Check navigation items
            nav_items = await page.locator(".nav-item").count()
            print(f"Navigation items: {nav_items}")

            # Check main container
            main_container = await page.locator(".main-container").count()
            print(f"Main container: {main_container}")

            # Check if dashboard is visible
            dashboard_visible = await page.locator("#dashboard.active").is_visible()
            print(f"Dashboard visible: {dashboard_visible}")

            # Check stats cards
            stats_cards = await page.locator(".stat-card").count()
            print(f"Stats cards: {stats_cards}")

            # Test navigation
            print("Testing navigation...")

            # Click Customers tab
            await page.click('[data-tab="customers"]')
            await page.wait_for_timeout(1000)

            customers_active = await page.locator("#customers.active").is_visible()
            print(f"Customers tab active: {customers_active}")

            # Click Products tab
            await page.click('[data-tab="products"]')
            await page.wait_for_timeout(1000)

            products_active = await page.locator("#products.active").is_visible()
            print(f"Products tab active: {products_active}")

            # Click Orders tab
            await page.click('[data-tab="orders"]')
            await page.wait_for_timeout(1000)

            orders_active = await page.locator("#orders.active").is_visible()
            print(f"Orders tab active: {orders_active}")

            # Back to Dashboard
            await page.click('[data-tab="dashboard"]')
            await page.wait_for_timeout(1000)

            dashboard_active = await page.locator("#dashboard.active").is_visible()
            print(f"Dashboard active again: {dashboard_active}")

            # Check for JavaScript errors
            print("Checking for JavaScript errors...")

            # Collect console messages
            console_messages = []
            page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

            # Wait for any async operations
            await page.wait_for_timeout(3000)

            if console_messages:
                print("Console messages:")
                for msg in console_messages[-10:]:  # Last 10 messages
                    print(f"  {msg}")
            else:
                print("No console messages")

            # Test JavaScript variables
            try:
                current_tab = await page.evaluate("() => window.currentTab || 'unknown'")
                print(f"Current tab variable: {current_tab}")

                api_url = await page.evaluate("() => window.API_BASE_URL || 'not set'")
                print(f"API URL variable: {api_url}")
            except Exception as e:
                print(f"JavaScript evaluation error: {e}")

            # Test API connectivity from frontend
            print("Testing API connectivity...")

            api_test = await page.evaluate("""
                async () => {
                    try {
                        const response = await fetch('http://127.0.0.1:8000/');
                        const data = await response.json();
                        return { success: true, status: response.status, data: data };
                    } catch (error) {
                        return { success: false, error: error.message };
                    }
                }
            """)

            print(f"API test result: {api_test}")

            # Test dashboard API call
            dashboard_test = await page.evaluate("""
                async () => {
                    try {
                        const response = await fetch('http://127.0.0.1:8000/dashboard');
                        const data = await response.json();
                        return { success: true, status: response.status, data: data };
                    } catch (error) {
                        return { success: false, error: error.message };
                    }
                }
            """)

            print(f"Dashboard API test: {dashboard_test}")

            # Final screenshot
            await page.screenshot(path="frontend_final.png", full_page=True)
            print("Final screenshot saved: frontend_final.png")

            print("\n" + "="*50)
            print("FRONTEND TEST RESULTS:")
            print("="*50)
            print(f"HTML structure: {'OK' if navbar_count > 0 else 'FAIL'}")
            print(f"Navigation: {'OK' if nav_items >= 4 else 'FAIL'}")
            print(f"Dashboard: {'OK' if dashboard_visible else 'FAIL'}")
            print(f"Tab switching: {'OK' if customers_active and products_active else 'FAIL'}")
            print(f"API connectivity: {'OK' if api_test.get('success') else 'FAIL'}")
            print("="*50)

            # Check if we should test forms
            print("\nTesting Add Customer form...")

            # Go to customers tab
            await page.click('[data-tab="customers"]')
            await page.wait_for_timeout(1000)

            # Try to click "Add Customer" button
            add_button = await page.locator('button:has-text("Thêm Khách Hàng")').count()
            print(f"Add Customer button found: {add_button}")

            if add_button > 0:
                await page.click('button:has-text("Thêm Khách Hàng")')
                await page.wait_for_timeout(1000)

                # Check if modal opened
                modal_visible = await page.locator("#addCustomerModal").is_visible()
                print(f"Add Customer modal opened: {modal_visible}")

                if modal_visible:
                    # Take screenshot of modal
                    await page.screenshot(path="modal_test.png")
                    print("Modal screenshot saved: modal_test.png")

                    # Close modal
                    await page.click('.close')
                    await page.wait_for_timeout(500)

            print("\nKeeping browser open for manual inspection...")
            print("Press Enter to close browser and continue...")

        except Exception as e:
            print(f"Error during test: {e}")
            await page.screenshot(path="error_screenshot.png")

        finally:
            # Wait for user input before closing
            try:
                input()
            except:
                pass
            await browser.close()

if __name__ == "__main__":
    print("FADO CRM Frontend Testing with Playwright")
    print("="*40)
    asyncio.run(test_frontend_simple())