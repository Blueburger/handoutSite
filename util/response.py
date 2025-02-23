import json

class Response:
    def __init__(self):
        
        self.responseTxt = b''
        self.http = 'HTTP/1.1 '
        self.body = b''
        self.code = '200'
        self.status = 'OK'
        self.headList = {"X-Content-Type-Options": "nosniff","Content-Type": "text/plain; charset=utf-8","Content-Length": "0",}
        self.cookieList = {}
        self.path = ''
        self.method = ''
        self.data4json = ''
        self.iserror = False

    # takes in a code and text and sets the code and status instance vars
    # code can be an int or a string (it is explicitly converted into str later)
    # text should be a string
    def set_status(self, code, text):
        self.code = code
        self.status = text
        return self

    # updates the headList dict by either replacing a pairing or adding a new one
    def headers(self, headers):
        self.headList.update(headers)
        return self

    # updates the cookieList dict by either replacing a pairing or adding a new one
    def cookies(self, cookies):
        self.cookieList.update(cookies)
        return self

    # takes in byte data and applies it to the current body
    def bytes(self, data):
        self.body += data
        return self
    
    # takes in text data, encodes that and applies it to the current body
    def text(self, data):
        data = data.encode()
        self.body += data
        return self
        
    # json calls self.headers to update the content type
    # then sets the body data to the encoded json
    def json(self, data):
        self.headers({"Content-Type":"application/json"})
        self.body = json.dumps(data).encode()
        return self

    # to data will be the builder, it will call all the necessary functions to build and return the proper response
    def to_data(self):
        # ensure responseTxt is empty before building the response
        self.responseTxt = b''
        # step 1: set the http version
        self.responseTxt += self.http.encode() 
        # step 2: set the status
        self.responseTxt += (f"{self.code} {self.status}").encode()
        # step 3: find and apply necessary headers
        help.findContentLength(self.body,self.headList)
        help.findContentType(self.path,self.headList)
        for elem, val in self.headList.items():
            headType = elem
            headVal = val
            self.responseTxt = self.responseTxt + ("\r" + "\n" + str(headType) + ": " + str(headVal)).encode()
        # step 4: apply necessary cookies
        for elem, val in self.cookieList.items():
            cookieType = elem
            cookieVal = val
            self.responseTxt = self.responseTxt + ("\r" + "\n" + "Set-Cookie: " + str(cookieType) + "=" + str(cookieVal)).encode()
        # step 5: apply necessary body data
        # start by adding the double CRLF to the end of the response
        self.responseTxt += ("\r" + "\n" + "\r" + "\n").encode()

        # explicitly checks if the body is bytes, if not it converts
        # this logic should be redundant now as self.body will always be a byte string        
        if not isinstance(self.body, bytes):
            self.body = str(self.body).encode()

        # add body to the response
        self.responseTxt = self.responseTxt + self.body
        # return the response text
        return self.responseTxt





        















def test1():
    res = Response()
    res.text("hello")
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 5\r\n\r\nhello'
    actual = res.to_data()
    print(f"actual: {actual}")
    assert expected == actual
    print(f"\n\n----\ntest passed\n----\n\n")


def test2():
    res = Response()
    res.text("Passersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of blood")
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 488\r\n\r\nPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of bloodPassersby were amazed by the unusually large amounts of blood'
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
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 16\r\n\r\nhellohello2hello'
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
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 16\r\nSet-Cookie: session=batman; Max-Age=259200;\r\n\r\nhellohello2hello'
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
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 13\r\ndonald-duck: rnald\r\nmickey: mouse\r\nSet-Cookie: session=batman; Max-Age=259200;\r\nSet-Cookie: dummy=indeed\r\n\r\nhi therehello'
    actual = res.to_data()
    assert(actual == expected)
    print("====== TEST 6 HATH PASSED ========")



def test7():
    res = Response()
    res.path = "dorkburger"
    res.set_status(404, "Not Found")
    res.text('The Page you are looking for does not exist')
    actual = res.to_data()
    expected = b'HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 43\r\n\r\nThe Page you are looking for does not exist'
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
    actual2 = res2.to_data()
    expected2 = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 0\r\ndeg: men\r\nSet-Cookie: dog=man\r\nSet-Cookie: hands=arms\r\n\r\n'
    print(f"actual 2 :{actual2}")
    assert actual2 == expected2
    print("Test 8 passed")


def test9():
    res = Response()
    res.bytes(b'hello bud')
    res.text('hello bud')
    res.bytes(b'hello bud')
    expected = b'HTTP/1.1 200 OK\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 27\r\n\r\nhello budhello budhello bud'
    actual = res.to_data()
    print(f"actual:{actual}")
    assert actual == expected
    print("Test 9 passed")


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
    test9()
else:
    from util import helper as help