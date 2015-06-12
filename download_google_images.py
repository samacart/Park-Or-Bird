import json
import os
import time
import requests
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError

from bs4 import BeautifulSoup

def GetBirdsList():
	# Generates a list of birds for searching in a text file
	# not the cleanest output, titles and references links will still be present
	# delete the first 136 lines of the output file for clean text

	r = requests.get('https://en.wikipedia.org/wiki/List_of_birds_by_common_name')
	soup = BeautifulSoup(r.content)
	birdnames = []
	for link in soup.find_all('a'):
		t = link.text.encode('utf-8')
		if t and t != "edit":
			birdnames.append(t)

	return birdnames

def GetNationalParkList():

	r = requests.get('https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States')
	soup = BeautifulSoup(r.content)
	parknames = []
	for th in soup.find_all('th',{'scope':'row'}):
		for link in th.find_all('a'):
			t = link.text.encode('utf-8')
			if t and t != "edit":
				parknames.append(t)

	return parknames

def DownloadImages(query, path):
	# Credit where credit is due
	# https://gist.github.com/crizCraig/2816295 
	
	BASE_URL = 'https://ajax.googleapis.com/ajax/services/search/images?'\
				'v=1.0&q=' + query + '&start=%d'
 
	BASE_PATH = os.path.join(path, query)
 
	if not os.path.exists(BASE_PATH):
		os.makedirs(BASE_PATH)
 
	start = 0 # Google's start query string parameter for pagination.
	while start < 60: # Google will only return a max of 56 results.
		r = requests.get(BASE_URL % start)
		for image_info in json.loads(r.text)['responseData']['results']:
			url = image_info['unescapedUrl']
			try:
				image_r = requests.get(url)
			except ConnectionError, e:
				print 'could not download %s' % url
				continue
 
		# Remove file-system path characters from name.
		title = image_info['titleNoFormatting'].replace('/', '').replace('\\', '')
	 
		file = open(os.path.join(BASE_PATH, '%s.jpg') % title, 'w')
		try:
			Image.open(StringIO(image_r.content)).save(file, 'JPEG')
		except IOError, e:
			print 'could not save %s' % url
			continue
		finally:
			file.close()
 
		print start
		start += 4 # 4 images per page.
 
		# Be nice to Google and they'll be nice back :)
		time.sleep(1.5)
 
if __name__ == "__main__":
#	DownloadImages('bird', 'bird_downloads')

#	Only have to run this once to generate the parks list
#	parks = GetNationalParkList()
#	with open("parks.txt", "wb") as outfile: 
#		for p in parks: 
#			outfile.write(p+"\n")

#	Only have to run this once to generate the birds list
#	birds = GetBirdsList()
#	with open("birds.txt","wb") as outfile:
#		for b in birds:
#			outfile.write(b+"\n")

