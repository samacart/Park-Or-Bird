import json
import os
import time
import requests
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError

from bs4 import BeautifulSoup

# I was receiving insecure platform warnings, requests should be doing this automatically
# it may be the python version I was testing
# import urllib3.contrib.pyopenssl
# urllib3.contrib.pyopenssl.inject_into_urllib3()

# Credit where credit is due
# https://gist.github.com/crizCraig/2816295 
def GetBirdsList():
	r = requests.get('https://en.wikipedia.org/wiki/List_of_birds_by_common_name')
	


def DownloadImages(query, path):
	
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
# Example use
	DownloadImages('bird', 'bird_downloads')

# Real use, build out a search engine for each common name
# https://en.wikipedia.org/wiki/List_of_birds_by_common_name
