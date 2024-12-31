# Create .env file:

Create a .env file in root directory and put your session_cookies from nexusmods in there.

Login to Nexus and go to a single mod page up until the slow download button. Open web console, network tab and click on slow download. See the Post Request and copy the value of cookie in here

.env File content:
SESSION_COOKIES="your_session_cookies_value_here"