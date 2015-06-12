import json
import os
import time
import requests
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup

class GoogleImageGetter():

	def __init__(self):
		self._birds = []
		self._parks = []

	def GetBirds(self):
		self._birds = self.GetBirdsList()

	def GetParks(self):
		self._parks = self.GetNationalParkList()

	def Print(self, var, arg):

		printList = self._birds if var.lower() == "birds" else self._parks

		if arg.lower() == "names":
			print "Current Names:\n" + ', '.join(printList)

		if arg.lower() == "count":
			print "Current Count: {}".format(len(printList))

	def HaveBird(self, testBird):
		return testBird.lower() in [b.lower for b in self._birds]

	def GetBirdsList(self):

		# flag is needed based on the page structure
		# birds start after the External_links reference
		flag = False

		r = requests.get('https://en.wikipedia.org/wiki/List_of_birds_by_common_name')
		soup = BeautifulSoup(r.content)
		birdnames = []
		for link in soup.find_all('a'):
			t = link.text.encode('utf-8')
			if flag:
				if t and t != "edit":
					birdnames.append(t)
			try:
				if link['href'] == "#External_links":
					flag = True
			except:
				pass


		return birdnames

	def GetNationalParkList(self):

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

	gi = GoogleImageGetter()
	gi.GetBirds()
	gi.Print("birds","count")
	print gi.HaveBird('Ovenbird')


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

