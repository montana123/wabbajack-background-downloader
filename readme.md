# Wabbajack-background-downloader

This python program expects a file with all the mods you want to download from nexus mods. It works with premium or non premium account.

Example output.txt file:

https://www.nexusmods.com/skyrimspecialedition/mods/84686?tab=files&file_id=364791
https://www.nexusmods.com/skyrimspecialedition/mods/61497?tab=files&file_id=254891
https://www.nexusmods.com/skyrimspecialedition/mods/55282?tab=files&file_id=237992

One url per line. You can use the Wabbajack-fast-downloader python tool to extract the urls: https://github.com/M1n-74316D65/Wabbajack-fast-downloader
Use the CLI tool to extract the modlist file.

# Simple Download Clicker

I also have a SimpleDownloadClicker.ahk script in that repo in case some mods are missing in the end.

# Requirements

- [Python 3.x](https://www.python.org)

# Create .env file:

Create a .env file in root directory and put your session_cookies from nexusmods in there.

Login to Nexus and go to a single mod page up until the slow download button. Open web console, network tab and click on slow download. See the Post Request and copy the value of cookie in here

.env File content:
SESSION_COOKIES="your_session_cookies_value_here"