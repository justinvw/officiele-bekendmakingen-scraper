from scrapy.conf import settings
from scrapy.xlib.pydispatch import dispatcher
from scrapy.core import signals
from scrapy.contrib.exporter import XmlItemExporter
from datetime import datetime

class OfficielebekendmakingenPipeline(object):
	def __init__(self):
		dispatcher.connect(self.spider_opened, signals.spider_opened)
		dispatcher.connect(self.spider_closed, signals.spider_closed)
		self.files = {}

	def spider_opened(self, spider):
		logtime = datetime.today()
		file = open('%s/itemlog_%s_%s.xml' %(settings.get('LOG_DIR'), logtime.strftime('%Y-%m-%d_%H_%M'), spider.domain_name), 'w+b')
		self.files[spider] = file
		self.exporter = XmlItemExporter(file)
		self.exporter.start_exporting()
	
	def spider_closed(self, spider):
		self.exporter.finish_exporting()
		file = self.files.pop(spider)
		file.close()
		
	def process_item(self, spider, item):
		for field in item:
			if item[field]:
				item[field] = item[field][0]
		self.exporter.export_item(item)
		return item