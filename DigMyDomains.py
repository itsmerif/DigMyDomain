import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

# Function to fetch and extract links from a single webpage
def extract_links_from_url(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=60)
        elapsed_time = time.time() - start_time
        
        if elapsed_time > 60:
            print(f"URL {url} took too long ({elapsed_time:.2f}s). Skipping...")
            return set()
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = set()
            # Find all <a> tags and extract the href attribute
            for anchor in soup.find_all('a', href=True):
                link = anchor['href']
                if link.startswith('http'):  # Consider only absolute URLs
                    links.add(link)
            return links
        else:
            print(f"Failed to fetch {url} with status code {response.status_code}.")
            return set()
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        print(f"Error occurred while processing {url}.")
        return set()

# Function to process the input file and extract links from all URLs
def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:  # Specify UTF-8 encoding
        urls = infile.readlines()

    total_sites = len(urls)
    all_links = set()
    skipped_sites = 0

    # Read existing links to avoid duplicates in the output file
    try:
        with open(output_file, 'r', encoding='utf-8') as outfile:  # Specify UTF-8 encoding
            written_links = set(line.strip() for line in outfile.readlines())
    except FileNotFoundError:
        written_links = set()  # Initialize as empty if the file doesn't exist

    with open(output_file, 'a', encoding='utf-8') as outfile:  # Append new links
        with tqdm(total=total_sites, desc="Processing Sites") as progress_bar:
            for idx, url in enumerate(urls, 1):
                url = url.strip()
                if url:
                    links = extract_links_from_url(url)
                    if links:
                        # Add links to all_links without checking for duplicates in real-time
                        for link in sorted(links):
                            if link not in written_links:
                                outfile.write(link + '\n')
                                written_links.add(link)  # Track written links to avoid duplication
                        all_links.update(links)  # Collect all links for later deduplication
                        progress_bar.set_postfix(Skipped=skipped_sites, Scraped=len(all_links))
                    else:
                        skipped_sites += 1
                        progress_bar.set_postfix(Skipped=skipped_sites, Scraped=len(all_links))

                    progress_bar.set_description(f"Processing {idx}/{total_sites}")
                progress_bar.update(1)

    # Deduplicate all collected links at the end
    unique_links = sorted(all_links)

    # Write unique links to the new file
    with open('output_unique.txt', 'w', encoding='utf-8') as unique_outfile:
        for link in unique_links:
            unique_outfile.write(link + '\n')

    print(f"\nSummary:\nProcessed: {total_sites - skipped_sites}/{total_sites}\nSkipped: {skipped_sites}\nSaved: {len(unique_links)} unique links to output_unique.txt")

# Example usage
input_file = 'sites.txt'  # Input file containing URLs (one per line)
output_file = 'output.txt'  # Output file to save the extracted links
process_file(input_file, output_file)
