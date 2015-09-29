import requests # to load web pages
from bs4 import BeautifulSoup # to parse pages
import re # to match partial strings
import csv # json to parse json
from datetime import datetime
import sys
import json
import glob
from collections import namedtuple
import numpy as np
import codecs
from tools import extract_sentiment_from_text
import requests
""" 
Code from code from https://impythonist.wordpress.com/2015/01/06/ultimate-guide-for-scraping-javascript-rendered-web-pages/
the reason for this extra code is because the verge social media sharing counts are loaded via javascript (ajax calls)
after the page loads.
"""

import sys

		
import sexmachine.detector as gender
gender_detector = gender.Detector(case_sensitive=False)



features = [
	'url',
	'title_text',
	'title_number_of_words',
	'title_average_word_lengths',
	'probability_title_sentiment_positive',
	'probability_title_sentiment_negative',
	'probability_title_sentiment_neutral',
	'author',
	'is_andy',
	'is_male',
	'is_female',
	'time_string',
	'is_weekday',
	'is_weekend',
	'is_morning',
	'is_afternoon',
	'is_night',
	'meta_description',
	'probability_meta_sentiment_positive',
	'probability_meta_sentiment_negative',
	'probability_meta_sentiment_neutral',
	'twitter_shares',
	'linkedin_shares',
	'facebook_shares',
	'facebook_comments',
	'facebook_likes',
	'facebook_click_count',
	'facebook_total_engagement',
	'article_text',
	'probability_article_sentiment_positive',
	'probability_article_sentiment_negative',
	'probability_article_sentiment_neutral',
	'article_number_of_words',
	'article_average_word_lengths',
	'article_number_of_unique_words',
	'article_average_unique_word_lengths',
	'number_of_videos',
	'number_of_images',
	'labels',
	'is_tech',
	'is_science',
	'is_culture',
	'is_transportation',
	'is_business',
	'is_us_world',
	'is_reviews',
	'is_longform',
	'is_entertainment',
	'is_design'
]

Datum = namedtuple('Datum', ' '.join(features) )

# converts QtString to python.string
# qt_to_string = lambda qtstring: str(qtstring.frame.toHtml().toAscii())

