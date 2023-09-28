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
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))

        #parse the request
        lines = self.data.decode("utf-8").split("\n")
        line = lines[0]
        method, path, protocol = line.split()
        requested_file_path = os.path.join("www/", path.lstrip("/"))
        requested_file_path = os.path.realpath(requested_file_path)
        print(f"Method: {method}\nPath: {path}\nRequested File Path: {requested_file_path}\nProtocol: {protocol}\n")

        #maybe wrap in "if get request"

        #Check if file exists, and serve it if it does
        try:
            with open(requested_file_path) as file:
                #serve the file
                #self.serveFile(file, requested_file_path)
                pass
        except FileNotFoundError:
            #return a 404 error
            pass
        except IsADirectoryError:
            #serve the webpage
            index_file = os.path.join(requested_file_path, "index.html")
            #if exists:
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
            # Read and send the index.html file content
            with open(index_file, "rb") as file:
                response += file.read().decode("utf-8")
            self.request.sendall(response.encode("utf-8"))
            return



        #interpret the request, decide what to serve (could be a file, response code, (webpage?))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8081 #TODO: Fix this

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
