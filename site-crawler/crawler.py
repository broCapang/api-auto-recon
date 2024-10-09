import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
from tqdm import tqdm

base_url = 'https://umexpert.um.edu.my/'

urls = [base_url]
visited_url = set()
failed_url = set()
urls.append(base_url)


def has_no_extension(url):
    path = urlparse(url).path
    return os.path.splitext(path)[1] == ""

time = time.time()
with tqdm(total=1, desc="Crawling") as pbar:
    while urls:
        current = urls.pop()
        try:
            response = requests.get(current)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            visited_url.add(current)
            for link in soup.find_all('a', href=True):
                full_url = urljoin(base_url, link['href'])
                if (full_url not in visited_url and
                        full_url not in urls and
                        full_url.startswith(base_url) and
                        full_url not in failed_url and
                        has_no_extension(full_url)):
                    urls.append(full_url)
                    pbar.total += 1
                    pbar.update(0)  # Reset the progress bar length

        except requests.RequestException as e:
            failed_url.add(current)
            print(f"Error fetching or processing the page: {e}")

        pbar.update(1)


with open('links-umexpert.txt', 'w') as file:
    for item in visited_url:
        file.write(f"{item}\n")

print(f"Time taken: {time.time() - time:.2f} seconds")

