#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
# Derived & referenced to Emalsha G.H.B. Link: https://emalsha.wordpress.com/2016/11/24/how-create-http-server-using-python-socket-part-ii/ 
class HTTPClient(object):
    def get_host_port(self, urllibObj):
        if (urllibObj.port == None and urllibObj.scheme == "http"):
            return urllibObj.hostname, 80
        elif (urllibObj.port == None and urllibObj.scheme == "https"):
            return urllibObj.hostname, 443
        else:
            return urllibObj.hostname, urllibObj.port

    def get_path(self, urllibObj):
        if urllibObj.path:
            return urllibObj.path
        else:
            return "/"

    # Derived & referenced to Python documentation. Link: https://docs.python.org/3/library/urllib.parse.html
    def urllib_obj(self, url):
        return urllib.parse.urlparse(url)

    def get_request(self, path, host):
        return f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nAccept: */*\r\nAccept-Charset: UTF-8\r\n\r\n" 
    
    def post_request(self, path, host, length, query):
        return f"POST {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {length}\r\nConnection: close\r\n\r\n{query}\r\n" 

    def get_url_encoded(self, args):
        return urllib.parse.urlencode(args) if args != None else urllib.parse.urlencode('')

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]
    
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
        return buffer.decode(encoding='utf-8', errors="ignore")

    def GET(self, url, args=None):
        code = 500
        body = ""
        urllibObj = self.urllib_obj(url)

        target_host, target_port = self.get_host_port(urllibObj)
        target_path = self.get_path(urllibObj)
        self.connect(target_host, target_port)  
        self.sendall(self.get_request(target_path, target_host))
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        header = self.get_headers(response)
        
        # Print output 
        print(code)
        print(header)
        print(body)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        urllibObj = self.urllib_obj(url)
        
        target_host, target_port = self.get_host_port(urllibObj)
        target_path = self.get_path(urllibObj)
        request_query = self.get_url_encoded(args)
        request_query_length = len(request_query.encode('utf-8'))        
        self.connect(target_host, target_port)
        self.sendall(self.post_request(target_path, target_host, request_query_length, request_query))
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        header = self.get_headers(response)

        # Print output 
        print(code)
        print(header)
        print(body)
        
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
