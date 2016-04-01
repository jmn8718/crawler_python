import json
import logging
import os

#logging.basicConfig(filename='./logs/io.log',format='%(asctime)s : %(levelname)s:  %(message)s',  datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)


def to_file(timestamp, crawled):
	logging.info('to_file - start ')
	print timestamp
	#print json.dumps(crawled)
	filename = 'data/'+timestamp + '_crawl.json'
	logging.info('to_file - writing -  '+filename)
	with open(filename, 'w') as outfile:
		json.dump(crawled, outfile, indent=2)
	logging.info('to_file - end')

def save_loop(timestamp, loop_number,to_crawl,crawled_urls,crawled):
	logging.info('save loop - start ')	
	try:
		directory = 'data_loop/'+timestamp
		if not os.path.exists(directory):
			os.makedirs(directory)

		filenameToCrawl = directory + '/{:04d}'.format(loop_number) + '_toCrawl.txt'
		with open(filenameToCrawl, 'w') as outfileToCrawl:
			for urlToCrawl in to_crawl:
				outfileToCrawl.write(urlToCrawl + '\n')

		filenameCrawledUrls = directory + '/{:04d}'.format(loop_number) + '_crawledUrls.txt'
		with open(filenameCrawledUrls, 'w') as outfileCrawled:
			for urlCrawled in crawled_urls:
				outfileCrawled.write(urlCrawled + '\n')

		filenameCrawled = directory + '/{:04d}'.format(loop_number) + '_crawled.json'
		with open(filenameCrawled, 'w') as outfile:
			json.dump(crawled, outfile, indent=2)
		
		logging.info('save loop - end ')	

	except Exception as e:
		print 'LOOP WRITE OUTPUT ERROR - '
		print e
		logging.error('LOOP WRITE OUTPUT ERROR '+ e)



if __name__ == "__main__":
    import sys
    fib(int(sys.argv[1]))