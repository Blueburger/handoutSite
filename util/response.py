import json

fileLibrary = {
    "ico": "image/x-icon",
    "js": "application/javascript; charset=UTF-8",
    "html": "text/html; charset=UTF-8",
    "css": "text/css; charset=UTF-8", 
    "jpg":"image/jpeg",
    "png":"image/png",
    "gif":"image/gif",
    "webp":"image/webp"
}

class Response:
    def __init__(self):
        
        self.responseTxt = b''
        self.http = 'HTTP/1.1 '
        self.body = b''
        self.code = '200'
        self.status = 'OK'
        self.headList = requiredHeaders()
        self.cookieList = {}
        self.path = ''
        self.validPath = True
        self.method = ''
        self.data4json = ''

    def set_status(self, code, text):
        self.code = code
        self.status = text
        return self

    def headers(self, allHeader):
        for elem, val in allHeader.items():
            headType = elem
            headVal = val
            self.responseTxt = self.responseTxt + ("\r" + "\n" + str(headType) + ": " + str(headVal)).encode()
            # ideally this will remove the key value pair that was just added to the response
            # this way if headers is called again it won't re add already added headers
            # this also means that the allHeader arg for this function MUST be the self.headList value
            #self.headList.pop(elem)
            # does not work raises error and in retrospect it wasn't even an issue to begin with
        self.headList = {}
        return self


    # similar to the logic in headers, cookies will also require the self.cookies be passed in as its arg
    # in this situation the cookie dict values should be along the lines of cookieName: cookie value and all directives
    def cookies(self, cookies):
        for elem, val in cookies.items():
            print(f"SETTING COOKIES:\nelem:{elem}\nvalue:{val}")
            cookieType = elem
            cookieVal = val
            self.responseTxt = self.responseTxt + ("\r" + "\n" + "Set-Cookie: " + str(cookieType) + "=" + str(cookieVal)).encode()
            #self.cookieList.pop(elem)
        self.cookieList = {}
        return self

    # to be used when the body of the request is data that SHOULD NOT BE DECODED
    def bytes(self, data):
        self.body += data
        return self
    
    # akin to bytes but when the body of the request can be plaintext
    def text(self, data):
        data = data.encode()
        self.body += data
        return self
        

    def json(self, data):
        # I mean this should work, json.dumps takes list, string, and dict as valid types
        self.headList.update({"Content-Type":"application/json; charset=UTF-8"})
        
        loadData = json.dumps(data)
        #print(f"load data value: {loadData}")
        self.body = loadData.encode()
        return self

    # to data will be the builder, it will call all the necessary functions to build and return the proper response
    def to_data(self):
        
        
        # step 1: set the http versions
        self.responseTxt += self.http.encode() 
        # step 2: set the status
        self.responseTxt += (f"{self.code} {self.status}").encode()
        #self.set_status(self.code, self.status)
        # step 3: apply necessary headers
        findContentLength(self.body,self.headList)
        findContentType(self.path,self.headList)

        print(f"\n=== DEBUG: Building Response ===")
        print(f"STATUS: {self.code} {self.status}")
        print(f"HEADERS: {self.headList}")
        print(f"COOKIES: {self.cookieList}")
        print(f"BODY LENGTH: {len(self.body)}\n")
        print(f"DEBUG: Nosniff Header Present? {'X-ContentTypeOptions' in self.headList}")

        self.headers(self.headList)
        # step 4: apply necessary cookies
        self.cookies(self.cookieList)
        # step 5: apply necessary body data
        # we are assuming here that text/data would have been called already
        # all that is left is to add that data onto the end of the response
        # adds the double CRLF that preceeds body
        self.responseTxt += ("\r" + "\n" + "\r" + "\n").encode()

        # updated so response text should always be bytes
       
        # encodes the existing body data if it is not already
        
        if not isinstance(self.body, bytes):
            self.body = str(self.body).encode()
        
        # add the body data to the encoded response text, body data is assumed to be encoded already
        self.responseTxt = self.responseTxt + self.body

        if self.validPath == True:
            return self.responseTxt
        else:
            print(f"the requested path for:{self.path}\nwas invalid and has been aborted")
            er = "HTTP/1.1 404 Not Found\r\nX-ContentTypeOptions: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 43\r\n\r\nThe Page you are looking for does not exist".encode()
            return er


# fileReader takes in a string path and returns the file data
# does NOT check if path is valid, this will need to be handled before calling this function
def fileReader(path):
    try:
        with open (f".{path}","rb") as file:
            data = file.read()
        return data
    except FileNotFoundError:
        return b"e"
    
        
# uses file name to find content type and adds to headerList
def findContentType(file, headerList):
    #print(f"\n\nfile: {file}\n\n")
    try:
        name, extension = file.split(".")
        contentType = fileLibrary.get(extension)
        if contentType:
            headerList.update({"Content-Type":contentType})
        return "f"
    except ValueError:
        return "e"
        
        

# uses the body data to determine the content length
def findContentLength(data, headerList):
    #print(f"data: {data}\nheadlistb4: {headerList}")
    contentLength = str(len(data))
    #print(f"content length: {contentLength}")
    headerList.update({"Content-Length":contentLength})
    #print(f"headlist after: {headerList}")

# a creates and returns a dictionary of headers
# this dict will be updated as the response is built to contain all proper headers
def requiredHeaders():
    headList = {
        "X-ContentTypeOptions": "nosniff",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Length": "0",
    }

    return headList

def test1():
    res = Response()
    res.text("hello")
    expected = b'HTTP/1.1 200 OK\r\nX-ContentTypeOptions: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 5\r\n\r\nhello'
    actual = res.to_data()
    print(f"actual: {actual}")
    assert expected == actual
    print(f"\n\n----\ntest passed\n----\n\n")


def test2():
    res = Response()
    res.text("Passersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of blood")
    expected = b'HTTP/1.1 200 OK\r\nX-ContentTypeOptions: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 488\r\n\r\nPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of blood'
    actual = res.to_data()
    #print(f"actual:\n{actual}")
    assert expected == actual


def test3():
    res = Response()
    imgData = fileReader("/public/imgs/dog.jpg")
    res.bytes(imgData)
    res.path = "/public/imgs/dog.jpg"

    expected = b'HTTP/1.1 200 OK\r\nX-ContentTypeOptions: nosniff\r\nContent-Type: image/jpeg\r\nContent-Length: 13159\r\n\r\n'
    expected = expected + imgData
    actual = res.to_data()
    #print(f"actual:\n{actual}")
    #print(f"expected:\n{expected}")
    assert expected == actual
    print('TEST 3 PASSED')


def test4():
    res = Response()
    res.text("hello")
    res.bytes(b"hello2")
    res.text("hello")
    expected = b'HTTP/1.1 200 OK\r\nX-ContentTypeOptions: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 16\r\n\r\nhellohello2hello'
    actual = res.to_data()
    print(f"actual: {actual}")
    assert expected == actual
    print(f"\n\n----\ntest 4 passed\n----\n\n")

def test5():
    res = Response()
    res.cookieList.update({'session':'batman; Max-Age=259200;'})
    res.text("hello")
    res.bytes(b"hello2")
    res.text("hello")
    expected = b'HTTP/1.1 200 OK\r\nX-ContentTypeOptions: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 16\r\nSet-Cookie: session=batman; Max-Age=259200;\r\n\r\nhellohello2hello'
    actual = res.to_data()
    print(f"actual:\n{actual}")
    print(f"expected:\n{expected}")
    assert expected == actual
    print(f"\n\n----\ntest 5 passed\n----\n\n")


if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()
    test5()