 

JSON_RPC_VERSION = "2.0"

class ResponseObject(object):
    def __init__(self, result, error, id):
        self.jsonrpc = JSON_RPC_VERSION
        self.result = result
        self.error = error
        seld.id = id
        
        
class RequestObject(object):
    def __init__(self, method, params, id):
        self.jsonrpc = JSON_RPC_VERSION
        self.method = method
        self.params = params
        self.id = id
        
    def __iter__(self):
        for attr, value in self.__dict__.iteritems():
            yield attr, value
        
        
class ErrorObject(object):
    def __init__(self, code, message, data):
        self.code = code
        self.message = message
        self.data = data
		

ErrorObject.errors ={
            -32700 : "Parse Error",
            -32600 : "Invalid Request",
            -32601 : "Method not found",
            -32602 : "Invalid params",
            -32603 : "Internal error",
            -32000 : "Server error"
        }