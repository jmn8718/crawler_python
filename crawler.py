import urllib
from bs4 import BeautifulSoup
import json
from time import localtime, strftime
import sys, os
import logging
from libs.out import to_file,save_loop, evaluate_crawled

TIMESTAMP = strftime("%Y%m%d%H%M%S", localtime())

logging.basicConfig(filename='logs/'+TIMESTAMP+'_crawl.log',format='%(asctime)s : %(levelname)s:  %(message)s',  datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

ANCHOR = 'Anchor'
EXCEPTION_GET = 'exceptionGET'
NOT_FOUND = 'NotFound'
ERROR_404 = 'error404'
NO_TITLE = 'NoTitle'
MAIL_TO = 'mailto:'
NOT_CRAWL = 'NotCrawl'
BASE_URL = 'https://www.bbvaapimarket.com/'
BASE_URL_WEB = 'https://www.bbvaapimarket.com/web/api_market/'
BASE_URL_EXTENDED = 'https://www.bbvaapimarket.com/web/api_market/home'

BASE_URL_PUBLIC = 'https://www.bbvaapimarket.com/web/api_market/'

def get_base_url(url):
	logging.info('GET BASE URL - '+url)
	urlArray = []
	urlArray.append('https://www.bbvaapimarket.com/' )
	urlArray.append('https://www.bbvaapimarket.com' )
	urlArray.append('www.bbvaapimarket.com/' )
	urlArray.append('www.bbvaapimarket.com' )
	urlArray.append('https://www.bbvaapimarket.com/web/api_market/' )
	urlArray.append('https://www.bbvaapimarket.com/web/api_market' )
	if url in urlArray:
		return BASE_URL_EXTENDED
	return url


def get_all_links(html):
	links = []
	for link in html.find_all('a'):
		links.append(link.get('href'))
	return links

def get_unique_links(html):
	links = []
	for link in html.find_all('a'):
		href = link.get('href')
		if href is not None and href not in links:
			if href.find(MAIL_TO)==-1 or href.find('javascript:void(0)'):
				links.append(href)
	return links

def get_url_content(url):
	try:
		page = urllib.urlopen(url).read()
		return page
	except Exception as e:
		print 'EXCEPT - get_url_content - '
		print e
		logging.error('EXCEPT - get_url_content - '+url)
		return EXCEPTION_GET

def resolve_url(url, href):
	"""
	This method evaluates the href to generate the full url of the href
	"""
	logging.info('RESOLVE URL - URL - '+url)
	logging.info('RESOLVE URL - HREF - '+href)
	if url == BASE_URL or url == BASE_URL[:-1] or url == BASE_URL_WEB[:-1]:
		url = BASE_URL_EXTENDED
		logging.debug('RESOLVE URL - CHANGE URL - '+url)

	#TODO check if ../web/api  /web/api/reg
	resolved_url = ''
	try:
		if href.find('/') == 0:
			logging.debug(' RESOLVE URL - FOUND / LINK')
			url_split = url.split('/')
			href_split = href.split('/')
			if href_split[1] in url_split:
				index = url_split.index(href_split[1])
				logging.debug(' RESOLVE URL - FOUND / LINK - INDEX - '+str(index))
				resolved_url_splits = url_split[:index]+href_split[1:]
				resolved_url = '/'.join(resolved_url_splits)
			else:
				logging.error(' RESOLVE URL - FOUND / LINK - NOT INDEX - ')

		elif href.find('#') == 0:
			logging.debug(' RESOLVE URL - FOUND PAGE LINK')
			resolved_url = url + href
		elif href.find('./') > -1:
			logging.debug(' RESOLVE URL - FOUND ./ in HREF')
			if url[-1]!='/':
				url = url.split('/')[:-1]
			else:
				url = url.split('/')
			resolved_url_splits = url + str(href).split('/')
			#print resolved_url_splits
			while '.' in resolved_url_splits:
				resolved_url_splits.remove('.')
			#print resolved_url_splits
			while '..' in resolved_url_splits:
				index = resolved_url_splits.index('..')
				#print index
				del resolved_url_splits[index]
				del resolved_url_splits[index-1]
				#print resolved_url_splits

			resolved_url='/'.join(resolved_url_splits)
		elif href.find('http') > -1:
			logging.debug(' RESOLVE URL - FOUND FULL LINK PAGE')
			resolved_url = href
		elif url.find(href) > -1:
			logging.debug(' RESOLVE URL - FOUND HREF INCLUDED IN URL - '+url)
			resolved_url = url
		elif href.find(MAIL_TO) > -1:
			logging.debug(' RESOLVE URL - FOUND MAILTO')
			resolved_url = MAIL_TO

		elif href.find('javascript:void(0)') > -1:
			logging.debug(' RESOLVE URL - FOUND javascript:void(0)')
			resolved_url = NOT_CRAWL
		else: # EX.: href='products'
			logging.debug(' RESOLVE URL - FOUND CHILD PAGE - '+url)
			if url[-1] == '/': 
				resolved_url = url+ href
			else:
				resolved_url = url.rsplit('/',1)[0] + '/' + href
			logging.debug(' RESOLVE URL - FOUND CHILD PAGE- SPLIT - '+resolved_url)
	except Exception as e:
		logging.error('EXCEPT - resolve_url - '+url)

	logging.info('RESOLVED URL - '+resolved_url)
	return resolved_url

def evaluate_content(url, soup_content):
	try:
		logging.info('EVALUATE CONTENT')
		result = []

		unique_links = get_unique_links(soup_content)
		for link in unique_links:

			logging.warning('\n\n '+str(link)+' \n\n')
			resolved_link = resolve_url(url, link)
			logging.warning('\n\n '+resolved_link+' \n\n')
			if link.find('#') == 0:
				logging.debug('URL: '+url)
				logging.debug('ANCHOR: '+link)
				result.append([link,ANCHOR])
			elif resolved_link.find(MAIL_TO) > -1:
				logging.debug('MAIL_TO: '+link)
				result.append([link,MAIL_TO])
			elif resolved_link.find(NOT_CRAWL) > -1:
				logging.debug('NOT_CRAWL: '+link)
				result.append([link,NOT_CRAWL])
			elif resolved_link.find('/web/guest') > -1 or resolved_link.find('file://') > -1 or resolved_link.find('.zip') > -1 or resolved_link.find('.pdf') > -1:
				logging.debug('NOT CRAWL LINK : '+link)
				logging.debug('NOT CRAWL RESOLVED LINK: '+resolved_link.encode('ascii', 'ignore').decode('ascii'))
				result.append([link,NOT_CRAWL])
			else:
				link_content = get_url_content(resolved_link)
				logging.warning('ELSE-----------------')
				
				if link_content is EXCEPTION_GET:
					logging.debug('EXCEPTION_GET: '+link)
					result.append([link,EXCEPTION_GET])
				elif link_content is NOT_FOUND:
					logging.debug('NOT_FOUND: '+link)
					result.append([link,NOT_FOUND])
				else:
					logging.debug('URL: '+link)
					soup_link = BeautifulSoup(link_content, 'html.parser')
					logging.info('EVALUATE CONTENT - SOUP ---\n'+link)
					if soup_link.title is not None and soup_link.title.string is not None:
						logging.debug('URL - TITLE: '+soup_link.title.string.encode('ascii', 'ignore').decode('ascii'))
						#TODO CHECK
						result.append([link,soup_link.title.string.encode('ascii', 'ignore').decode('ascii')])
					else:
						print 'EVALUATING-> ' + link
						print resolved_link
						if len(soup_link.find_all("section", class_=ERROR_404)) == 0:
							logging.warning('URL - No title')
							result.append([link,NO_TITLE])
						else:
							logging.warning('URL - 404')							
							result.append([link,ERROR_404])


		#logging.info('EVALUATE CONTENT '+str(result))
		return result
	except Exception as e:
		print 'EXCEPT - EVALUATE CONTENT - '
		print e
		logging.error('EXCEPT - EVALUATE CONTENT - '+url)
		return ([link,ERROR_404])

def add_to_list(listToAdd, toAdd):
	for item in toAdd:
		if item not in listToAdd:
			listToAdd.append(item)
	return listToAdd

def crawl_web(seed):
	print BASE_URL
	print BASE_URL_EXTENDED
	logging.info('STARTING CRAWL_WEB PROCESS')
	logging.info('SEED: '+seed)
	print 'Crawling '+seed
	
	to_crawl = [seed]
	crawled_urls = []
	crawled = {}

	count = 0
	while len(to_crawl)>0: # and count<=5:
		url = to_crawl.pop()
		url = get_base_url(url)
		logging.info('TO CRAWL: '+url)
		if url.find('#') > -1:
			url = url.split('#')[0]
			logging.info('TO CRAWL SPLIT: '+url)
		elif url.find('?') > -1:
			url = url.split('?')[0]
			logging.info('TO CRAWL SPLIT: '+url)
		if url.find('https://www.bbvaapimarket.com/') > -1 and url.find('login') == -1:
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
						links = [[NOT_FOUND,NOT_FOUND]]
					elif content == MAIL_TO:
						logging.debug('MAIL_TO: '+url)
						links = [[MAIL_TO,MAIL_TO]]
					elif content == EXCEPTION_GET:
						logging.debug('EXCEPTION_GET: '+url)
						links = [[EXCEPTION_GET,EXCEPTION_GET]]
					else:
						logging.debug('WITH_CONTENT: '+url)
						links = evaluate_content(url, soup)

						crawled[url]=links

						for link in links:
							if link[0].find('#') != 0:
								logging.debug('NEW URLS TO CRAWL - '+link[0])
								resolved_link = resolve_url(url,link[0])
								if resolved_link not in crawled_urls and resolved_link not in to_crawl and resolved_link.find('bbvaapimarket')>-1 and link[1]!=NOT_CRAWL and link[1]!=ERROR_404:
									logging.debug('NEW URLS TO CRAWL - ADDED - '+link[0])
									to_crawl.append(resolved_link)

				else:
					logging.warning('ERROR_404:' +url)
					links = [[ERROR_404,ERROR_404]]
			else:
				logging.info('CRAWLED: '+url)
		else:
			logging.warning('PAGE TO NOT CRAWL: '+url)
		save_loop(TIMESTAMP, count,to_crawl,crawled_urls,crawled)

	print count
	if len(crawled)>0:
		crawled_sorted=  sorted(crawled)
		for url_crawled in crawled_sorted:
			print url_crawled
	to_file(TIMESTAMP, crawled)
	evaluate_crawled(crawled)
	print 'Done crawling'
	logging.info('END CRAWL_WEB PROCESS')

def crawl_web_with_prop(base, base_extended):
	#BASE_URL = base
	#BASE_URL_EXTENDED = base_extended
	crawl_web(base)

def main(argv):
	crawl_web(argv[0])
	#crawl_web('https://www.bbvaapimarket.com/web/api_market/ffa')

if __name__ == "__main__":
    main(sys.argv[1:])