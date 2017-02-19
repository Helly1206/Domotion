#import httplib
#import httplib2
#import json
# TRY ...
#conn = httplib.HTTPConnection("localhost",8090) # HTTPSConnection
#conn.request("GET", "/get?tag=Another")
#r1 = conn.getresponse()
#print r1.status, r1.reason
#data1 = r1.read()
#print data1
# json decode string
#data2 = json.loads(data1)
#print data2

#lots to do ......

import requests
#from requests.auth import HTTPBasicAuth #(not required, first eqample will do)

r = requests.get('http://localhost:8090/get?tag=Another') #, auth=('user', 'pass'))
#requests.get('https://api.github.com/user', auth=HTTPBasicAuth('user', 'pass'))
print(r)
print r.status_code
print r.text
print r.json()
#requests.exceptions.ConnectionError

#import httplib2
#h = httplib2.Http()
#h.add_credentials(myname, mypasswd)
#resp, content = h.request("http://localhost:8090/get?tag=Another","GET")
#assert resp.status == 200
#assert resp['content-type'] == 'text/html'
#print(resp)
#print(content)
#resp, content = h.request("http://localhost:8090/get?tag=lamp1","GET")
#assert resp.status == 200
#assert resp['content-type'] == 'text/html'
#print(resp)
#print(content)
#del h
#ConnectionRefusedError

#http.add_credentials(_user, _password)
#    http.authorizations.append(
#        httplib2.BasicAuthentication(
#            (_user, _password),
#            netloc,
#            wms_url,
#            {},
#            None,
#            None,
#            http
#        )
#    )