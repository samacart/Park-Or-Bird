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
import multiprocessing

class InsertFlickr():

    def InsertFlickrData(self, sourcefile, db_name, coll_name):
        try:
            client = MongoClient()

            print db_name
            print coll_name

            db = getattr(client, db_name)
            collection = getattr(db, coll_name)
 
            with open(sourcefile,'rb') as source:
                for line in source:
                    fields = line.split('\t')
                    d["id"] = fields[0]
                    d["user_id"] = fields[1]
                    d["user_nick"] = urllib.unquote(fields[2]).decode('utf-8')
                    d["date_taken"] = fields[3]
                    d["date_uploaded"] = fields[4]
                    d["capture_device"] = fields[5]
                    d["title"] = fields[6].replace("+", " ")
                    d["desc"] = fields[7]
                    d["user_tags"] = urllib.unquote(fields[8]).decode('utf8')
                    d["machine_tags"] = fields[9]
                    d["long"] = fields[10]
                    d["lat"] = fields[11]
                    d["accuracy"] = fields[12]
                    d["page_url"] = fields[13]
                    d["download_url"] = fields[14]
                    if fields[22].replace("\n","") == "0":
                        type = "photo"
                    else:
                        type = "video"
                    d["type"] = type
                    d["source_file"] = sourcefile

                # Only insert if this document doesn't exist
                existing_document = collection.find_one({"id":d["id"]})
                if not existing_document:
                    id = collection.insert(d)
                    print "Inserted id %s into MongoDB." %id

            return

        except pymongo.errors.ConnectionFailure, e:
           print "Could not connect to MongoDB: %s" % e

if __name__ == "__main__":
    f = InsertFlickr()
    f.InsertFlickrData( "Flickr/yfcc100m_dataset-0", "Photo_Meta", "Flickr")
