from scrapy.conf import settings
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import TakeFirst
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from datetime import datetime, timedelta
import libxml2
import os
import re
from officielebekendmakingen.items import OfficielebekendmakingenItem

class OfficielebekendmakingenSpider(CrawlSpider):
	def get_downloaded_documents():
		""" Returns a list with filenames of the already downloaded XML documents """
		# Find logfiles
		logdir = os.listdir(settings.get('LOG_DIR'))
		test = re.compile('itemlog_.*\.xml')
		logfiles = filter(test.search, logdir)
		
		documents = []
		
		# Open each logfile to collect the names of downloaded documents
		for logfile in logfiles:
		
			xml = libxml2.parseFile(settings.get('LOG_DIR') + '/' + logfile)

			for document in xml.xpathEval('//items/item'):
				xmldoc = document.xpathEval('xmlUrl')[0].content
				if xmldoc:
					documents.append(xmldoc)
		
		return documents
		
	def generate_search_urls(start, end, documenttypes):
		""" Returns a list of search urls based on given time and documenttype 
		criteria. """
		totaldays = (end + timedelta(days = 1) - start).days
		
		urls = []
		for day in range(totaldays):
			today = start + timedelta(days = day)
			for doctype in documenttypes:
				urls.append('https://zoek.officielebekendmakingen.nl/zoeken/resultaat/?zkt=Uitgebreid&pst=ParlementaireDocumenten&dpr=AnderePeriode&spd='+ today.strftime("%Y%m%d") + '&epd=' + today.strftime("%Y%m%d") + '&kmr=EersteKamerderStatenGeneraal|TweedeKamerderStatenGeneraal|VerenigdeVergaderingderStatenGeneraal&sdt=KenmerkendeDatum&par='+ doctype +'&dst=Opgemaakt|Opgemaakt+na+onopgemaakt&isp=true&pnr=1&rpp=10')
		
		return urls
	
	domain_name = 'zoek.officielebekendmakingen.nl'
	downloaded_documents = get_downloaded_documents()
	start_urls = generate_search_urls(datetime.strptime(settings.get('PUBLICATION_DATE_FROM'), '%Y-%m-%d'), datetime.strptime(settings.get('PUBLICATION_DATE_TILL'), '%Y-%m-%d'), settings.get('DOCUMENT_TYPES'))
	
	rules = (
		Rule(SgmlLinkExtractor(allow=(r'zoeken/resultaat/\?',), restrict_xpaths=['//div[@class="paginering boven"]'])),
		Rule(SgmlLinkExtractor(allow=(r'/',), restrict_xpaths=['//div[@class="lijst"]']), 'parse_item'),
	)
	
	def parse_item(self, response):
		""" Extracts the document information """
		hxs = HtmlXPathSelector(response)
		
		#item = OfficielebekendmakingenItem()
		item = {}
		item['creator'] = hxs.select('//meta[@name="DC.creator"]/@content').extract()
		item['docType'] = hxs.select('//meta[(@name="DC.type" or @name="DC.Type") and (@scheme="OVERHEIDop.AanhangselTypen" or @scheme="OVERHEIDop.Parlementair")]/@content').extract()
		item['identifier'] = hxs.select('//meta[@name="DC.identifier"]/@content').extract()
		item['pubDate'] = hxs.select('//meta[@name="DCTERMS.available"]/@content').extract()
		item['htmlUrl'] = hxs.select('//a[@id="permaHyperlink"]/@href').extract()
		item['pdfUrl'] = hxs.select('//a[@id="downloadPdfHyperLink"]/@href').extract()
		item['xmlUrl'] = hxs.select('//a[@id="downloadXmlHyperLink"]/@href').extract()
		
		# If an XML version is available, download it!
		if item['xmlUrl']:		
			if item['xmlUrl'][0] not in self.downloaded_documents:
				yield Request('https://zoek.officielebekendmakingen.nl/%s' %(item['xmlUrl'][0]), callback=lambda r: self.save_document(r, item))
		
	def save_document(self, response, item):
		""" Saves the downloaded XML docuemt, adds it to the list of downloaded documents 
		(to prevent duplicate downlads), and logs the downloaded item.
		"""
		if response.status == 200:
			self.downloaded_documents.append(item['identifier'])
			yield OfficielebekendmakingenItem(item)
			
			if not(os.path.exists(settings.get('DOWNLOAD_DIR') + '/' + item['docType'][0])):
				os.mkdir(settings.get('DOWNLOAD_DIR') + '/' + item['docType'][0])
			
			filename = response.url.split("/")[-1]
			open(settings.get('DOWNLOAD_DIR') + '/' + item['docType'][0] + '/' + filename, 'wb').write(response.body)
			
		else:
			self.log('Error fetching %s, status %s' %(response.url, response.status))
		

SPIDER = OfficielebekendmakingenSpider()