import urllib
from bs4 import BeautifulSoup

def print_links(html):
	links = []
	for link in html.find_all('a'):
		links.append(link.get('href'))
    	#print(link.get('href'))
	print len(links)


def print_unique_links(html):
	links = []
	for link in html.find_all('a'):
		href = link.get('href')
		if href not in links:
			links.append(href)
	    	#print(link.get('href'))
	print len(links)




def crawl_web(url):
	print 'Crawling '+url
	page = urllib.urlopen(url).read()

	soup = BeautifulSoup(page, 'html.parser')

	if len(soup.find_all("section", class_="error404")) == 0 :
		print 'Page with content'
		print_links(soup)
		print_unique_links(soup)
	else:
		print 'ERROR 404'
	print 'Done crawling'

crawl_web("http://www.bbvaapimarket.com/")
crawl_web('https://www.bbvaapimarket.com/web/api_market/ffa')