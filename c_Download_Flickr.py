#!/usr/bin/env python
#--------------------------------------------------------
# File Name: insert_flickr.py
# Author: Simon Macarthur
# Date: June 2015
# Version: 0.1 Initial Version
# Purpose: This program uses extracts metadata from the Yahoo 100M photo files
#           transforms it into JSON and stores it in MongoDB
#--------------------------------------------------------

import pymongo
from pymongo import MongoClient
import json
import os
import subprocess

class DownloadFlickr():

    def DownloadFlickrImages(self, search_phrase, db_name, coll_name, hdfs_path):
        try:
	    f = open("Download_Log.txt", "w")

            client = MongoClient('mongodb://10.122.114.74:27017')

            db = getattr(client, db_name)
            collection = getattr(db, coll_name)
            downloads = collection.find({'$and':[{'User_tags':{'$regex': search_phrase}},{'Photo_video':0}]}, timeout=False)
	    for item in downloads:
		subprocess.call("wget -O " + str(item["id"]) + ".jpg" + " " + item["downloadURL"], shell=True) 
		subprocess.call("/usr/local/hadoop/bin/hadoop fs -put " + str(item["id"]) + ".jpg " + hdfs_path, shell=True) 
		subprocess.call("rm "+ str(item["id"]) + ".jpg", shell=True)
		
		f.write( "Downloaded: " + item["downloadURL"] + "\n")

	    f.close()
            return

        except pymongo.errors.ConnectionFailure, e:
           print "Could not connect to MongoDB: %s" % e
	finally:
	    downloads.close()

if __name__ == "__main__":
    f = DownloadFlickr()
    f.DownloadFlickrImages( "bird,", "Photos", "Flickr", "/data/Flickr/Bird")
