from util.response import Response
from util import response
from util import database as dbm
import json
import uuid

# according to project write up, I may need to use a different function
# when the requested path is "/" and "/chat"
def serveCSS(request, handler):
    res = Response()
    res.path = request.path
    hehe = response.findContentType(res.path, res.headList)
    if hehe == "e":
        res.validPath = False

    data = response.fileReader(res.path).decode()
    res.text(data)
    handler.request.sendall(res.to_data())

# Image handler should handle all responses for /public/img requests
def serveImg(request, handler):
    res = Response()
    res.path = request.path
    response.findContentLength(res.path,res.headList)
    data = response.fileReader(res.path)
    if data == "e" or data == b"e":
        res.validPath = False
    res.bytes(data)
    handler.request.sendall(res.to_data())

def faviconLoader(request, handler):
    res = Response()
    print(f"requested:{request.path}")
    res.path = "/public/imgs/favicon.ico"
    response.findContentLength(res.path,res.headList)
    data = response.fileReader(res.path)
    if data == "e" or data == b"e":
        res.validPath = False
    res.bytes(data)
    handler.request.sendall(res.to_data())



def serveHTML(request, handler):
    # initializing the response object first will allow for working with data in that object
    res = Response()
    # Notes, cannot simply send the request to the Response object as it should not take any args other than self
    # as a result all request processing must be done OUTSIDE the Response class
    #print(f"request: {request.headers}")
    
    path = request.path
    if request.path == "/":
        path += "/public/index.html"
    if "js" in path:
        path2 = "/public/js"
        if "/public/js" in path:
            i = 0
        else:
            path = path2 + path
    if "layout" in path:
        path2 = "/public/layout"
        path = path2 + path
    if "chat" in path and "js" not in path:
        path = "/public/chat.html"

    res.path = path
    hehe = response.findContentType(path, res.headList)
    if hehe == "e":
        res.validPath = False



    # a result of my laziness I didn't make a seperate path for either of these routes
    # explicitly checks if path is for index.html or chat.html and renders page using
    # layout as defined
    if "index.html" in path or "chat.html" in path:
        data = response.fileReader("/public/layout/layout.html").decode()
        data2 = response.fileReader(path).decode()
        data = data.replace("{{content}}", data2)
    else:
        data = response.fileReader(path).decode()
    
    if data == "e" or data == b"e":
        res.validPath = False

  
    res.text(data) 
    handler.request.sendall(res.to_data())


# for getting & displaying chat messages
def serveChats(request, handler):
    res2 = Response()
    res2.path = request.path
    allData = dbm.getAllMessages()
        
    retList = []
    headList = res2.headList
    for x in allData:
        if x.get("deleted") != "True":
            # for making the data more human readable, remove the ID value mongo assigns
            cleanx = {key: value for key, value in x.items() if key != '_id'}
            retList.append(cleanx)
    res2.data4json = {"messages":retList}
    res2.json({"messages":retList})
    handler.request.sendall(res2.to_data())

def serveChatsOld(request, handler):
    print(f"I am trying to respond with chats")
    res = Response()
    res.path = request.path
    allData = dbm.getAllMessages()
    retList = []
    headList = res.headList
    for x in allData:
        if x.get("deleted") != "True":
            # for making the data more human readable, remove the ID value mongo assigns
            cleanx = {key: value for key, value in x.items() if key != '_id'}
            retList.append(cleanx)
    res.json(retList)
    handler.request.sendall(res.to_data())

# for posting chat messages
# will also involve setting a session cookie for user if not logged in
def addChats(request, handler):
    print("\n\nADDING A CHAT\n\n")
    res = Response()
    res.method = request.method
    body = request.body

    print(f"Chat body: {body}")
    cookies = request.cookies
        

    dBody = body.decode()
    dBody = dBody.replace("&","&amp;")
    dBody = dBody.replace("<","&lt;")
    dBody = dBody.replace(">","&gt;")
    wBody = json.loads(dBody)

    print(f"data to add: {wBody}")
    allData = dbm.getAllMessages()
    try:
        lastValue = allData[-1]
        idValue = lastValue.get("id",None)
    except IndexError:
        idValue = None

    # inserts the message into the database
    # retCode will return a value that will be used to determine
    # if a cookie needs to set
    retCode = dbm.insertMessage(wBody,idValue,cookies)
    if retCode[0]:
        # must set session cookie
        unique = str(retCode[1])
        print(f"unique val: {unique}")
        directives = "; Path=/; Max-Age=259200; HttpOnly; SameSite=Strict"
        value = unique+directives
        res.cookieList.update({"session":value})

    allData = dbm.getAllMessages()
    retListPost = []
    for x in allData:
        cleanx = {key: value for key, value in x.items() if key != "_id"}
        retListPost.append(cleanx)
    lastValue2 = retListPost[-1]
    res.data4json = lastValue2
    res.json(lastValue2)
    res.status = "Created"
    res.code = "200"
    

    handler.request.sendall(res.to_data())
    print(f"final response: {res.responseTxt}")
# for updating a chat message
def updateChats(request, handler):
    print("UPDATING CHAT")
    res = Response()
    update = json.loads(request.body)

    #print(f"update value: {update}")
    uContent = update.get('content')
    uContent = uContent.replace("&","&amp;")
    uContent = uContent.replace("<","&lt;")
    uContent = uContent.replace(">","&gt;")
    update.update({'content':uContent})

    #print(f"update now:{update}")


    res.path = request.path
    print(f"requested update: {request.path}")
    msgId = res.path.split('/chats/')[1]
    
    
    message = dbm.findMessageById(msgId)
    print(f"Message: {message}")
    whoCanEdit = message[0]["authorId"]

    session = request.cookies.get("session")
    print(request.cookies.items())
    print(f"session: {session}")
    print(f"who can edit: {whoCanEdit}")
    print(f"session:{session}\nwhocanedit:{whoCanEdit}")
    if session == whoCanEdit:
        print("permission to update granted")
        dbm.updateMessage(msgId,update)
    else:
        print("you lack perms")
        res.code = 403
        res.status = "Forbidden"
    
    handler.request.sendall(res.to_data())


# for deleting a chat message
def deleteChats(request, handler):
    res = Response()
    
    res.path = request.path
    
    msgId = res.path.split('/chats/')[1]
    message = dbm.findMessageById(msgId)
    whoCanEdit = message[0]["authorId"]
    session = request.cookies.get("session")

    if session == whoCanEdit:
        print("permission to delete granted")
        dbm.deleteMessage(msgId)
    else:
        #print("you lack perms")
        res.code = 403
        res.status = "Forbidden"
    handler.request.sendall(res.to_data())