def extract_features(url, section_name):
	try:
		response = requests.get(url)
	except Exception as e:
		print 'Could not load response module:'+str(e)
		return False
	if not response.ok:
		return False

	HTML = response.content
	soup = BeautifulSoup(HTML)

	extracted_features = {
		'is_tech':0,
		'is_science':0,
		'is_culture':0,
		'is_transportation':0,
		'is_design':0,
		'is_business':0,
		'is_us_world':0,
		'is_reviews':0,
		'is_longform':0,
		'is_entertainment':0,
		'is_design':0
	}

	extracted_features['url'] = url
	if section_name == 'us-world':
		section_name = 'us_world'
	
	extracted_features['is_'+str(section_name)] = 1 

	try:
		# select the title, and select the contents, replace white spaces and newline characters
		extracted_features['title_text'] = soup.find_all('meta', attrs={'name':'twitter:title'})[0]['content'].encode('utf-8')
	except Exception as e:
		print 'Exception Occured During Title Extraction: '+str(e)
		extracted_features['title_text'] = 'TITLE EXTRACTION FAILED'

	try:
		if extracted_features['title_text'] == 'TITLE EXTRACTION FAILED':
			raise Exception('No Title')

		title_words = extracted_features['title_text'].split(' ') # get word list
		extracted_features['title_number_of_words'] = len(title_words) # get number of words
		title_word_lengths = [ len(word) for word in title_words ] # get word lengths to calculate average
		extracted_features['title_average_word_lengths'] = np.mean(title_word_lengths) # average word lengths in the introduction

		if len(extracted_features['title_text'])< 80000:
			try:
				negative,positive,neutral = extract_sentiment_from_text(extracted_features['title_text'])
				extracted_features['probability_title_sentiment_negative'] = negative
				extracted_features['probability_title_sentiment_positive'] = positive
				extracted_features['probability_title_sentiment_neutral'] = neutral
			except Exception as e:
				extracted_features['probability_title_sentiment_negative'] = -1
				extracted_features['probability_title_sentiment_positive'] = -1
				extracted_features['probability_title_sentiment_neutral'] = -1
				print 'Exception Occured During ARTICLE SENTIMENT Extraction'+str(e)
		else:
			extracted_features['probability_title_sentiment_negative'] = -1
			extracted_features['probability_title_sentiment_positive'] = -1
			extracted_features['probability_title_sentiment_neutral'] = -1


	except Exception as e:
		print 'Exception Occured During Title Feature Calculation'+str(e)
		extracted_features['title_number_of_words'] = -1
		extracted_features['title_average_word_lengths'] = -1
		extracted_features['probability_title_sentiment_negative'] = -1
		extracted_features['probability_title_sentiment_positive'] = -1
		extracted_features['probability_title_sentiment_neutral'] = -1



	# name of the author
	try:
		extracted_features['author'] = str(soup.select('a.author')[0].contents[0]).encode('utf-8')

		decided = gender_detector.get_gender(extracted_features['author'].split(' ')[0])

		extracted_features['is_male'] = 0
		extracted_features['is_female'] = 0
		extracted_features['is_andy'] = 0

		if decided == 'male' or decided == 'mostly_male':
			extracted_features['is_male'] = 1
		elif decided=='female' or decided =='mostly_female':
			extracted_features['is_female'] = 1
		else:
			extracted_features['is_andy'] = 1

		
	except Exception as e:
		print 'Exception Occured During Author Extraction'+str(e)
		extracted_features['author'] = 'NOONE'
		extracted_features['is_andy'] = 0
		extracted_features['is_male'] = 0
		extracted_features['is_female'] = 0



	# find the time that the article was published

	try:
		time_string = str(soup.select('time')[0].contents[0])
		extracted_features['time_string'] = time_string

		dt = datetime.strptime(time_string, '%B %d, %Y %I:%M %p')
		extracted_features['is_weekday'] = int(dt.isoweekday() < 6)
		extracted_features['is_weekend'] = 1-extracted_features['is_weekday']
		extracted_features['is_morning'] = int(dt.hour < 12)
		extracted_features['is_afternoon'] = int(12 <= dt.hour <= 18)
		extracted_features['is_night'] = int(dt.hour > 18)

	except Exception as e:
		print 'Exception Occured During TIME STRING Extraction'+str(e)
		extracted_features['time_string'] = '000'
		extracted_features['is_weekday'] = -1
		extracted_features['is_weekend'] = -1
		extracted_features['is_morning'] = -1
		extracted_features['is_afternoon'] =  -1
		extracted_features['is_night'] = -1

	# the verge displays 4 social counts:
	# (0) Facebook
	# (1) Twitter
	# (2) LinkedIn
	# (3) Pinterest

	# social_counts = [ element.contents for element in soup.select('.p-button__count')]

	# extracted_features['fb_shares'] = -1
	# extracted_features['twitter_shares'] = -1
	# extracted_features['linkedin_shares'] = -1
	# extracted_features['pinterest_shares'] = -1

	# for index,count in enumerate(social_counts):
	# 	try:
	# 		pre_parsed = count[0].replace('(','').replace(')','').replace(',','').replace('k', '000').replace('m', '000000').replace('M','000000')
	# 		social_counts[index] = int(pre_parsed)
	# 	except IndexError as e:
	# 		print 'EERROr occured during social shares extraction, certain social network didnt exist'+str(e)
	# 		social_counts[index] = 0
	
	# try:
	# 	extracted_features['fb_shares'] = social_counts[0]
	# 	extracted_features['twitter_shares'] = social_counts[1]
	# 	extracted_features['linkedin_shares'] = social_counts[2]
	# 	extracted_features['pinterest_shares'] = social_counts[3]
	# except IndexError as e:
	# 	print 'EERROr occured during social shares extraction'+str(e)
	# 	extracted_features['fb_shares'] = -1
	# 	extracted_features['twitter_shares'] = -1
	# 	extracted_features['linkedin_shares'] = -1
	# 	extracted_features['pinterest_shares'] = -1

	try:
		extracted_features['twitter_shares'] = json.loads(requests.get('http://urls.api.twitter.com/1/urls/count.json?url='+url).content)['count']
	except Exception as e:
		print 'Failed to get twitter information'+str(e)
		extracted_features['twitter_shares'] = -1

	try:
		extracted_features['linkedin_shares'] = json.loads(requests.get('https://www.linkedin.com/countserv/count/share?url='+url+'&format=json').content)['count']
	except Exception as e:
		print 'Failed to get linkedin information'+str(e)
		extracted_features['linkedin_shares'] = -1

	try:
		facebook_engagement_information = json.loads(requests.get('https://api.facebook.com/method/links.getStats?urls='+url+'&format=json').content)[0]

		extracted_features['facebook_shares'] = facebook_engagement_information['share_count']
		extracted_features['facebook_comments'] = facebook_engagement_information['comment_count']
		extracted_features['facebook_likes'] = facebook_engagement_information['like_count']
		extracted_features['facebook_click_count'] = facebook_engagement_information['click_count']
		extracted_features['facebook_total_engagement'] = facebook_engagement_information['total_count']
	except Exception as e:
		print 'Failed to get facebook information '+str(e)
		extracted_features['facebook_shares'] = -1
		extracted_features['facebook_comments'] = -1
		extracted_features['facebook_likes'] = -1
		extracted_features['facebook_click_count'] = -1
		extracted_features['facebook_total_engagement'] = -1


	try:
		extracted_features['meta_description'] = soup.find_all('meta', attrs={'name':'description'})[0]['content'].replace('\n',' ').replace('\r', '').encode('utf-8')
		try:
			negative,positive,neutral = extract_sentiment_from_text(extracted_features['meta_description'])
			extracted_features['probability_meta_sentiment_negative'] = negative
			extracted_features['probability_meta_sentiment_positive'] = positive
			extracted_features['probability_meta_sentiment_neutral'] = neutral
		except Exception as e:
			extracted_features['probability_meta_sentiment_negative'] = -1
			extracted_features['probability_meta_sentiment_positive'] = -1
			extracted_features['probability_meta_sentiment_neutral'] = -1
			print 'Exception Occured During meta SENTIMENT Extraction'+str(e)
	except Exception as e:
		print 'Exception Occured during DESCRIPTION Extraction'+str(e)
		extracted_features['meta_description'] = ''


	try:
		# extracts the actual article text
		extracted_features['article_text'] = " ".join( [ paragraph.text for paragraph in soup.select('article p') if paragraph.attrs.get('class', [ False ])[0] == False] ).encode('utf-8').replace('\n', '').replace('\xc2\xa0', ' ').replace('\r', '')
		extracted_features['article_text'] = re.sub("<!--.*?-->", "", extracted_features['article_text'])
		extracted_features['article_text'] = re.sub("<!--", "", extracted_features['article_text'])
		extracted_features['article_text'] = re.sub("-->", "", extracted_features['article_text'])
		# if extracted_features['article_text'] == '':
			# extracted_features['article_text'] =" \n".join( [ paragraph.text for paragraph in soup.select('.m-article__entry p') if paragraph.attrs.get('class', [ False ])[0] == False] )
		
		# simple counting:
		article_words = extracted_features['article_text'].split(' ') # get word list
		extracted_features['article_number_of_words'] = len(article_words) # get number of words
		article_word_lengths = [ len(word) for word in article_words ] # get word lengths to calculate average
		extracted_features['article_average_word_lengths'] = np.mean(article_word_lengths) # average word lengths in the article

		article_unique_words = set(article_words)
		extracted_features['article_number_of_unique_words'] = len(article_unique_words)
		article_unique_word_lengths = [ len(word) for word in article_unique_words ] # get word lengths to calculate average
		extracted_features['article_average_unique_word_lengths'] = np.mean(article_unique_word_lengths) # average word lengths in the introduction

		if len(extracted_features['article_text']) < 80000:
			try:
				negative,positive,neutral = extract_sentiment_from_text(extracted_features['article_text'])
				extracted_features['probability_article_sentiment_negative'] = negative
				extracted_features['probability_article_sentiment_positive'] = positive
				extracted_features['probability_article_sentiment_neutral'] = neutral
			except Exception as e:
				extracted_features['probability_article_sentiment_negative'] = -1
				extracted_features['probability_article_sentiment_positive'] = -1
				extracted_features['probability_article_sentiment_neutral'] = -1
				print 'Exception Occured During ARTICLE SENTIMENT Extraction'+str(e)
		else:
			extracted_features['probability_article_sentiment_negative'] = -1
			extracted_features['probability_article_sentiment_positive'] = -1
			extracted_features['probability_article_sentiment_neutral'] = -1

	except Exception as e:
		print 'Exception Occured During ARTICLE Extraction'+str(e)
		extracted_features['article_text']  = 'FAILED'
		extracted_features['article_number_of_words'] = 0
		extracted_features['article_number_of_unique_words'] = 0
		extracted_features['article_average_word_lengths'] = 0
		extracted_features['article_average_unique_word_lengths'] = 0
		extracted_features['probability_article_sentiment_negative'] = -1
		extracted_features['probability_article_sentiment_positive'] = -1
		extracted_features['probability_article_sentiment_neutral'] = -1

	try:
		extracted_features['number_of_videos'] = len(soup.select('.video-wrap')) + len(soup.select('video'))
	except Exception as e:
		extracted_features['number_of_videos'] = 0
		print 'Exception Occured During VIDEO Extraction'+str(e)

	try:
		extracted_features['number_of_images'] = len(soup.select('.m-feature__body img')) + len(soup.select('.e-image img')) 
	except Exception as e:
		print 'Exception Occured During IMG Extraction'+str(e)
		extracted_features['number_of_images'] = 0


	# select all links within the labels holder, explore the contents of those links
	# those are our labels
	try:
		extracted_features['labels'] = ', '.join( [ str(tag.select('a')[0].contents[0]) for tag in soup.select('.p-entry-header__labels')[0].select('li') ] ).encode('utf-8')
	except Exception as e:
		print 'Exception Occured During LABEL extraction'+str(e)
		extracted_features['labels'] = ''

	return Datum(**extracted_features)



