# I am putting my helper functions here




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

# adding this helper function here since it being in response may be why I keep failing tests

def fileReader(path):
    try:
        with open (f".{path}","rb") as file:
            data = file.read()
        return data
    except (FileNotFoundError, IsADirectoryError) as e:
        print(f"ERROR REPORTED: {e}")
        return b"e"

        # a creates and returns a dictionary of headers
# this dict will be updated as the response is built to contain all proper headers
def requiredHeaders():
    headList = {
        "X-Content-Type-Options": "nosniff",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Length": "0",
    }

    return headList


# uses the body data to determine the content length
def findContentLength(data, headerList):
    #print(f"data: {data}\nheadlistb4: {headerList}")
    contentLength = str(len(data))
    #print(f"content length: {contentLength}")
    headerList.update({"Content-Length":contentLength})
    #print(f"headlist after: {headerList}")
    return headerList


       
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
        