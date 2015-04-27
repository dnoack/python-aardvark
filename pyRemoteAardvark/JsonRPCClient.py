import socket
import json
import JsonParser
import JsonRpcMsg

RECV_SIZE_MAX = 2048

  
def find_json_object(objectName, jsonMsg):
  if(objectName in jsonMsg):
    retValue = jsonMsg[objectName]
  else:
    raise KeyError(val)
  return retValue
  

class JsonRPCClient(object):
  
    def __init__(self, address=***REMOVED***, port= 1234):
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.sock.connect((address,port))
      self.messageId = 0
      self.encoder = JsonParser.Encoder()
      self.decoder = JsonParser.Decoder()
      
    
    def __exit__(self):
      self.sock.close()
      self.sock = None
      
      
    def send_request(self, methodName, params):
      self.messageId = self.messageId+1
      request = JsonRpcMsg.RequestObject(methodName, params, self.messageId)
      encodedRequest = self.encoder.default(request)
      self.sock.send(encodedRequest)
      encodedResponse = self.sock.recv(RECV_SIZE_MAX)
      
      response = self.decoder.default(encodedResponse)
      return response
      
      
"""     
test = JsonRPCClient("127.0.0.1", 1234)

params = {"port" : 0}
msg =test.send_request("Aardvark.aa_open", params)

if("result" in msg):
  if("Aardvark" in msg["result"]):
    params = {"Aardvark" : msg["result"]["Aardvark"]}
    test.send_request("Aardvark.aa_close", params)
"""