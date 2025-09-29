# -*- coding: utf-8 -*-
# FADO CRM Frontend Server
# HTTP server cho frontend de tranh CORS issues

import http.server
import os
import socketserver
import threading
import time
import webbrowser


class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler voi CORS headers"""

    def end_headers(self):
        # Add CORS headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()


def serve_frontend(port=3000):
    """Khoi dong HTTP server cho frontend"""

    # Change to frontend directory
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    if os.path.exists(frontend_dir):
        os.chdir(frontend_dir)
        print(f"Serving from: {frontend_dir}")
    else:
        print("Frontend directory not found!")
        return

    # Start server
    handler = CORSHTTPRequestHandler

    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"Frontend server starting at http://localhost:{port}")
            print("CORS enabled for API calls")
            print("Press Ctrl+C to stop server")

            # Auto open browser
            def open_browser():
                time.sleep(1)
                webbrowser.open(f"http://localhost:{port}")

            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()

            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\nFrontend server stopped!")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {port} already in use. Trying port {port+1}...")
            serve_frontend(port + 1)
        else:
            print(f"Error starting server: {e}")


if __name__ == "__main__":
    print("FADO CRM Frontend Server")
    print("=" * 30)
    serve_frontend()
