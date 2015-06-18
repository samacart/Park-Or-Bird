import threading
from c_GoogleImageGetter import GoogleImageGetter
import sys

def main():
	t = GatherData()
	t.go()

	try:
		print "joining threads"
		join_threads(t.threads)

	except KeyboardInterrupt: 
		print "\nCaught Interrupt"
		print "Terminate main thread."
		print "If only daemonic threads are left, terminate whole program"

class GatherData(object):

	def __init__(self):
		self.running = True
		self.threads = []

	def get_birds(self):
		while(self.running):
			try:
				print "Get Birds"
				gib = GoogleImageGetter()
				gib.GetBirdsFromFile("shortbirds.txt")
				gib.DownloadBirdImages("./bird_output",4)
			except:
				print sys.exc_info()

	def get_parks(self):
		while(self.running):
			try:
				print "Get Parks"
				gip = GoogleImageGetter()
				gip.GetParksFromFile("shortparks.txt")
				gip.DownloadParkImages("./park_output",4)
			except:
				print sys.exc_info()

	def daemonize(self, t):
		print "daemon"
		t.daemon = True
		t.start()
		self.threads.append(t)

	def go(self):
		print "go"
		t1 = threading.Thread(target=self.get_birds)
		t2 = threading.Thread(target=self.get_parks)
		t3 = threading.Thread(target=self.get_user_input)

		self.daemonize(t1)
		self.daemonize(t2)
		self.daemonize(t3)

		'''
		t1.daemon = True
		t2.daemon = True
		t3.daemon = True

		t1.start()
		t2.start()
		t3.start()

		self.threads.append(t1)
		self.threads.append(t2)
		self.threads.append(t3)
		'''


	def get_user_input(self):
		while True:
			x= raw_input("Enter e for exit: ")
			if x.lower() == 'e':
				self.running = False
				break

def join_threads(threads):

	"""
	Join threads in interruptable fashion.
	From http://stackoverflow.com/a/9790882/145400
	"""

	for t in threads:
		while t.isAlive():
			t.join(5)

if __name__ == "__main__":
	main()
	

