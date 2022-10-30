from botSystem import BUILD_TYPE
from typing import Collection, Dict
import pymongo
from pymongo import MongoClient
from pymongo import collection
import bson
from bson import DBRef

import pprint
import sys

userdata = {"name": 'Andrew',
	"account": 'somestring_new111',
	"id": 0}

s1 = {"scoreType": 'one',
	"kill_1": 101,
	"kill_2": 1001}

#db = MongoClient('192.168.1.18', 27017)
#client = MongoClient('mongodb://192.168.1.18:27017/')
client = MongoClient(host='192.168.1.18',
		port=27017,
		username='dbuser',
		password='dbuser123',
		authSource='admin')



class Mongodb:

	def __init__(self):
		self.client = MongoClient(host='192.168.1.18',
			port=27017,
			username='dbuser',
			password='dbuser123',
			authSource='admin')

		if "pytest" in sys.modules or (BUILD_TYPE == BUILD_TYPE.UNIT_TESTING):
			DATABASE_NAME = 'discord_rs_bot_test'
		else:
			DATABASE_NAME = 'discord_rs_bot'
			
		self.db = self.client[DATABASE_NAME]

	# def __del__(self):
	# 	self.db.client.close()

	def setCollection(self, collectionIdStr : str):
		self.collection = self.db[collectionIdStr]
		return self.collection

	def updateOne(self, collection : str, searchKey : Dict, record : Dict):
		col = self.db[collection]
		updateRec = col.update_one(searchKey, {'$set': record}, upsert=True)
		return (updateRec)

	def findRecord(self, collection :str, searchKey : Dict):
		col = self.db[collection]
		return col.find_one(searchKey)

	def close(self):
		self.client.close()

if __name__ == '__main__':

	db1 = Mongodb()

	print('running something')
	
	#db = client[DATABASE_NAME]
	#accounts = db['Account']
	# scores = db['Scores']
	#
	# count = scores.update_one({"scoreType": 'one'}, {'$set': s1}, upsert=True)
	# rec = scores.find_one({"scoreType": 'one'})
	# id = rec['_id']
	# dbref = DBRef('scores',
	# 	id,
	# 	DATABASE_NAME)
	# userdata['id'] = dbref
	# accounts.update_one(filter={"name": 'Andrew'}, update={'$set': userdata}, upsert=True)
	#



	# accounts = db1.setCollection('Account')
	# print('Accounts Count: {0}'.format(accounts.count_documents({})))
	# for rec in accounts.find():
	# 	pprint.pprint(rec)

	record = db1.findRecord('Account', {'name': 'Andrew'})
	pprint.pprint(record)
	db1.close()

	# db_names = client.list_database_names()
	# if DATABASE_NAME in db_names:
	# 	print('Found Database')

	

