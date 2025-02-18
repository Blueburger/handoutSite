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
    retCode = (False,"haha")
    # session will either get the session token of whoever sent the message or return None
    session = cookies.get("session")
    # if session exists then the uniqueID for this user is the session token
    if session:
        uniqueId = cookies["session"]
    else:    
        # if no session token exists one is created and the return value is a tuple that informs the caller t
        # that a new uuid was generated along with returning at uuid as a string
        uniqueId = str(uuid.uuid4())
        retCode = (True,uniqueId)     
    # unsure why this issue was happening exactly but when DB gets reset the first message
    # sent will always assign the session token as /
    # hopefully not a sign of a bigger issue, the easy fix is to explicity check if the session token value is /
    # and then treat it as if this is someone new sending msg for first time
    #if uniqueId == "/":
    #    uniqueId = str(uuid.uuid4())
    #    retCode = (True,uniqueId)
    
    displayName = str(uniqueId)
    displayName = findGuestName(displayName)
    
    # originally I was using the uuid as the guest display name, realized the security flaw in that
    # then I decided to use the uuid still but replace chars so real uuid is protected
    # but the resulting names were hard to make out and even though they were unique it was hard to tell
    #for char in displayName:
    #    if ord(char) % 2 == 0:
    #        displayName = displayName.replace(char,"X")
    #    if ord(char) % 3 == 0:
    #        displayName = displayName.replace(char,"D")
    #    if ord(char) % 5 == 0:
    #        displayName = displayName.replace(char,":")
    #    if ord(char) % 7 == 0:
    #        displayName = displayName.replace(char,"3")
    
    



    if id == None:
        id = 1
    else:
        id = int(id)
        id +=1
    id = str(id)

    if not displayName:
        msgs = getAllMessages()
        try:
            lastMsg = msgs[-1]
            lastMsgID = int(lastMsg["id"])
            newVal = lastMsgID +1
        except IndexError:
            newVal = 1
        guestName = "Guest:" + str(newVal)
    else:
        guestName = displayName
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

# takes in a string of a uuid and returns the name of whatever guest has that Id
def findGuestName(id):
    guestName = list(chat_collection.find({"authorId":id}))
    try:
        guestName = guestName[0]["author"]
    except IndexError:
        guestName = None
    with open("logs.txt","w") as file:
        file.write(f"guestName retrieved: {guestName}")
    print(f"GUEST NAME: {guestName}")
    return guestName

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