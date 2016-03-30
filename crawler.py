import urllib
from bs4 import BeautifulSoup
import json
from time import localtime, strftime
import sys
import logging

TIMESTAMP = strftime("%Y%m%d%H%M%S", localtime())

logging.basicConfig(filename='./logs/'+TIMESTAMP+'_crawl.log',format='%(asctime)s : %(levelname)s:  %(message)s',  datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

NOT_FOUND = 'NotFound'
ERROR_404 = 'error404'
BASE_URL = 'http://www.bbvaapimarket.com/'
BASE_URL_EXTENDED = 'http://www.bbvaapimarket.com/web/api_market/'

def to_file(crawled):
	logging.info('to_file - start')
	print TIMESTAMP
	#print json.dumps(crawled)
	filename = './data/'+TIMESTAMP + '_crawl.json'
	with open(filename, 'w') as outfile:
		json.dump(crawled, outfile, indent=2)
	logging.info('to_file - end')

def get_all_links(html):
	links = []
	for link in html.find_all('a'):
		links.append(link.get('href'))
	return links

def print_links(html):
	print len(get_all_links(html))


def get_unique_links(html):
	links = []
	for link in html.find_all('a'):
		href = link.get('href')
		if href not in links and href != None:
			links.append(href)
	return links

def print_unique_links(html):
	print len(get_unique_links(html))

def get_url_content(url):
	try:
		page = urllib.urlopen(url).read()
		return page
	except:
		logging.error('EXCEPT - get_url_content - '+url)
		return NOT_FOUND

def resolve_url(url, href):
	"""
	This method evaluates the href to generate the full url of the href
	"""
	logging.info('RESOLVE URL - URL - '+url)
	logging.info('RESOLVE URL - HREF - '+href)
	if url == BASE_URL:
		url = BASE_URL_EXTENDED
		logging.debug('RESOLVE URL - CHANGE URL - '+url)

	resolved_url = ''
	if href.find('#') == 0:
		logging.debug(' RESOLVE URL - FOUND PAGE LINK')
		resolved_url = url + href
	elif href.find('../') > -1:
		logging.debug(' RESOLVE URL - FOUND PREVIOUS PARENT PAGE')
		count = len(href.split('../')-1)
		resolved_url = '/'.join(b.split('/',-2)[:-3])
	elif href.find('./') > -1:
		logging.debug(' RESOLVE URL - FOUND NEXT CHILD PAGE')
		resolved_url = url + href[2:]
	elif href.find('http') > -1:
		logging.debug(' RESOLVE URL - FOUND EXTERNAL LINK PAGE')
		resolved_url = href
	else: # EX.: href='products'
		resolved_url = url + href

	logging.info('RESOLVED URL - '+resolved_url)
	return resolved_url

def evaluate_content(url, content):
	result = []

	soup = BeautifulSoup(content, 'html.parser')

	if len(soup.find_all("section", class_=ERROR_404)) == 0:
		unique_links = get_unique_links(soup)
		for link in unique_links:
			resolved_link = resolve_url(url, link)
			link_content = get_url_content(resolved_link)
			
			if link_content is NOT_FOUND:
				logging.debug('NOT_FOUND: '+link)
				result.append([link,link_content])
			else:
				logging.debug('URL: '+link)
				soup_link = BeautifulSoup(link_content, 'html.parser')
				logging.debug('URL - TITLE: '+soup_link.title.string)
				result.append([link,soup_link.title.string])
	else:
		logging.warning('404')
		result = [ERROR_404] 
	return result

def crawl_web(seed):
	logging.info('STARTING CRAWL_WEB PROCESS')
	logging.info('SEED: '+seed)
	print 'Crawling '+seed
	
	to_crawl = [seed]
	crawled = {}

	while len(to_crawl)>0:
		url = to_crawl.pop()
		if url not in crawled:
			logging.info('TO CRAWL: '+url)
			content = get_url_content(url)
			if content == NOT_FOUND:
				logging.debug('NOT_FOUND: '+link)
				links = [content]
			else:
				links = evaluate_content(url, content)
			crawled[url]=links
		else:
			logging.info('CRAWLED: '+url)

	to_file(crawled)
	print 'Done crawling'
	logging.info('END CRAWL_WEB PROCESS')


def main(argv):
	crawl_web(argv[0])
	#crawl_web('https://www.bbvaapimarket.com/web/api_market/ffa')

if __name__ == "__main__":
    main(sys.argv[1:])