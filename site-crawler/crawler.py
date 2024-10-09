import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
from tqdm import tqdm

base_url = 'https://open.dosm.gov.my/'

urls = [base_url]
visited_url = set()
failed_url = set()

def has_no_extension(url):
    path = urlparse(url).path
    if path.endswith('/'):
        path = path[:-1]
    return os.path.splitext(path)[1] == ""

def normalize_url(url):
    parsed = urlparse(url)
    return parsed.scheme + '://' + parsed.netloc + parsed.path.rstrip('/')

start_time = time.time()
with tqdm(desc="Crawling") as pbar:
    while urls:
        current = urls.pop()
        normalized_current = normalize_url(current)
        if normalized_current in visited_url:
            continue
        try:
            response = requests.get(current, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            visited_url.add(normalized_current)
            for link in soup.find_all('a', href=True):
                full_url = urljoin(current, link['href'])
                if not full_url.startswith('http'):
                    continue
                normalized_full_url = normalize_url(full_url)
                if (normalized_full_url not in visited_url and
                        normalized_full_url not in failed_url and
                        normalized_full_url.startswith(base_url) and
                        has_no_extension(normalized_full_url)):
                    urls.append(full_url)
            time.sleep(1)  # Respectful delay
        except requests.RequestException as e:
            failed_url.add(normalized_current)
            print(f"Error fetching or processing the page {current}: {e}")
        pbar.update(1)

print(f"Visited URLs ({len(visited_url)}):")
for url in sorted(visited_url):
    print(url)

print(f"Time taken: {time.time() - start_time:.2f} seconds")


# Convert the set of visited URLs to a list
visited_urls_list = list(visited_url)

# Convert the list to a JSON-formatted string
visited_urls_json = json.dumps(visited_urls_list)

# Send a POST request to port 3000 with the JSON data
try:
    post_response = requests.post('http://localhost:3000', data=visited_urls_json, headers={'Content-Type': 'application/json'})
    post_response.raise_for_status()
    print(f"POST request successful. Response: {post_response.text}")
except requests.RequestException as e:
    print(f"Error sending POST request: {e}")

