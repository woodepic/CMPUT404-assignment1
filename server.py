#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def send_301_redirect(self, new_location):
        response = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {new_location}\r\n\r\n"
        self.request.sendall(response.encode("utf-8"))

    def sendFile(self, filepath):
        #send the contents of a file back to the web browser user
        #assume the file exists

        #create response for successful http and css files
        response = "HTTP/1.1 200 OK\r\n"
        if filepath.endswith(".css"): response = response + "Content-Type: text/css"
        elif filepath.endswith(".html"): response = response + "Content-Type: text/html"
        response = response + "\r\n\r\n"
        print(f"Response: {repr(response)}")
        
        #read and send file content
        with open(filepath, "rb") as file: response += file.read().decode("utf-8")

        #send the http response to the user
        self.request.sendall(response.encode("utf-8"))
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("\nGot a request of: %s" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))

        #parse & print the request
        lines = self.data.decode("utf-8").split("\n")
        line = lines[0]
        method, path, protocol = line.split()
        requested_file_path = os.path.join("www/", path.lstrip("/"))
        requested_file_path = os.path.realpath(requested_file_path)
        print(f"Method: {method}\nPath: {path}\nRequested File Path: {requested_file_path}\nProtocol: {protocol}")

        #TODO: maybe wrap in "if get request"

        #Check if file exists, and serve it if it does
        try:
            with open(requested_file_path) as file:
                self.sendFile(requested_file_path)

        except FileNotFoundError:
            #return a 404 error
            response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n"
            response += "<html><body><h1>404 Not Found</h1></body></html>" #this will provide an HTML webpage indicating the 404
            self.request.sendall(response.encode("utf-8"))
            
        except IsADirectoryError:
            if not path.endswith("/"):
                print("ATTEMPTING REDIRECT")
                # Redirect to the URL with a trailing slash
                new_location = f"http://{self.server.server_address[0]}:{self.server.server_address[1]}{path}/"
                print(f"NEW LOCATION: {new_location}")
                self.send_301_redirect(new_location)
                return


            #serve the webpage located inside the directory
            #TODO: should I maybe make sure this internal index.html exists?
            index_file = os.path.join(requested_file_path, "index.html")
            self.sendFile(index_file)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
