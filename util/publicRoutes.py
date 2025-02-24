from util.response import Response
from util import response
from util import database as dbm
from util import helper as help
import json
import uuid







# according to project write up, I may need to use a different function
# when the requested path is "/" and "/chat"
def serveCSS(request, handler):
    res = Response()
    res.path = request.path
    ctype = help.findContentType(res.path, res.headList)
    
    if not ctype:
        errorSay(request, handler)

    data = help.fileReader(res.path).decode()
    res.text(data)
    handler.request.sendall(res.to_data())

# Image handler should handle all responses for /public/img requests
def serveImg(request, handler):
    res = Response()
    res.path = request.path
    help.findContentLength(res.path,res.headList)
    data = help.fileReader(res.path)
    if not data:
        errorSay(request, handler)
    res.bytes(data)
    handler.request.sendall(res.to_data())

def faviconLoader(request, handler):
    res = Response()
    print(f"requested:{request.path}")
    res.path = "/public/imgs/favicon.ico"
    help.findContentLength(res.path,res.headList)
    data = help.fileReader(res.path)
    if not data:
        errorSay(request, handler)
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
    if "chat" in path and "js" not in path:
        path = "/public/chat.html"

    res.path = path
    ctype = help.findContentType(path, res.headList)
    
    if not ctype:
        errorSay(request, handler)



    # a result of my laziness I didn't make a seperate path for either of these routes
    # explicitly checks if path is for index.html or chat.html and renders page using
    # layout as defined
    print(f"path:{path}")
    bslogic = path.split("/")
    last = bslogic[-1]
    if "index.html" == last or "chat.html" == last:
        data = help.fileReader("/public/layout/layout.html").decode()
        data2 = help.fileReader(path).decode()
        data = data.replace("{{content}}", data2)
    else:
        data = help.fileReader(path).decode()

    #if "index.html" in path or "chat.html" in path:
    #    data = help.fileReader("/public/layout/layout.html").decode()
    #    data2 = help.fileReader(path).decode()
    #    data = data.replace("{{content}}", data2)
    #else:
    #    data = help.fileReader(path).decode()

  
    res.text(data) 
    handler.request.sendall(res.to_data())


# for getting & displaying chat messages
def serveChats(request, handler):
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
    res.data4json = {"messages":retList}
    res.json({"messages":retList})
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
    res.set_status(200, "OK")
    res.text('message created')

    handler.request.sendall(res.to_data())
    print(f"final response: {res.responseTxt}")




# for updating a chat message
def updateChats(request, handler):
    print("UPDATING CHAT")
    res = Response()
    res.method = request.method
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
        forbidden(request, handler)
    
    handler.request.sendall(res.to_data())




# for deleting a chat message
def deleteChats(request, handler):
    res = Response()
    res.method = request.method
    res.path = request.path
    msgId = res.path.split('/chats/')[1]
    message = dbm.findMessageById(msgId)
    whoCanEdit = message[0]["authorId"]
    session = request.cookies.get("session")

    if session == whoCanEdit:
        print("permission to delete granted")
        dbm.deleteMessage(msgId)
    else:
        forbidden(request, handler)
    handler.request.sendall(res.to_data())

# returns the error message
# called individually by the specific end points if they detect the request was improper
def errorSay(request, handler):
    res = Response()
    res.set_status(404, "Not Found")
    #res.code = 404
    #res.status = "Not Found"
    res.text("The page you are looking for could not be found")
    handler.request.sendall(res.to_data())

# Returns the 404 Forbidden response
def forbidden(request, handler):
    res = Response()
    res.set_status(403, "Forbidden")
    handler.request.sendall(res.to_data())

# FOR AO 1, adding emoji reactions
def addEmoji(request, handler):
    res = Response()
    res.method = request.method
    res.path = request.path
    mojiReact = json.loads(request.body)
    emoji = mojiReact.get("emoji")
    print(f"ADDEMOJI:\nmojiReact:{mojiReact}")
    msgId = res.path.split('/reaction/')[1]
    message = dbm.findMessageById(msgId)
    whoCanEdit = message[0]["authorId"]
    session = request.cookies.get("session")

    success = dbm.addMoji(msgId,emoji,session)
    if success == 1:
        forbidden(request, handler)
    handler.request.sendall(res.to_data())


def removeEmoji(request, handler):
    res = Response()
    res.method = request.method
    res.path = request.path
    mojiReact = json.loads(request.body)
    emoji = mojiReact.get("emoji")
    print(f"REMOVE EMOJI:\nmojiReact:{mojiReact}")
    msgId = res.path.split('/reaction/')[1]
    message = dbm.findMessageById(msgId)
    whoCanEdit = message[0]["authorId"]
    session = request.cookies.get("session")

    if session == whoCanEdit:
        dbm.removeMoji(msgId,emoji,session)
    else:
        forbidden(request, handler)
    handler.request.sendall(res.to_data())


# I AM GOING TO SEE THE MOVIE: THE MONKEY 
# SO taking a break from this, change nickname is mostly done
# currently the only issue is that if a nickname is set, that nickname is NOT applied to new msgs from same user
# the only way Nicknames are updated for any message is if the change nickname API call is sent
# Must modify the insertMessage logic so that it can account for if a nickname has already been selected
# ALSO: must html escape everything
def changeNickName(request, handler):
    res = Response()
    newNameRequest = json.loads(request.body)
    session = request.cookies.get("session")
    name =  newNameRequest.get("nickname")
    # if name is None
    if not name:
        pass
    else: # name does exist
        name = name.replace("&","&amp;")
        name = name.replace("<","&lt;")
        name = name.replace(">","&gt;")
        dbm.updateName(session, name)
    handler.request.sendall(res.to_data())

