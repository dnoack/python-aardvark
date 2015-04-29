# Copyright (c) 2015  Kontron Europe GmbH
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


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
  
    def __init__(self, address="127.0.0.1", port= 1234):
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.sock.connect((address,port))
      self.messageId = 0
      self.encoder = JsonParser.Encoder()
      self.decoder = JsonParser.Decoder()
      
    
    def __exit__(self):
      self.sock.close()
      self.sock = None
    
    
    def close(self):
        self.sock.close()
        self.sock = None
      
      
    def send_request(self, methodName, params):
      self.messageId = self.messageId+1
      request = JsonRpcMsg.RequestObject(methodName, params, self.messageId)
      encodedRequest = self.encoder.default(request)
      ret = self.sock.send(encodedRequest)
      if(ret < 0):
        print "Could not send data over socket"
      encodedResponse = self.sock.recv(RECV_SIZE_MAX)
      
      response = self.decoder.default(encodedResponse)
      return response
      