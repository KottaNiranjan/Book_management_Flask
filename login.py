from pymongo import MongoClient
from flask import jsonify

client=MongoClient("localhost",27017)
user_db=client.Assignment_3.user_db
