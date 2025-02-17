import json
import sys
import os
from util import publicRoutes as pr
from pymongo import MongoClient
import uuid

docker_db = os.environ.get('DOCKER_DB', "false")

if docker_db == "true":
    print("using docker compose db")
    mongo_client = MongoClient("mongo")
else:
    print("using local db")
    mongo_client = MongoClient("localhost")

db = mongo_client["cse312"]

chat_collection = db["chat"]


# fine this will be the data base manager

def insertMessage(message,id,cookies):


    #print(f"\n\n THIS IS THE DATA BASE MANAGER INSERTING A MESSAGE")
    #print(f"\n message:{message}")
    messageData = message.get("content")
   
    #print(f"message DATA:{messageData}")
    messageU = {"content":messageData}

    # using uuid lib to gen a uuid
    # this uuid will be tied to "Guest:" to make a unique guest name
    # the uuid by itself will be set as the session cookie
    # because this cookie only needs to be sent when someone sends a message
    # the logic for it will be localized here (may potentially use helper funcs if I think it simplifies things)
    retCode = "N/A"
    session = cookies.get("session")
    if session:
        uniqueId = cookies["session"]
    else:    
        uniqueId = str(uuid.uuid4())
        retCode = (True,uniqueId)   
    if uniqueId == "/":
        uniqueId = str(uuid4())
        retCode = (True,uniqueId)
    displayName = str(uniqueId)
    for char in displayName:
        if ord(char) % 2 == 0:
            displayName = displayName.replace(char,"X")
        if ord(char) % 3 == 0:
            displayName = displayName.replace(char,"D")
        if ord(char) % 5 == 0:
            displayName = displayName.replace(char,":")
        if ord(char) % 7 == 0:
            displayName = displayName.replace(char,"3")
    guestName = "Guest:" + displayName
    



    if id == None:
        id = 1
    else:
        id = int(id)
        id +=1
    id = str(id)
    # token and auth stuff will eventually go here
    # on second thought Im just going to add it here rn
    token = cookies.get("token")
    # eventually authenticated will call a helper function
    # it will then check the token for validity
    # for simplicity, and since auth is hw 2 stuff, it is just set to False
    authenticated = False 

    if not authenticated:
        insert = {"author":guestName,"id":id,"updated":False,"deleted":"False","authorId":uniqueId}
                  
    else:
        # eventually the logic for checking and authenticationg the XSRF token will be here
        pass
    
    insert.update(messageU)
    print(f"\n\nfinal message Value: {insert}")
    chat_collection.insert_one(insert)

    return retCode


def getAllMessages():
    return list(chat_collection.find({}))

def findMessageById(id):
    strId = str(id)
    return list(chat_collection.find({"id":strId}))

def deleteMessage(id):
    strId = str(id)
    filter = {"id": strId}
    update = {'$set':{"deleted":"True"}}
    chat_collection.update_one(filter, update)

def updateMessage(id,body):
    strId = str(id)
    filter = {"id": strId}
    newMessage = body["content"]
    update = {'$set':{"content":newMessage,"updated":True}}
    success = chat_collection.update_one(filter,update)