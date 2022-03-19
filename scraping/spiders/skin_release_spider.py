from scrapy import Spider


class SkinReleaseSpider(Spider):

    name = "skinrelease"
    start_urls = ["https://leagueoflegends.fandom.com/wiki/List_of_champion_skins_(League_of_Legends)"]

    def parse(self, response):
        for tr in response.xpath('//table[contains(@class,"article-table")]/tbody/tr'):
            item = self.parse_row(tr)
            if item:
                yield item

    def parse_row(self, tr):
        champion = tr.xpath('./td/@data-champion').get()
        if champion is None:
            return None
        return {
            'champion': champion,
            'skin': tr.xpath('./td/@data-skin').get(),
            'release': tr.xpath('./td[4]/@data-sort-value').get()
        }
