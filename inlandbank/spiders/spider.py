import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import IinlandbankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class IinlandbankSpider(scrapy.Spider):
	name = 'inlandbank'
	start_urls = ['https://www.inlandbank.com/about-us']

	def parse(self, response):
		yield response.follow(response.url, self.parse_post)

	def parse_post(self, response):
		articles = response.xpath('//div[@class="expandable-list"][1]/h2')

		for index in range(len(articles)):
			item = ItemLoader(item=IinlandbankItem(), response=response)
			item.default_output_processor = TakeFirst()

			date = response.xpath(f'//div[@class="expandable-list"][1]/div[@class="expandable-list-content"][{index+1}]/p[position()<3]//text() |//div[@class="expandable-list"][1]/div[@class="expandable-list-content"][{index+1}]/strong/following-sibling::text()[1]').getall()
			date = re.findall(r'\w+\s\d+\,\s\d+', ''.join(date))
			title = response.xpath(f'//div[@class="expandable-list"][1]/h2[{index+1}]//text()').get().strip()
			content = response.xpath(f'//div[@class="expandable-list"][1]/div[@class="expandable-list-content"][{index+1}]//text()').getall()
			content = [p.strip() for p in content if p.strip()]
			content = re.sub(pattern, "", ' '.join(content))

			item.add_value('title', title)
			item.add_value('link', response.url)
			item.add_value('content', content)
			item.add_value('date', date)

			yield item.load_item()
