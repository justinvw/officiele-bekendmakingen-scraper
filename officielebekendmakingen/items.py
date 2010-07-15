from scrapy.item import Item, Field

class OfficielebekendmakingenItem(Item):
	creator = Field()
	docType = Field()
	pubDate = Field()
	identifier = Field()
	htmlUrl = Field()
	pdfUrl = Field()
	xmlUrl = Field()
