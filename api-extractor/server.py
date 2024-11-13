from flask import Flask, jsonify
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)
port = 3000

# Function to extract URLs using Playwright
async def extract_urls():
    base_url = "https://open.dosm.gov.my/"

    urls_request = []
    urls_response = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Intercept and capture network requests (including API calls)
        page.on("request", lambda request: urls_request.append(request.url) if request.resource_type in ["xhr", "fetch"] else None)

        # Capture network responses
        page.on("response", lambda response: urls_response.append(response.url) if response.request.resource_type in ["xhr", "fetch"] else None)

        # Navigate to the page you want to capture API calls from
        await page.goto(base_url)

        # Wait for the network to be idle to capture all requests/responses
        await page.wait_for_load_state("networkidle")

        # Merge the requests and responses into one list
        merged_urls = urls_request + urls_response

        # Filter for unique URLs under 'https://open.dosm.gov.my/'
        unique_urls = list(set([url for url in merged_urls if url.startswith(base_url)]))

        # Close the browser
        await browser.close()

        return unique_urls

@app.route('/extract-urls', methods=['GET'])
async def get_urls():
    try:
        urls = await extract_urls()
        return jsonify({
            'status': 'success',
            'data': urls
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=port)

