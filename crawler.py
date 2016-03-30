import urllib
from bs4 import BeautifulSoup
import json
from time import localtime, strftime
import sys
import logging

TIMESTAMP = strftime("%Y%m%d%H%M%S", localtime())

logging.basicConfig(filename='logs/'+TIMESTAMP+'_crawl.log',format='%(asctime)s : %(levelname)s:  %(message)s',  datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

NOT_FOUND = 'NotFound'
ERROR_404 = 'error404'
MAIL_TO = 'mailto:'
NOT_CRAWL = 'NotCrawl'
BASE_URL = 'http://www.bbvaapimarket.com/'
BASE_URL_EXTENDED = 'http://www.bbvaapimarket.com/web/api_market/'

def to_file(crawled):
	logging.info('to_file - start ')
	print TIMESTAMP
	#print json.dumps(crawled)
	filename = 'data/'+TIMESTAMP + '_crawl.json'
	logging.info('to_file - writing -  '+filename)
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
		if href not in links and href != None and href.find(MAIL_TO)==-1:
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

	#TODO check if ../web/api  /web/api/reg
	resolved_url = ''
	if href.find('#') == 0:
		logging.debug(' RESOLVE URL - FOUND PAGE LINK')
		resolved_url = url + href
	elif href.find('../') > -1:
		logging.debug(' RESOLVE URL - FOUND PREVIOUS PARENT PAGE - '+url)
		count = len(href.split('../')-1)
		resolved_url = '/'.join(url.split('/',-2)[:-3])		
		logging.debug(' RESOLVE URL - FOUND PREVIOUS PARENT PAGE - SPLIT - '+resolved_url)
		resolved_url += href
	elif href.find('./') > -1:
		logging.debug(' RESOLVE URL - FOUND NEXT CHILD PAGE - '+url)
		resolved_url = url.rsplit('/',1)
		resolved_url = resolved_url[0]
		logging.debug(' RESOLVE URL - FOUND NEXT CHILD PAGE- SPLIT - '+resolved_url)
		resolved_url += '/' + href[2:]
	elif href.find('http') > -1:
		logging.debug(' RESOLVE URL - FOUND FULL LINK PAGE')
		resolved_url = href
	elif url.find(href) > -1:
		logging.debug(' RESOLVE URL - FOUND HREF INCLUDED IN URL - '+url)
		resolved_url = url
	elif href.find(MAIL_TO) > -1:
		logging.debug(' RESOLVE URL - FOUND MAILTO')
		resolved_url = MAIL_TO
	else: # EX.: href='products'
		logging.debug(' RESOLVE URL - FOUND CHILD PAGE - '+url)
		resolved_url = url.rsplit('/',1)
		resolved_url = resolved_url[0]
		logging.debug(' RESOLVE URL - FOUND CHILD PAGE- SPLIT - '+resolved_url)
		resolved_url+= '/' + href

	logging.info('RESOLVED URL - '+resolved_url)
	return resolved_url

def evaluate_content(url, soap_content):
	result = []

	unique_links = get_unique_links(soap_content)
	for link in unique_links:
		resolved_link = resolve_url(url, link)
		if resolved_link.find(MAIL_TO) > -1:
			logging.debug('MAIL_TO: '+link)
			result.append([link,MAIL_TO])
		elif resolved_link.find('/web/guest') > -1:
			logging.debug('NOT CRAWL LINK : '+link)
			logging.debug('NOT CRAWL RESOLVED LINL: '+resolved_link)
			result.append([link,NOT_CRAWL])
		else:
			link_content = get_url_content(resolved_link)
			
			if link_content is NOT_FOUND:
				logging.debug('NOT_FOUND: '+link)
				result.append([link,NOT_FOUND])
			else:
				logging.debug('URL: '+link)
				soup_link = BeautifulSoup(link_content, 'html.parser')
				logging.debug('URL - TITLE: '+soup_link.title.string)
				result.append([link,soup_link.title.string])

	return result

def add_to_list(listToAdd, toAdd):
	for item in toAdd:
		if item not in listToAdd:
			listToAdd.append(item)
	return listToAdd

def crawl_web(seed):
	logging.info('STARTING CRAWL_WEB PROCESS')
	logging.info('SEED: '+seed)
	print 'Crawling '+seed
	
	to_crawl = [seed]
	crawled_urls = []
	crawled = {}

	count = 0
	while len(to_crawl)>0 and count<=10:
		url = to_crawl.pop()
		logging.info('TO CRAWL: '+url)
		if url.find('#') > -1:
			url = url.split('#')[0]
			logging.info('TO CRAWL SPLIT: '+url)
		elif url.find('?') > -1:
			url = url.split('?')[0]
			logging.info('TO CRAWL SPLIT: '+url)
		if url != 'https://www.bbvaapimarket.com' and url.find('bbvaapimarket') > -1 and url.find('login') == -1:
			if url not in crawled_urls:
				crawled_urls.append(url)

				count+=1
				print count
				print url

				content = get_url_content(url)
				soup = BeautifulSoup(content, 'html.parser')

				if len(soup.find_all("section", class_=ERROR_404)) == 0:
					if content == NOT_FOUND:
						logging.debug('NOT_FOUND: '+url)
						links = [NOT_FOUND]
					elif content == MAIL_TO:
						logging.debug('MAIL_TO: '+url)
						links = [MAIL_TO]
					else:
						logging.debug('WITH_CONTENT: '+url)
						links = evaluate_content(url, soup)

						crawled[url]=links

						for link in links:
							#print str(links)
							logging.debug('NEW URLS TO CRAWL - '+link[0])
							resolved_link = resolve_url(url,link[0])
							if resolved_link not in crawled_urls and resolved_link not in to_crawl and resolved_link.find('bbvaapimarket')>-1 and resolved_link!=NOT_CRAWL:
								logging.debug('NEW URLS TO CRAWL - ADDED - '+link[0])
								to_crawl.append(link[0])

				else:
					logging.warning('ERROR_404:' +url)
					links = [ERROR_404]
			else:
				logging.info('CRAWLED: '+url)
		else:
			logging.warning('PAGE TO NOT CRAWL: '+url)

	print count
	if len(crawled)>0:
		for key in crawled:
			print key
	to_file(crawled)
	print 'Done crawling'
	logging.info('END CRAWL_WEB PROCESS')


def main(argv):
	crawl_web(argv[0])
	#crawl_web('https://www.bbvaapimarket.com/web/api_market/ffa')

if __name__ == "__main__":
    main(sys.argv[1:])