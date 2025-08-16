import scrapy
import csv
import os
import re
import random


class CoursesSpider(scrapy.Spider):
    name = "courses"

    def __init__(self, csv_file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not csv_file:
            raise ValueError("You must provide -a csv_file=yourfile.csv")

        # ✅ folder name = CSV file name (without extension)
        self.csv_file = csv_file
        self.output_dir = os.path.splitext(os.path.basename(csv_file))[0]
        os.makedirs(self.output_dir, exist_ok=True)

        self.start_urls = []
        self.rows = []

        # open CSV safely (Excel/Windows friendly)
        with open(csv_file, newline="", encoding="cp1252", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = list(row.values())[2]  # ✅ first column is the link
                self.start_urls.append(url)
                self.rows.append(row)

        self.files_saved = 0  # ✅ correct indentation

    def start_requests(self):
        for url, row_data in zip(self.start_urls, self.rows):
            yield scrapy.Request(url, callback=self.parse_course, meta={"row_data": row_data})

    def parse_course(self, response):
        row_data = response.meta['row_data']

        last_part = response.url.rstrip('/').split('/')[-1]
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', last_part)
        rand_num = random.randint(10**8, 10**12)
        file_name = f"{safe_name}_{rand_num}.txt"

        # extract visible text (ignoring script/style/header/footer)
        text_parts = response.xpath(
            '//body//*[not(self::script) and not(self::style) and not(self::header) and not(self::footer)]/text()'
        ).getall()
        text_parts = [t.strip() for t in text_parts if t.strip()]
        body_text = "\n".join(text_parts)

        # row metadata
        header_lines = [f"{col}: {val}" for col, val in row_data.items()]
        header_text = "\n".join(header_lines)

        # ✅ save inside folder with same name as CSV
        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(header_text + "\n\n" + body_text)

        self.files_saved += 1
        self.log(f"Saved course page: {file_path}")
