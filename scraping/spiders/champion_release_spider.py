from scrapy import Spider


class ChampionReleaseSpider(Spider):

    name = "championrelease"
    start_urls = ["https://leagueoflegends.fandom.com/wiki/List_of_champions"]

    def parse(self, response):
        for tr in response.xpath('//table[contains(@class,"article-table")]/tbody/tr'):
            item = self.parse_row(tr)
            if item:
                yield item

    def parse_row(self, tr):
        try:
            return {
                'champion': tr.xpath('./td/span/@data-champion').get(),
                'release': tr.xpath('./td[3]//text()').get().strip()
            }
        except:
            return None
