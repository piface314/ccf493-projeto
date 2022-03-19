from datetime import datetime
from scrapy import Spider
import re


class PlayHistorySpider(Spider):

    name = "playhistory"
    start_urls = ['https://www.leagueofgraphs.com/']

    def parse(self, response):
        for res in response.css('#championListBox div.championBox a::attr(href)'):
            url = res.get().replace('/builds/','/stats/')
            yield response.follow(url, self.parse_stats_page)

    def parse_stats_page(self, response):
        yield {'champion': self.parse_champion_name(response)} | self.parse_graphs(response)

    def parse_champion_name(self, response):
        return response.css('div.pageBanner div.txt h2::text').get()

    def parse_graphs(self, response):
        atts = ['popularity', 'winrate', 'banrate']
        scripts = response.css('script:contains("graphGrid")::text').getall()
        return {att: self.parse_graph(script) for script, att in zip(scripts, atts)}

    def parse_graph(self, script_tag):
        str_vector, = re.search(r"data: (\[.*\]\]),", script_tag).groups(1)
        vector = eval(str_vector)
        return [(datetime.fromtimestamp(t/1000), data) for t, data in vector]
