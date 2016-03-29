import urllib
from bs4 import BeautifulSoup
import json
from time import localtime, strftime

NOT_FOUND = 'NotFound'

def to_file(crawled):
	timestamp = strftime("%Y%m%d%H%M%S", localtime())
	print timestamp
	#print json.dumps(crawled)
	filename = timestamp + '_crawl.json'
	with open(filename, 'w') as outfile:
		json.dump(crawled, outfile, indent=2)

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
		return NOT_FOUND

def evaluate_content(content):
	result = ['error404']

	soup = BeautifulSoup(content, 'html.parser')

	if len(soup.find_all("section", class_="error404")) == 0:
		result = get_unique_links(soup)

	return result

def crawl_web(seed):
	print 'Crawling '+seed
	
	to_crawl = [seed]
	crawled = {}

	while len(to_crawl)>0:
		url = to_crawl.pop()
		if url not in crawled:
			content = get_url_content(url)
			if content == NOT_FOUND:
				links = [content]
			else:
				links = evaluate_content(content)
			crawled[url]=links
		else:
			print 'URL: '+url+ ' || Already done'

	to_file(crawled)
	print 'Done crawling'


def main():
	crawl_web("http://www.bbvaapimarket.com/")
	#crawl_web('https://www.bbvaapimarket.com/web/api_market/ffa')

if __name__ == "__main__":
    main()