import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import EuroclearItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'
base = 'https://www.euroclear.com/bin/euroclear/search/marketing/newsandinsights.query.json?offset={}&f.facet_insights-formats=press-release&f.facet_entity=group&language=en'
class EuroclearSpider(scrapy.Spider):
	name = 'euroclear'
	offset = 0
	start_urls = [base.format(offset)]
	counter = 0
	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['results'])):
			links = data['results'][index]['url']
			yield response.follow(links, self.parse_post)

		# offset is 0,10,20,30,40,50... 10 results per query
		iterations = int(data['total']/10 + (data['total'] % 10 > 0))
		if self.counter <= iterations:
			self.counter += 1
			self.offset += 10
			yield response.follow(base.format(self.offset), self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[@class="pageheader__meta__date"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('(//div[@class="parsys"])[1]//text() | //div[@class="adetails"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		if any('For more information about Euroclear' in text for text in content):
			content = content[:-3]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=EuroclearItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
