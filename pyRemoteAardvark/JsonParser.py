 
from json import *
import collections


class Encoder(JSONEncoder):
    def __init__(self):
        JSONEncoder.__init__(self, encoding="UTF-8")
        
    def default(self, msg):
        return self.encode(dict(msg))
        
        
class Decoder(JSONDecoder):
    def __init__(self):
        JSONDecoder.__init__(self,  object_pairs_hook=collections.OrderedDict)
    
    def default(self, msg):
        return self.decode(msg)
