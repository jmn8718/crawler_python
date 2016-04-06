import json
import logging
import os
import csv
from slackclient import SlackClient
#logging.basicConfig(filename='./logs/io.log',format='%(asctime)s : %(levelname)s:  %(message)s',  datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

SLACK_TOKEN = 'xoxp-15941309378-15942199969-21442107746-ca689d55a4'
SLACK_CHANNEL = 'crawler_errors'
SLACK_USERNAME = 'THE CRAWLER'
SLACK_EMOJI = ':loudspeaker:'

def sendSlack(message):
	try:
		formatedMessage = '\n----------------------------------\n'
		formatedMessage += message
		sc = SlackClient(SLACK_TOKEN)
		result_bot = sc.api_call(
		    "chat.postMessage", channel=SLACK_CHANNEL, text=formatedMessage,
		    username=SLACK_USERNAME, icon_emoji=SLACK_EMOJI
		)
		if(result_bot['ok']==True):
			print('Slack ok')
		else:
			raise Exception('Error in slack '+str(result_bot))
	except:
		print("Unexpected error in sendSlack:" + str(sys.exc_info()))

def evaluate(crawled, stringCondition):
	result = []
	try:
		logging.debug('EVALUATING ---------------- ' + stringCondition)
		for page in crawled:
			for link in  crawled[page]:
				if link[1] == stringCondition:
					logging.debug(page + ' : ' + link[0] + ' --- ' +link[1])
					print page + ' : ' + link[0] + ' --- ' +link[1]
					links = []
					links.append(page)
					links.append(link[0])
					links.append(link[1])
					result.append(links)
	except Exception as e:
		logging.error('EVALUATING ---------------- ' + stringCondition)
		logging.error(e)
		print 'ERROR IN evaluate '+ stringCondition
		print e	
	return	result

def evaluate_crawled(timestamp, crawled):
	logging.info('evaluate_crawled - start ')

	keywords = []
	#keywords.append('Anchor' )
	keywords.append('exceptionGET' )
	keywords.append('NotFound' )
	keywords.append('error404' )
	#keywords.append('NoTitle' )
	#keywords.append('NotCrawl' )
	errors = []
	for keyword in keywords:
		errors += evaluate(crawled, keyword)

	logging.info('evaluate_crawled - end ')
	if len(errors) > 0 :
		slack_message = 'CRAWLER EXECUTION TIMESTAMP : '+ TIMESTAMP + '\n'
		sendSlack(slack_message)
	for error in errors:
		slack_message = 'URL:' + error[0] + '\n'
		slack_message += 'LINK: ' + error[1] + '\n'
		slack_message += 'ERROR: ' + error[2]
		sendSlack(slack_message)
	return errors

def to_csv(timestamp, crawled):
	logging.info('to_csv - start ')
	filename = 'data/'+timestamp + '_crawl.csv'
	logging.info('to_csv - writing -  '+filename)
	fieldnames = ['page','link','title']
	errors = evaluate_crawled(crawled)
	try:
		with open(filename, 'w') as csvfile:
			row_writer = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			row_writer.writerow([field for field in fieldnames])
			for row in errors:
				print row
				row_writer.writerow([field for field in row])
				#for link in content:
					#link[0]
					#row = [page, link[0], link[1]]
					#row_writer.writerow([field for field in row])
	except Exception as e:
		print 'ERROR IN to_csv'
		print e
	logging.info('to_csv - end')

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

def test_to_csv(timestamp):
	try:
		filename = 'data/'+timestamp+'_crawl.json'
		crawled = json.loads(open(filename).read())
		#print json.dumps(crawled, indent=2)
		#to_csv(timestamp.split('_')[0],json.dumps(crawled, indent=2))
		#to_csv(timestamp, crawled)
		evaluate_crawled(crawled)
	except Exception as e:
		print 'ERROR IN test_to_csv'
		print e

if __name__ == "__main__":
    import sys
    test_to_csv(sys.argv[1])