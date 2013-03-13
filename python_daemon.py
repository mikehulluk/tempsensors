from wsgiref.simple_server import make_server
import json

with open('test1.html') as f:
    index_html = f.read()

def serve_index(environ, start_response):
    
   status = '200 OK'
   response_headers = [
                  ('Access-Control-Allow-Origin', '*'),
                  ('Content-Type', 'text/html'),
                  ('Content-Length', str(len(index_html)))
                  ]
   start_response(status, response_headers)
   return [index_html]


def serve_ajax(environ, start_response):
   result = [{"name":"John Johnson","street":"Oslo West 555","age":33}]
   response_body = json.dumps(result)
   status = '200 OK'
   response_headers = [
                  ('Access-Control-Allow-Origin', '*'),
                  ('Content-Type', 'text/plain'),
                  ('Content-Length', str(len(response_body)))
                  ]
   start_response(status, response_headers)
   return [response_body]



def application(environ, start_response):
   if environ['PATH_INFO'] == '/':
       return serve_index(environ, start_response)
   elif environ['PATH_INFO'] == '/ajax/new_data/':
       return serve_ajax(environ, start_response)
   else:
       assert False
       
   print environ 



httpd = make_server('localhost',8051, application)

httpd.serve_forever()

httpd.handle_request()
