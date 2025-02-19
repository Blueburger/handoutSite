class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables
        splitter = ('\r\n\r\n').encode()
        splitReq = request.split(splitter)
        print(f"splitreq:{splitReq}")
        
        decodedText = self.stringify(splitReq[0])
        divyUp = decodedText.split('\r\n')
        print(f"divyUp:{divyUp}")
        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}

        mvp = divyUp[0]
        divyUp.remove(divyUp[0])
        self.joshAllen(mvp)

        try:
            #workableData = self.parseHeaders(divyUp)
            #print(f"workable data:{workableData}")
            #bodydataLen = len(workableData)
            #bodyData = workableData[bodydataLen-1]
            #self.body = bodyData.encode()
            self.parseHeaders(divyUp)
            self.body = splitReq[1]
        except IndexError:
            pass


    # takes in a request then builds that request back as a string of decoded characters
    # note, this will not be proper for image uploads but that isn't relevant in HW 1
    def stringify(self, req):
        return req.decode("utf-8")
    
    # sets the method, version, and path variables, aka the MVP: Josh Allen
    def joshAllen(self, mvpString):
        jAllen = mvpString.split(' ')
        self.method = jAllen[0] if len(jAllen) > 0 else ""
        self.path = jAllen[1] if len(jAllen) > 1 else "/"
        self.http_version = jAllen[2].split('/')[1] if len(jAllen) > 2 else "1.1"
        

    # parseHeaders takes in a list of strings, each string in list is a header key and value, sets header and cookie dicts
    def parseHeadersOld(self, headers):
        cookies = False
        prevHeader = "null"

        for headPair in headers:
            if headPair != "" and prevHeader != "":
                splitValues = headPair.split(": ")
                head = splitValues[0]
                if head == "Cookie":
                    cookies = True
                try:
                    value = splitValues[1]
                except IndexError:
                    pass
                if cookies:
                    self.headers[head] = value
                    seperateCookies = value.split("; ")
                    for cookiePair in seperateCookies:
                        pairing = cookiePair.split("=")
                        try:
                            self.cookies[pairing[0]] = pairing[1]
                        except IndexError:
                            pass
                    cookies = False
                else:
                    self.headers[head] = value
            prevHeader = headPair
        return headers
    


    def parseHeaders(self, headers):
        for headPair in headers:
            if ": " not in headPair:
                continue
        
            key, value = headPair.split(": ", 1)
            self.headers[key] = value
            
            if key == "Cookie":
                for cookiePair in value.split("; "):
                    if "=" in cookiePair:
                        cookieKey, cookieVal = cookiePair.split("=", 1)
                        self.cookies[cookieKey.strip()] = cookieVal.strip()
                        
    
def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str
    print("\n\n----------------------------------\n\nTEST 1 PASSED\n\n----------------------------------")
    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct

def test2():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""

    print("\n\n----------------------------------\n\nTEST 2 PASSED\n\n----------------------------------")
def test3():
    request = Request(b'POST /spanghorn HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nCookie: id=batman; visits=4\r\n\r\nThis is the body text and I Have Spoken')
    assert request.method == "POST"
    assert "Host" in request.headers
    assert "id" in request.cookies
    assert request.body == b"This is the body text and I Have Spoken"
    print(f"headers: {request.headers}\n\n")
    print(f"cookies: {request.cookies}")
    print("\n\n----------------------------------\n\nTEST 3 PASSED\n\n----------------------------------")
if __name__ == '__main__':
    test1()
    test2()
    test3()
