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
    
    displayName = str(uniqueId)
    displayName = findGuestName(displayName)
    
    
    # checks if the returned ID value of the message exists
    # if not set the id to 1, if it did exist id is set to id+1
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
    reactions = findReactions(id)
    if not reactions:
        reactions = {}
    if not authenticated:
        insert = {"author":guestName,"id":id,"updated":False,"deleted":"False","authorId":uniqueId,"reactions":reactions}              
    else:
        # eventually the logic for checking and authenticationg the XSRF token will be here
        pass
    
    hasName = nickNameCheck(session)
    if hasName:
        insert.update({"nickname":hasName})

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

# takes the unique ID value of a message then returns the reactions dict of said message
def findReactions(id):
    message = findMessageById(id)
    #print(f"DATA BASE:\nmessage:{message}")
    reactions = None
    if message:
        reactions = message[0]["reactions"]
        #print(f"DATA BASE:\nreactions:{reactions}")
    return reactions

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
    reactions = findReactions(id)
    newMessage = body["content"]
    update = {'$set':{"content":newMessage,"updated":True}}
    success = chat_collection.update_one(filter,update)

def addMoji(id,moji,reactor):
    strId = str(id)
    filter = {"id": strId}
    print(f"DATA BASE ADD EMOJI:\nID:{id}\nEmoji:{moji}\nreactor:{reactor}")
    reactions = findReactions(id) 
    print(f"current message reactions:{reactions}")
    alreadyHas = reactions.get(moji)
    if not alreadyHas:
        reactions.update({moji:[reactor]})
    else:
        if reactor in alreadyHas:
            return 1
        else:
            alreadyHas.append(reactor)
            reactions.update({moji:alreadyHas})
    update = {'$set':{"reactions":reactions}}
    success = chat_collection.update_one(filter,update)

# removes an emoji reaction, if the individual removing the emoji was the only one who reacted
# then remove the emoji from reactions entierly
def removeMoji(id, moji, reactor):
    strId = str(id)
    filter = {"id": strId}
    print(f"DATA BASE REMOVE EMOJI:\nID:{id}\nEmoji:{moji}\nreactor:{reactor}")
    reactions = findReactions(id) 
    print(f"current message reactions:{reactions}")
    # we know the reactions list will have the specific emoji in it already
    # so it should be safe to assume that previousReactions could never have value None
    previousReactions = reactions.get(moji)
    if reactor in previousReactions:
        previousReactions.remove(reactor)
        # if removing the reactor from the reactions list results in that list being empty
        # remove the emoji reaction as a whole from the message
        if len(previousReactions) == 0:
            reactions.pop(moji)
        else:
            reactions.update({moji:previousReactions})
    update = {'$set':{"reactions":reactions}}
    success = chat_collection.update_one(filter,update)
    print(f"modified message reaction:{reactions}")

# takes in a session token and a nickname both as strings
def updateName(sesToken, newName):
    filter = {"authorId":str(sesToken)}
    chat_collection.update_many(filter,{'$set':{"nickname":newName}})
    
def nickNameCheck(sesToken):
    filter = {"authorId":str(sesToken)}
    amsg = chat_collection.find_one(filter)
    if amsg:
        nickname = amsg.get("nickname")
        return nickname