import requests # to load web pages
from bs4 import BeautifulSoup # to parse pages
import re # to match partial strings
import csv
import sys
from datetime import datetime


# categories of links that we want to scrape
section_links = [
	'http://www.theverge.com/tech',
	'http://www.theverge.com/science',
	'http://www.theverge.com/culture',
	'http://www.theverge.com/transportation',
	'http://www.theverge.com/design',
	'http://www.theverge.com/business',
	'http://www.theverge.com/us-world',
	'http://www.theverge.com/reviews',
	'http://www.theverge.com/longform',
	'http://www.theverge.com/entertainment',
	'http://www.theverge.com/design',
]

ARTICLE_TEMPLATE = re.compile('http://www.theverge.com/\d{4}/\d{1,2}/\d{1,2}/\d*/[^\']*')

def get_links(text, compiled_regex):
	"""
		harvests text from webpage using compiled_regex.
		@params:
			text : string with html to be parsed
			compiled_regex : compiled regex for the link
	"""
	soup = BeautifulSoup(text)
	# clean out and obtain only the attributes in the links
	cleaned = [ tag.attrs for tag in soup.select('.p-basic-article-list a') ]
	
	selected_links = []
	for obj in cleaned:
		try:
			match = compiled_regex.match(obj['href'])
			if match:
				# we obtained a match, append it to the article links
				selected_links.append(match.group())
		except KeyError as e:
			# skip this round because cleaned object does not have an href tag
			pass
	# make them unique by passing into set object.
	return set(selected_links)




global_links = set()
to_be_saved = []


if len(sys.argv) == 3:
	start_page = int(sys.argv[1])
	end_page = int(sys.argv[2])
else:
	start_page = 1
	end_page = 100

for i in range(start_page, end_page):
	for section_link in section_links:
		section_name = section_link.split('/')[-1]
		r = requests.get(section_link+'/archives/' + str(i) ) #append archives to search archives only

		links_in_section = get_links(r.text, ARTICLE_TEMPLATE)

		# filter links in section here?
		
		for link in links_in_section:
			if not link in global_links:
				to_be_saved.append( (link, section_name) )
				global_links.add(link)

				if len(to_be_saved) == 1000:
					# Many links! Save now...
					now_time = str(datetime.now())
					now_time = now_time.replace(':','_').replace('.','_').replace(' ', '__')

					with open('verge_links' + now_time + '.csv', 'w') as f:
						writer = csv.writer(f)
						for row in to_be_saved:
							writer.writerow(row)
						print 'saved ' + now_time
					to_be_saved = [] # flush to be saved


now_time = str(datetime.now())
now_time = now_time.replace(':','_').replace('.','_').replace(' ', '__')

with open('verge_links' + now_time + '.csv', 'w') as f:
	writer = csv.writer(f)
	for row in to_be_saved:
		writer.writerow(row)
	print 'saved ' + now_time

print 'completed scrape of sections'