def create_writer(file_name, count):
	writer = csv.writer(open(out_name+'_'+str(count)+'.csv', 'w'))
	writer.writerow(features)
	return writer


if __name__ == '__main__':


	if len(sys.argv) > 1:
		directory = sys.argv[1]
	else:
		directory = './'

	files = glob.glob(directory+'*.csv')

	test_pages_to_crawl = [
		('http://www.theverge.com/2015/4/27/8505531/best-buy-begins-accepting-apple-pay', 'technology'),
		('http://www.theverge.com/2015/4/27/8503599/samsung-galaxy-s6-case-romero-britto-so-fancy', 'technology'),
		('http://www.theverge.com/2015/4/27/8504579/nbc-sports-live-extra-app-apple-tv-now-available', 'technology'),
		('http://www.theverge.com/2015/9/21/9364597/review-minority-report-fox-tv-series', 'entertainment')
	]

	pages_to_crawl = []


	for csv_file in files:
		with open(csv_file, 'r') as f:
			reader = csv.reader(f)
			for row in reader:
				pages_to_crawl.append((row[0], row[1]))
			#endfor
		#endwith
	#endcsv_file

	# pages_to_crawl = test_pages_to_crawl

	print 'There are '+str(len(pages_to_crawl))+' pages to crawl.'

	now_time = str(datetime.now())
	now_time = now_time.replace(':','_').replace('.','_').replace(' ', '__')
	
	out_name = directory+'content_extracted_'+now_time


	file_count = 0
	articles_count = 0

	writer = create_writer(out_name, file_count)
	
	for page_information in pages_to_crawl:
		page, section = page_information
		extracted_features = extract_features(page, section)

		if type(extracted_features) is bool and not extracted_features:
			print str(articles_count)+' articles extracted, SKIPPED: '+page
			continue

		print str(articles_count)+' articles extracted, '+page
		writer.writerow(list(extracted_features))
		articles_count += 1

		if articles_count % 1000 == 0:
			file_count += 1
			writer = create_writer(out_name, file_count )

