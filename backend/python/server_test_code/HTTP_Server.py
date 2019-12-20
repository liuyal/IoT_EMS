import time, sys, os, io, copy,  datetime
import http.server, socketserver
from http.server import HTTPServer
import HTTPHandler
import SQL_Module

# https://docs.python.org/3/library/http.html
# https://www.itsecguy.com/custom-web-server-responses-with-python/

def run(HostIP="0.0.0.0", HostPort=8000, handler_class=http.server.SimpleHTTPRequestHandler):
    with socketserver.TCPServer((HostIP, HostPort), handler_class) as httpd:
        print("Server Hosted on: " + HostIP + ":" + str(HostPort))
        httpd.serve_forever()

def runRequestHandler(HostIP="0.0.0.0", HostPort=8000, handler_class=HTTPHandler.RequestHandler):
    print("Server Hosted on: " + HostIP + ":" + str(HostPort))
    server = (HostIP, HostPort)
    httpd = HTTPServer(server, handler_class)
    httpd.serve_forever()

if __name__== "__main__":
    SQL_Module.Test()
    # run()
    runRequestHandler()
