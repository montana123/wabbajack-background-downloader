import requests
import time
import random
import os
import re
import sys
import datetime
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

### Set variables here ###
links_file = "output.txt"
session_cookies = os.getenv('SESSION_COOKIES')
download_directory = "downloads"
output_file = "output.txt"
processed_file = "processed_output.txt"
log_download_path = "download.log"
log_skip_path = "skip.log"
### END - Set variables here ###

# Constants
skyrim_game_id = "1704"
nexus_download_url = "https://www.nexusmods.com/Core/Libs/Common/Managers/Downloads?GenerateDownloadUrl"

# Function to read links from the file
def read_links(file_path):
    with open(file_path, 'r') as file:
        links = [line.strip() for line in file.readlines()]
    return links

# Function to extract file_id and game_id from the URL
def extract_ids_from_url(url):
    match = re.search(r"file_id=(\d+)", url)
    if match:
        file_id = match.group(1)
        game_id = skyrim_game_id
        return file_id, game_id
    else:
        print(f"Failed to extract file_id and game_id from URL: {url}")
        return None, None

# Function to make the POST request and get the download URL
def make_post_request(referer_url, file_id, game_id):
    url = nexus_download_url
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en,de;q=0.9,de-DE;q=0.8,en-US;q=0.7",
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.nexusmods.com",
        "Referer": referer_url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": session_cookies
    }
    data = {
        "fid": file_id,
        "game_id": game_id
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        print(f"Request successful to {referer_url}")
        try:
            response_data = response.json()
            if isinstance(response_data, list):
                download_url = response_data[0].get("url", "")
            else:
                download_url = response_data.get("url", "")
            if download_url:
                return download_url
            else:
                print("No download URL found in the response.")
        except ValueError:
            print(f"Failed to parse the response as JSON from {referer_url}")
    else:
        print(f"Request failed for {referer_url} with status code {response.status_code}")
    
    return None

def download_file(download_url, referer_url,):
    try:
        os.makedirs(download_directory, exist_ok=True)
        file_name = download_url.split("/")[-1].split("?")[0]
        file_path = os.path.join(download_directory, file_name)
        
        if os.path.exists(file_path):
            with open(log_skip_path, "a") as skip_log:
                skip_log.write(f"Skipped: {file_name} (already exists) - URL: {referer_url}\n")
            print(f"File {file_name} already exists. Skipping download.")
            remove_line(referer_url)
            return  # Skip downloading
        
        # Send GET request to download the file
        response = requests.get(download_url, stream=True)
        
        if response.status_code == 200:
            # Try to get the total file size from the headers, but allow for zero
            total_size = int(response.headers.get('content-length', 0))
            if total_size == 0:
                total_size = None  # Set to None if size is not available

            downloaded_size = 0
            start_time = time.time()
            
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)

                        # Calculate download speed and progress
                        elapsed_time = time.time() - start_time

                        # Avoid division by zero when calculating speed
                        speed = 0  # Default speed is 0
                        if elapsed_time > 0:  # Ensure time has passed before calculating speed
                            speed = downloaded_size / elapsed_time / 1024  # Speed in KB/s

                        # Avoid division by zero when calculating percentage
                        percentage = 0
                        if total_size and total_size > 0:  # Only calculate percentage if total_size is non-zero
                            percentage = (downloaded_size / total_size) * 100

                        # Calculate total size in MB, if available
                        total_size_mb = "N/A"
                        if total_size and total_size > 0:
                            total_size_mb = total_size / 1024 / 1024  # Convert bytes to MB

                        # Print the stats with N/A if total size is unavailable
                        progress_bar = '=' * int(percentage // 2)
                        remaining_bar = ' ' * (50 - len(progress_bar))
                        sys.stdout.write(f"\r[{progress_bar}{remaining_bar}] {percentage:.2f}% | "
                                        f"Speed: {speed:.2f} KB/s | "
                                        f"Downloaded: {downloaded_size / 1024 / 1024:.2f} MB / "
                                        f"{total_size_mb} MB")
                        sys.stdout.flush()

            with open(log_download_path, "a") as download_log:
                download_log.write(f"{referer_url}\n")
            
            print(f"\nDownloaded {file_name} to {file_path}")
            remove_line(referer_url)
        
        else:
            print(f"Failed to download file from {download_url} with status code {response.status_code}")
    
    except Exception as e:
        print(f"Error downloading file: {e}")

def remove_line(referer_url):
    with open(output_file, "r") as f:
        lines = f.readlines()
    
    with open(output_file, "w") as f:
        for line in lines:
            if line.strip() != referer_url:
                f.write(line)
    
    with open(processed_file, "a") as f:
        f.write(f"{referer_url}\n")

# Function to process links line by line
def process_links(links):
    total_files = len(links)
    for index, link in enumerate(links):
        print(f"\nRemaining downloads: {total_files - index} / {total_files}")
        referer_url = link
        file_id, game_id = extract_ids_from_url(referer_url)
        if file_id and game_id:
            download_url = make_post_request(referer_url, file_id, game_id)
            if download_url:
                download_file(download_url, referer_url)
        time.sleep(random.uniform(1, 3))  # Random sleep between requests (to prevent rate-limiting)

if __name__ == "__main__":
    links = read_links(links_file)
    process_links(links)
