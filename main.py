import ConfigParser
import sys
from crawler import crawl_web_with_prop
PROPERTIES_FILE_PATH = 'properties.cfg'

try:
	config = ConfigParser.ConfigParser()
	config.read(PROPERTIES_FILE_PATH)
except Exception as e:
	print e

def main(argv):
	environment = argv[0].lower()
	base_url = config.get(environment,'BASE_URL')
	#print 'BASE_URL: '+base_url
	base_url_extended = config.get(environment,'BASE_URL_EXTENDED')
	#print 'BASE_URL_EXTENDED: '+base_url_extended
	#crawl_web_with_prop('https://www.bbvaapimarket.com/web/api_market/bbva/paystats/documentation', base_url_extended)
	#crawl_web_with_prop('https://www.bbvaapimarket.com/web/api_market/register', base_url_extended)
	crawl_web_with_prop(base_url, base_url_extended)


if __name__ == "__main__":
	try:
		if len(sys.argv) > 1:
			main(sys.argv[1:])
		else:
			raise Exception('NO ENVIRONMENT PROVIDED.\nPLEASE TRY AGAIN PROVIDING ONE OF THE FOLLOWING ENVIRONMENTS [ DEV, PRE, PRO ] ')
	except Exception as e:
		print e