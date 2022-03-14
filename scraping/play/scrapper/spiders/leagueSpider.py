import scrapy
import re
import json
from datetime import datetime

url = 'https://www.leagueofgraphs.com/champions/stats/'
class LeagueSpider(scrapy.Spider):
    #scrapy crawl post -s CLOSESPIDER_ITEMCOUNT=1000 -o posts.json
    name = "league"
    start_urls = [url+row['championSlug']  for row in json.load(open('champNames.json'))]

    def parse(self, response):
        champ = response.url.split('/')[-1]
        item = {'champion' : champ}
        cols = ['popularity','winrate','banrate']
        variable = response.css('script:contains("graphGrid")::text').getall()[0:3]
        for script,col in zip(variable,cols):
            s_vetor, = re.search(r"data: (\[.*\]\]),",script).groups(1)
            vector = eval(s_vetor)
            vector = [(datetime.fromtimestamp(t/1000),data) for t, data in vector]
            item[col] = vector
        yield item

##//script[contains(.,'graphFunc')/text()']
## //graphFunc

##var 



