import time, sys, os

import http.server, socketserver
import HTTPHandler
import SQL_Module





# https://docs.python.org/3/library/http.html
def run(HostIP="0.0.0.0", HostPort=8000, handler_class=HTTPHandler.SimpleHTTPRequestHandler):
    with socketserver.TCPServer((HostIP, HostPort), handler_class) as httpd:
        print("Server Hosted on: " + HostIP + ":" + str(HostPort))
        httpd.serve_forever()



if __name__== "__main__":
    SQL_Module.Test()
    run()
