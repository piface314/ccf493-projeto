from scrapy import Spider
import re


class PatchHistorySpider(Spider):

    name = "patchhistory"
    # TODO: tornar configurável de qual patch começar
    start_urls = ["https://leagueoflegends.fandom.com/wiki/V12.5"]

    months = {
        'january': 1,
        'february': 2,
        'march': 3,
        'april': 4,
        'may': 5,
        'june': 6,
        'july': 7,
        'august': 8,
        'september': 9,
        'october': 10,
        'november': 11,
        'december': 12
    }

    @staticmethod
    def alltext(elem):
        return (''.join(elem.xpath("./text() | .//text()").getall())
                .replace('\xa0', '')
                .replace('\u2212', '-')
                .replace('\u2013', '-')
                .replace('\u300c', '[')
                .replace('\u300d', ']')
                .replace('\u00d7', ' x ')
                .replace('\u2018', "'")
                .replace('\u2019', "'")
                .strip())

    def parse(self, response):
        yield {
            'id': self.parse_id(response),
            'url': response.url,
            'date': self.parse_date(response),
            'champions': self.parse_champions(response),
        }
        prev_url = self.parse_url(response, 'Prev')
        if prev_url:
            yield response.follow(prev_url, self.parse)

    def parse_id(self, response):
        return response.xpath("//aside/h2/a[@title='Patch']/parent::h2/text()").get().strip()

    def parse_date(self, response):
        s = response.xpath("//td[@data-source='Release']/text()").getall()
        try:
            s = ''.join(s).strip()
            month, day, year = re.match(r'(\w+)\s+(\d+).*?(\d+)', s).groups()
            month = self.months[month.lower()]
            return f'{year}-{month:02d}-{int(day):02d}'
        except:
            return None

    def parse_champions(self, response):
        selector = (response.xpath("//dl[./dt/span[@data-champion]]")
                    or response.xpath("//p[./span[@data-champion]]"))
        champions = [self.parse_champion(dl) for dl in selector]
        return champions

    def parse_champion(self, dl_elem):
        selector = dl_elem.xpath("following-sibling::ul[1]/li")
        champion = {
            'name': dl_elem.xpath(".//@data-champion").get(),
            'changes': [self.parse_changes(li) for li in selector]
        }
        return champion

    def parse_changes(self, li_elem):
        lines = self.alltext(li_elem).split('\n')
        if len(lines) == 1:
            return lines[0]
        return {'about': lines[0], 'lines': lines[1:]}

    def parse_url(self, response, dir):
        prefix = re.match(r'^(https://.*?)/', response.url).group(1)
        href = response.xpath(f"//td[@data-source='{dir}']/a/@href")
        return prefix + href.get().strip() if href else None
