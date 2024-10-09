const puppeteer = require('puppeteer');
const express = require('express');
const app = express();
const port = 3000;

// Function to extract URLs using Puppeteer
async function extractUrls() {
  const baseUrl = "https://open.dosm.gov.my/";

  let urlsRequest = [];
  let urlsResponse = [];

  // Launch Puppeteer browser
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Intercept and capture network requests (including API calls)
  page.on('request', request => {
    if (request.resourceType() === 'xhr' || request.resourceType() === 'fetch') {
      urlsRequest.push(request.url());
    }
  });

  // Capture network responses
  page.on('response', async response => {
    if (response.request().resourceType() === 'xhr' || response.request().resourceType() === 'fetch') {
      urlsResponse.push(response.url());
    }
  });

  // Navigate to the page you want to capture API calls from
  await page.goto(baseUrl);

  // Optionally wait for the network to be idle to capture all requests/responses
  await page.waitForNetworkIdle();

  // Merge the requests and responses into one list
  const mergedUrls = urlsRequest.concat(urlsResponse);

  // Filter for unique URLs under 'https://open.dosm.gov.my/'
  const uniqueUrls = mergedUrls.filter(onlyUnique).filter(url => url.startsWith(baseUrl));

  // Close the browser
  await browser.close();

  // Return the unique URLs as JSON
  return uniqueUrls;
}

// Helper function to filter unique URLs
function onlyUnique(value, index, array) {
  return array.indexOf(value) === index;
}

// API endpoint that triggers the URL extraction
app.get('/extract-urls', async (req, res) => {
  try {
    const urls = await extractUrls();
    res.json({
      status: 'success',
      data: urls
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: error.message
    });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
