import scrapy
import csv
import os
import re
import random
import hashlib
import shutil
import time
from parsel import Selector
from datetime import datetime


from tqdm import tqdm


class CoursesSpider(scrapy.Spider):
    name = "courses"

    def __init__(self, csv_file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not csv_file:
            raise ValueError("You must provide -a csv_file=yourfile.csv")

        self.csv_file = csv_file
        self.output_dir = os.path.splitext(os.path.basename(csv_file))[0]

        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

        self.start_urls = []
        self.rows = []

        # open CSV safely
        with open(csv_file, newline="", encoding="cp1252", errors="ignore") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # wrap with tqdm for progress bar
        for row in tqdm(rows, desc=f"Loading URLs from {csv_file}", unit="row"):
            try:
                url = next((v for v in row.values()
                           if v and v.strip().startswith("http")), None)
                if url:
                    self.start_urls.append(url.strip())
                    self.rows.append(row)
                else:
                    self._log_error(row, "❌ No valid link found in row")
            except Exception as e:
                self._log_error(row, f"❌ CSV row read error: {e}")

        self.files_saved = 0

    def start_requests(self):
        for url, row_data in zip(self.start_urls, self.rows):
            yield scrapy.Request(
                url,
                callback=self.parse_course,
                errback=self.handle_error,
                meta={"row_data": row_data,
                      "original_url": url, "retry_count": 0},
                dont_filter=True
            )

    def parse_course(self, response):
        url = response.meta['original_url']

        try:
            # ✅ generate ultra-unique filename
            last_part = response.url.rstrip('/').split('/')[-1]
            safe_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', last_part) or "course"
            hash_part = hashlib.md5(response.url.encode()).hexdigest()[:10]
            rand_num = random.randint(10**8, 10**12)
            timestamp = int(time.time() * 1000)
            file_name = f"{safe_slug}_{hash_part}_{timestamp}_{rand_num}.txt"

            # start with response.body
            sel = Selector(text=response.text)

            # remove unwanted tags completely
            for tag in ["script", "style", "header", "footer", "nav", "svg", "noscript"]:
                for node in sel.xpath(f"//{tag}"):
                    node_root = node.root
                    node_root.getparent().remove(node_root)

            # extract visible text (ignoring script/style/header/footer)
            text_parts = sel.xpath("//body//text()").getall()

            text_parts = [t.strip() for t in text_parts if t.strip()]
            body_text = "\n".join(
                text_parts) if text_parts else "⚠️ No visible text extracted."

            # ✅ save inside folder, only URL + body text
            file_path = os.path.join(self.output_dir, file_name)

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"URL: {url}\n\n")
                    f.write(body_text)
            except UnicodeEncodeError:
                # fallback: encode non-UTF8 chars safely
                with open(file_path, "w", encoding="utf-8", errors="replace") as f:
                    f.write(f"URL: {url}\n\n")
                    f.write(body_text)

            self.files_saved += 1
            self.log(f"✅ Saved course page: {file_path}")

        except Exception as e:
            # log errors
            row_data = response.meta.get('row_data', {})
            self._log_error(row_data, f"❌ Parsing error for {url}: {e}")

    def handle_error(self, failure):
        """Handles request-level errors (timeouts, 404, etc.) and retries."""
        meta = failure.request.meta
        row_data = meta.get("row_data", {})
        url = meta.get("original_url", "Unknown URL")
        retry_count = meta.get("retry_count", 0)

        if retry_count < 3:
            self.log(f"⚠️ Retry {retry_count + 1} for {url}",
                     level=scrapy.logformatter.logging.WARNING)
            yield scrapy.Request(
                url,
                callback=self.parse_course,
                errback=self.handle_error,
                meta={"row_data": row_data, "original_url": url,
                      "retry_count": retry_count + 1},
                dont_filter=True
            )
        else:
            self._log_error(row_data, f"❌ Failed after 5 retries: {url}")

    def _log_error(self, row_data, message: str):
        """Writes errors into a dedicated log file inside the output dir."""
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        safe_row = " | ".join(f"{k}={v}" for k, v in row_data.items() if v)
        log_text = f"[{ts}] {message}\n\n"

        error_file = os.path.join(self.output_dir, "errors.log")
        with open(error_file, "a", encoding="utf-8") as f:
            f.write(log_text)

        self.log(message, level=scrapy.logformatter.logging.ERROR)
