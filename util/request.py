class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables
        
        decodedText = self.stringify(request)
        divyUp = decodedText.split('\r\n')

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
            workableData = self.parseHeaders(divyUp)
            bodydataLen = len(workableData)
            bodyData = workableData[bodydataLen-1]
            self.body = bodyData.encode()
        except IndexError:
            pass


    # takes in a request then builds that request back as a string of decoded characters
    # note, this will not be proper for image uploads but that isn't relevant in HW 1
    def stringify(self, req):
        bs= ""
        for char in req:
            bs = bs+chr(char)
        return bs
    
    # sets the method, version, and path variables, aka the MVP: Josh Allen
    def joshAllen(self, mvpString):
        jAllen = mvpString.split(' ')
        try:
            self.method = jAllen[0]
            self.path = jAllen[1]
            self.http_version = jAllen[2].split('/')[1]
        except IndexError:
            pass

    # parseHeaders takes in a list of strings, each string in list is a header key and value, sets header and cookie dicts
    def parseHeaders(self, headers):
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
