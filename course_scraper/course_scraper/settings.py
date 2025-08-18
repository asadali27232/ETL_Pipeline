BOT_NAME = "course_scraper"

SPIDER_MODULES = ["course_scraper.spiders"]
NEWSPIDER_MODULE = "course_scraper.spiders"

# ----------------------------
# Scrapy Optimized Settings
# ----------------------------

# Concurrency
CONCURRENT_REQUESTS = 64                  # Maximum concurrent requests
CONCURRENT_REQUESTS_PER_DOMAIN = 16       # Limit per domain to avoid bans
CONCURRENT_REQUESTS_PER_IP = 16

# Download
DOWNLOAD_DELAY = 0                         # No fixed delay for speed
RANDOMIZE_DOWNLOAD_DELAY = True            # Randomize delay if any
DOWNLOAD_TIMEOUT = 15                      # Fail fast on slow responses

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3                            # Retry failed requests up to 3 times
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# Redirects
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 10

# Cookies
COOKIES_ENABLED = False                    # Disable cookies for speed

# Headers
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/137.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Robots.txt
ROBOTSTXT_OBEY = False                     # Ignore robots.txt

# Logging
LOG_LEVEL = "INFO"

# Auto-throttle (optional)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.2
AUTOTHROTTLE_MAX_DELAY = 2
AUTOTHROTTLE_TARGET_CONCURRENCY = 8

# Retry middleware priority (ensure it runs)
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
}
