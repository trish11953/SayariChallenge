import scrapy
import json
from scrapy.http import JsonRequest
from scrapy import signals


class CompanySpider(scrapy.Spider):
    name = "companies"
    start_urls = [
        "https://firststop.sos.nd.gov/api/Records/businesssearch",
    ]
    custom_settings = {"DOWNLOAD_DELAY": 0.1}  # sets the delay to 0.1 seconds

    formdata = {"SEARCH_VALUE": "X", "STARTS_WITH_YN": "true", "ACTIVE_ONLY_YN": "true"}
    x_titled = reg = {}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CompanySpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        with open("output.json", "w") as f:
            for item in self.x_titled.items():
                f.write(json.dumps(item))
                f.write("\n")
        spider.logger.info("Spider closed: %s", spider.name)

    def start_requests(self):
        for url in self.start_urls:
            yield JsonRequest(
                url=url,
                headers={
                    "accept": "/",
                    "origin": "https://firststop.sos.nd.gov",
                    "referer": "https://firststop.sos.nd.gov/search/business",
                    "authorization": "undefined",
                },
                data=self.formdata,
                callback=self.parse_httpbin,
            )

    def parse_httpbin(self, response):
        data = json.loads(response.text)
        rows = data["rows"]
        for id in rows:
            if rows[id]["TITLE"][0].startswith("X"):
                self.x_titled[id] = rows[id]
                yield JsonRequest(
                    url="https://firststop.sos.nd.gov/api/FilingDetail/business/"
                    + str(id)
                    + "/false",
                    headers={
                        "accept": "/",
                        "origin": "https://firststop.sos.nd.gov",
                        "referer": "https://firststop.sos.nd.gov/search/business",
                        "authorization": "undefined",
                    },
                    callback=self.parse_details,
                    cb_kwargs={"id": id},
                )

    def parse_details(self, response, id):
        data = json.loads(response.text)
        if self.x_titled[id]:
            self.x_titled[id]["Additional information"] = data
