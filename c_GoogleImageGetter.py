import json
import os
import time
import sys
import requests
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
from pymongo import MongoClient

class GoogleImageGetter():

	def __init__(self):
		self._birds = []
		self._parks = []

		# initialize mongo client settings
		self._MC = MongoClient()
		self._db = self._MC.db_GoogleDownloads
		self._collection = self._db.Images

	def GetBirdsFromWiki(self):
		self._birds = self.GetBirdsList()

	def GetParksFromWiki(self):
		self._parks = self.GetNationalParkList()

	def GetBirdsFromFile(self, birdFile):
		with open(birdFile, 'rb') as f:
			self._birds = f.read().splitlines()

	def GetParksFromFile(self, parkFile):
		with open(parkFile, 'rb') as f:
			self._parks = f.read().splitlines()

	def AddBird(self, bird):
		self._birds.append(bird)

	def AddPark(self, park):
		self._parks.append(park)

	def Print(self, var, arg):

		printList = self._birds if var.lower() == "birds" else self._parks

		if arg.lower() == "names":
			print "Current Names:\n" + ', '.join(printList)

		if arg.lower() == "count":
			print "Current Count: {}".format(len(printList))

	def HaveBird(self, testBird):
		return testBird.lower() in [b.lower() for b in self._birds]

	def HavePark(self, testPark):
		return testPark.lower() in [p.lower() for p in self._parks]

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
					#set the flag to start collecting birds
					flag = True
				if link.text.encode('utf-8') == "Painted bunting":
					#currently last bird in the list, set the flag to stop collection
					flag = False

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

	def DownloadParkImages(self, path, maxresults=60):
		for p in self._parks:
			print "Downloading images for {}, max results = {}".format(p, maxresults)
			try:
				#self.DownloadImages("park", p, path, maxresults)
				self.GetImageData("park", p, path, maxresults)
			except:
				print sys.exc_info()
				pass		

	def DownloadBirdImages(self, path, maxresults=60):
		for b in self._birds:
			print "Downloading images for {}, max results = {}".format(b, maxresults)
			try:
				#self.DownloadImages("bird", b, path, maxresults)
				self.GetImageData("bird", b, path, maxresults)
			except:
				print sys.exc_info()
				pass

	def GetImageData(self, category, query, path, maxresults):
		
		BASE_URL = 'https://ajax.googleapis.com/ajax/services/search/images?'\
					'v=1.0&q=' + query + '&start=%d'

		start = 0
		while start < maxresults:
			try:
				r = requests.get(BASE_URL % start)
				for image_info in json.loads(r.text)['responseData']['results']:
					try:
						j = {}
						j['category'] = category
						j['query'] = query
						j['image_info'] = image_info
						js = json.loads(json.dumps(j))
						self._collection.insert(js)
					except:
						print "Insertion error"
						print sys.exc_info()
						pass
		
			except:
				print "Bad request: {}".format(BASE_URL)
				print sys.exc_info()
				pass

			start += 4
			time.sleep(1.5)
				

	def DownloadImages(self, category, query, path, maxresults):
		# Credit where credit is due
		# https://gist.github.com/crizCraig/2816295 
		
		BASE_URL = 'https://ajax.googleapis.com/ajax/services/search/images?'\
					'v=1.0&q=' + query + '&start=%d'
	 
		#BASE_PATH = os.path.join(path, query)
		BASE_PATH = path
	 
		if not os.path.exists(BASE_PATH):
			os.makedirs(BASE_PATH)
	 
		start = 0 # Google's start query string parameter for pagination.
		while start < maxresults: # Google will only return a max of 56 results.
			r = requests.get(BASE_URL % start)
			for image_info in json.loads(r.text)['responseData']['results']:
				url = image_info['unescapedUrl']
				try:
					image_r = requests.get(url)
				except ConnectionError, e:
					print 'could not download %s' % url
					continue
	 
			# Remove file-system path characters from name.
			title_base = image_info['titleNoFormatting'].replace('/', '').replace('\\', '')
			title = query + "-" + str(start) + "-" + title_base		 

			file = open(os.path.join(BASE_PATH, '%s.jpg') % title, 'w')
			try:
				Image.open(StringIO(image_r.content)).save(file, 'JPEG')
				
				j = {}
				j['category'] = category
				j['query'] = query
				j['url'] = BASE_URL
				j['base path'] = BASE_PATH
				j['base title'] = title_base
				j['title'] = title
		
				js = json.loads(json.dumps(j))
				self._collection.insert(js)
		
			except IOError, e:
				print 'could not save %s' % url
				continue
			finally:
				file.close()
	 
			start += 4 # 4 images per page.
	 
			# Be nice to Google and they'll be nice back :)
			time.sleep(1.5)
 
if __name__ == "__main__":

	gi = GoogleImageGetter()
	gi.GetBirdsFromFile("shortbirds.txt")
	#gi.GetBirdsFromWiki()
	gi.Print("birds","count")
	gi.DownloadBirdImages("./bird_output",2)
	#gi.DownloadBirdImages("./bird_output",16)
	#print gi.HaveBird("Ovenbird")

	#gi.GetParksFromWiki()
	#gi.GetParksFromFile("shortparks.txt")
	#gi.Print("parks","count")
	#print gi.HavePark("Yosemite")

	#gi.AddPark("Prospect Park")
	#gi.AddPark("Central Park")
	#gi.Print("parks","names")
	#gi.DownloadParkImages("./park_output", 16)


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

