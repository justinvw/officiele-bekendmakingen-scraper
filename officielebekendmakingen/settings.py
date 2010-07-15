BOT_NAME = 'officielebekendmakingen'
BOT_VERSION = '0.1'
LOG_DIR = 'logs' # Absolute path to the directory which holds the logfiles
DOWNLOAD_DIR = 'downloads' # Absolute path to the directory which holds the downloaded XML files
DOCUMENT_TYPES = ['Agenda', 'Handeling', 'Kamerstuk', 'AanhangselvandeHandelingen', 'Kamervragenzonderantwoord', 'Nietdossierstuk', 'Bijlage'] # Specifies which types of documents should be downloaded, values need to correspond with those used in the search url
PUBLICATION_DATE_FROM = '2005-01-01'
PUBLICATION_DATE_TILL = '2010-06-01'
SPIDER_MODULES = ['officielebekendmakingen.spiders']
ITEM_PIPELINES = ['officielebekendmakingen.pipelines.OfficielebekendmakingenPipeline']
NEWSPIDER_MODULE = 'officielebekendmakingen.spiders'
DEFAULT_ITEM_CLASS = 'officielebekendmakingen.items.OfficielebekendmakingenItem'
CONCURRENT_REQUESTS_PER_SPIDER = 4
DOWNLOAD_DELAY = 0.50
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

