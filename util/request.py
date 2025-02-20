class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables
        splitter = ('\r\n\r\n').encode()
        splitReq = request.split(splitter)
        #print(f"splitreq:{splitReq}")
        
        decodedText = self.stringify(splitReq[0])
        divyUp = decodedText.split('\r\n')
        #print(f"divyUp:{divyUp}")
        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}

        mvp = divyUp[0]
        divyUp.remove(divyUp[0])
        self.joshAllen(mvp)

        self.parseHeaders(divyUp)
        self.body = splitReq[1] if len(splitReq) > 1 else b""



    # takes in a request without body and returns that decoded
    def stringify(self, req):
        return req.decode("utf-8")
    
    # sets the method, version, and path variables, aka the MVP: Josh Allen
    def joshAllen(self, mvpString):
        jAllen = mvpString.split(' ')

        self.method = jAllen[0] if len(jAllen) > 0 else "GET"
        self.path = jAllen[1] if len(jAllen) > 1 else "/"
        self.http_version = jAllen[2] if len(jAllen) > 2 else "HTTP/1.1"
        

    # parseHeaders takes in a list of strings, each string in list is a header key and value, sets header and cookie dicts
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
    print(f"method:{request.method}\nversion:{request.http_version}\npath:{request.path}")
    assert request.method == "GET"
    assert request.http_version == "HTTP/1.1"
    assert request.path == "/"
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
