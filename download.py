import requests
import time
import random
import os
import re
import sys

### Set variables here ###
links_file = "output.txt"
# Login to Nexus and go to a single mod page up until the slow download button. Open web console, network tab and click on slow download. See the Post Request and copy the value of cookie in here
session_cookies = ""
#download_directory = "downloads"
download_directory = "E:\Wabbajack Downloads"
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
    # Extract the file_id and game_id using a regular expression
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
            # Inspect the response content type
            response_data = response.json()
            print("Response Content: ", response.text)  # Print response to debug

            # Check if response_data is a list and try to extract the URL
            if isinstance(response_data, list):
                # Assuming the first element in the list contains the desired data
                download_url = response_data[0].get("url", "")
            else:
                # If it's not a list, handle it as if it were a dictionary
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

def download_file(download_url, referer_url):
    try:
        # Ensure the directory exists
        os.makedirs(download_directory, exist_ok=True)
        
        # Extract the file name from the download URL
        file_name = download_url.split("/")[-1].split("?")[0]
        
        # Define the full path to save the file
        file_path = os.path.join(download_directory, file_name)
        
        # Check if the file already exists
        if os.path.exists(file_path):
            with open(log_skip_path, "a") as skip_log:
                skip_log.write(f"Skipped: {file_name} (already exists) - URL: {referer_url}\n")
            print(f"File {file_name} already exists. Skipping download.")
            remove_line(referer_url)
            return  # Skip downloading
        
        # Send GET request to download the file
        response = requests.get(download_url, stream=True)
        
        if response.status_code == 200:
            # Get total file size from the headers
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            # Save the file to the specified location
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Calculate percentage
                        percentage = (downloaded_size / total_size) * 100
                        
                        # Print the progress bar
                        progress_bar = '=' * int(percentage // 2)
                        remaining_bar = ' ' * (50 - len(progress_bar))  # 50 is the width of the progress bar
                        sys.stdout.write(f"\r[{progress_bar}{remaining_bar}] {percentage:.2f}%")
                        sys.stdout.flush()
            
            # Log the successful download
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
            
    # Remove the line corresponding to the current referer_url
    with open(output_file, "w") as f:
        for line in lines:
            if line.strip() != referer_url:  # Ensure we're not removing the current referer_url
                f.write(line)
    
    # Append the processed referer_url to processed_output.txt
    with open(processed_file, "a") as f:
        f.write(f"{referer_url}\n")
        
# Function to process links line by line
def process_links(links):
    for link in links:
        referer_url = link
        # Extract file_id and game_id from the URL
        file_id, game_id = extract_ids_from_url(referer_url)
        if file_id and game_id:
            download_url = make_post_request(referer_url, file_id, game_id)
            if download_url:
                download_file(download_url, referer_url)
        time.sleep(random.uniform(1, 3))  # Random sleep between requests (to prevent rate-limiting)

if __name__ == "__main__":
    links = read_links(links_file)
    process_links(links)
