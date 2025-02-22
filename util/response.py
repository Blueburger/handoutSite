import json



class Response:
    def __init__(self):
        
        self.responseTxt = b''
        self.http = 'HTTP/1.1 '
        self.body = b''
        self.code = '200'
        self.status = 'OK'
        self.headList = {"X-Content-Type-Options": "nosniff","Content-Type": "text/plain; charset=UTF-8","Content-Length": "0",}
        self.cookieList = {}
        self.path = ''
        self.validPath = False
        self.method = ''
        self.data4json = ''

    def set_status(self, code, text):
        self.code = code
        self.status = text
        return self

    def headers(self, headerDict):
        self.headList.update(headerDict)
        return self

    def cookies(self, cookieDict):
        self.cookieList.update(cookieDict)
        return self


    def ADDheaders(self, allHeader):
        for elem, val in allHeader.items():
            headType = elem
            headVal = val
            self.responseTxt = self.responseTxt + ("\r" + "\n" + str(headType) + ": " + str(headVal)).encode()
        

    # similar to the logic in headers, cookies will also require the self.cookies be passed in as its arg
    # in this situation the cookie dict values should be along the lines of cookieName: cookie value and all directives
    def ADDcookies(self, cookies):
        for elem, val in cookies.items():
            print(f"SETTING COOKIES:\nelem:{elem}\nvalue:{val}")
            cookieType = elem
            cookieVal = val
            self.responseTxt = self.responseTxt + ("\r" + "\n" + "Set-Cookie: " + str(cookieType) + "=" + str(cookieVal)).encode()
            # Zaid said that these functions should simply update the dictionary

    # to be used when the body of the request is data that SHOULD NOT BE DECODED
    def bytes(self, data):
        self.body += data
        # if bytes are added to body, an error response should not be set
        if data != "e" and data != b"e":
            self.validPath = True
        return self
    
    # akin to bytes but when the body of the request can be plaintext
    def text(self, data):
        data = data.encode()
        self.body += data
        # if text is being added to body and error response should not be sent
        
        if data != "e" and data != b"e":
            self.validPath = True
        return self
        

    def json(self, data):
        # I mean this should work, json.dumps takes list, string, and dict as valid types
        self.headers({"Content-Type":"application/json"})
        loadData = json.dumps(data)
        self.body = loadData.encode()
        # Logic: if JSON data is loaded into the body then the requested path would need to be valid
        if data != "e" and data != b"e":
            self.validPath = True
        return self

    # to data will be the builder, it will call all the necessary functions to build and return the proper response
    def to_data(self):
        self.responseTxt = b''
        if not self.validPath:
            print(f"the requested path for:{self.path}\nwas invalid and has been aborted")
            er = "HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 43\r\n\r\nThe Page you are looking for does not exist".encode()
            return er

        
        # step 1: set the http versions
        self.responseTxt += self.http.encode() 
        # step 2: set the status
        self.responseTxt += (f"{self.code} {self.status}").encode()
        #self.set_status(self.code, self.status)
        # step 3: apply necessary headers
        help.findContentLength(self.body,self.headList)
        help.findContentType(self.path,self.headList)
       
        print(f"\n=== DEBUG: Making the Response ===")
        print(f"STATUS: {self.code} {self.status}")
        print(f"HEADERS: {self.headList}")
        print(f"COOKIES: {self.cookieList}")
        print(f"BODY LENGTH: {len(self.body)}\n")
        print(f"DEBUG: Nosniff Header Present? {'X-ContentTypeOptions' in self.headList}")

        self.ADDheaders(self.headList)
        # step 4: apply necessary cookies
        self.ADDcookies(self.cookieList)
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
            er = "HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 43\r\n\r\nThe Page you are looking for does not exist".encode()
            return er






        















def test1():
    res = Response()
    res.text("hello")
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 5\r\n\r\nhello'
    actual = res.to_data()
    print(f"actual: {actual}")
    assert expected == actual
    print(f"\n\n----\ntest passed\n----\n\n")


def test2():
    res = Response()
    res.text("Passersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of blood")
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 488\r\n\r\nPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of blood'
    actual = res.to_data()
    #print(f"actual:\n{actual}")
    assert expected == actual


def test3():
    res = Response()
    #imgData = help.fileReader("/public/imgs/dog.jpg")
    res.bytes(imgData)
    res.path = "/public/imgs/dog.jpg"

    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: image/jpeg\r\nContent-Length: 13159\r\n\r\n'
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
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 16\r\n\r\nhellohello2hello'
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
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 16\r\nSet-Cookie: session=batman; Max-Age=259200;\r\n\r\nhellohello2hello'
    actual = res.to_data()
    print(f"actual:\n{actual}")
    print(f"expected:\n{expected}")
    assert expected == actual
    print(f"\n\n----\ntest 5 passed\n----\n\n")



# Test 6, applying multiple COOKIES and HEADERS
# essentially what needs to happen is we create a response and add numerous headers 
# with subsequent calls to res.headers
# try the same with cookies, and even mix up the order of calls
def test6():
    res = Response()
    res.cookies({'session':'batman; Max-Age=259200;'})
    res.text("hi there")
    res.headers({'donald-duck':"rnald"})
    res.cookies({'dummy':'indeed'})
    res.bytes(b"hello")
    res.headers({'mickey':'mouse'})
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 13\r\ndonald-duck: rnald\r\nmickey: mouse\r\nSet-Cookie: session=batman; Max-Age=259200;\r\nSet-Cookie: dummy=indeed\r\n\r\nhi therehello'
    actual = res.to_data()
    assert(actual == expected)
    print("====== TEST 6 HATH PASSED ========")



def test7():
    res = Response()
    res.path = "dorkburger"
    actual = res.to_data()
    expected = b'HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 43\r\n\r\nThe Page you are looking for does not exist'
    print(f"actual\n{actual}")
    assert actual == expected 
    print("====== TEST 7 HATH PASSED ========")


# test 8, tests with json
def test8():
    res = Response()
    insertValue = {"hemberger":"hipdog"}
    res.text('hello bud')
    res.json(insertValue)
    res.text('hello bud')
    res.json(insertValue)
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: application/json\r\nContent-Length: 23\r\n\r\n{"hemberger": "hipdog"}'
    actual = res.to_data()
    print(f"actual:{actual}")
    assert actual == expected
    res2 = Response()
    res2.cookies({'dog':'man','hands':'arms'})
    res2.cookies({'dog':'man'})
    res2.headers({'deg':'men'})
    res2.validPath = True
    actual2 = res2.to_data()
    expected2 = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Length: 0\r\ndeg: men\r\nSet-Cookie: dog=man\r\nSet-Cookie: hands=arms\r\n\r\n'
    print(f"actual 2 :{actual2}")
    assert actual2 == expected2
    print("Test 8 passed")

if __name__ == '__main__':
    import helper as help
    test1()
    test2()
    #test3()
    test4()
    test5()
    test6()
    test7()
    test8()
else:
    from util import helper as help