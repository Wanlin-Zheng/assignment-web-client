#!/usr/bin/env python3
# coding: utf-8
# Copyright [2023] [Wanlin Zheng]

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):

        data = data.split()
        return int(data[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        data = data.split("\r\n\r\n")
        return data[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        parsed_url = urllib.parse.urlparse(url)

        # try to connect to port if not, return error code 404
        try:
            if (parsed_url.port == None):
                self.connect(parsed_url.hostname, 80)
            else:
                self.connect(parsed_url.hostname, parsed_url.port)
        except Exception as e:
            print(e)
            print("-------------------------HERE IS THE CONNECTION ERROR----------------------------------\n")
            print("CONNECTION FAILED")
            print(parsed_url.hostname)
            print(parsed_url.port)
            print("-----------------------------------------------------------\n")
            return HTTPResponse(code, body)

        msg = ""
        if (parsed_url.path == ""):
            msg = "GET / HTTP/1.1\r\n"
        else:
            msg = "GET " + parsed_url.path +" HTTP/1.1\r\n"
        host_header = "Host: " + parsed_url.hostname + "\r\nAccept: text/html,application/json,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
        accept_language_header = "Accept-Language: en-US,en;q=0.5\r\n"
        accept_encoding_header =  "Accept-Encoding: gzip, deflate\r\n"
        content_type_header = "Content-Tpye: application/json\r\n"
        connnection_header = "Connection: close\r\n\r\n"
        header = host_header + content_type_header +  accept_language_header + accept_encoding_header + connnection_header

        # print("----------------------------HERES THE sent requests-------------------------------\n"
        #       + msg + header
        #       +"-----------------------------------------------------------\n" )

        self.sendall(msg + header)
        returnData = self.recvall(self.socket)
        print("----------------------------HERE IS THE RECIEVED DATA-------------------------------\n"
              + returnData
              +"-----------------------------------------------------------\n" )
        

        code = self.get_code(returnData)
        body = self.get_body(returnData)

        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        parsed_url = urllib.parse.urlparse(url)

         # try to connect to port if not, return error code 404
        try:
            if (parsed_url.port == None):
                self.connect(parsed_url.hostname, 80)
            else:
                self.connect(parsed_url.hostname, parsed_url.port)
        except Exception as e:
            print(e)
            print("-------------------------ERROR WITH CONNECTION----------------------------------\n")
            print("CONNECTION FAILED")
            print(parsed_url.hostname)
            print(parsed_url.port)
            print("-----------------------------------------------------------\n")
            return HTTPResponse(code, body)
        
        msg = "POST " + parsed_url.path +" HTTP/1.1\r\n"
        host_header = "Host: " + parsed_url.hostname + "\r\n"
        accept_header = "Accept: text/html, application/json, application/xhtml+xml\r\n"

        # parse args into a string
        parsed_args = ""

        if args:
            for key in args: 
                parsed_args = parsed_args + key + "=" + args[key] + "&"
            # remove last &
            if (parsed_args != ""):
                parsed_args = parsed_args[:-1]

        # get content-lenght
        byte_count = len(parsed_args.encode("utf-8"))
        content_type_header = "Content-Tpye: application/json\r\n"
        content_count_header = "Content-Length: " + str(byte_count) + "\r\n"
        connnection_header = "Connection: keep-alive\r\n\r\n"
        header = host_header + accept_header + content_type_header + content_count_header + connnection_header

        # print("----------------------------HERES THE sent requests-------------------------------\n"
        #       + msg + header + parsed_args
        #       +"-----------------------------------------------------------\n" )
        self.sendall(msg + header + parsed_args)


        returnData = self.recvall(self.socket)
        print("----------------------------HERES THE RETURN-------------------------------\n"
              + returnData
              +"-----------------------------------------------------------\n" )
        
        if returnData:
            code = self.get_code(returnData)
            body = self.get_body(returnData)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
