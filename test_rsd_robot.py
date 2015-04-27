
import socket, time


for i in range (1):

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((***REMOVED***,1234))

  
  print "Requesting plugin list"
  s.send("{\"jsonrpc\": \"2.0\", \"method\": \"RSD.showAllRegisteredPlugins\", \"params\" : { \"nothing\": 0 }, \"id\" : 95}")
  data = s.recv(1024)
  print 'Received', repr(data)


  print "Requesting function list"
  s.send("{\"jsonrpc\": \"2.0\", \"method\": \"RSD.showAllKownFunctions\", \"params\" : { \"nothing\": 0 }, \"id\" : 96}")
  data = s.recv(1024)
  print 'Received', repr(data)
  
  # Requesting device list
  print "Find devices"
  s.send("{\"jsonrpc\": \"2.0\", \"method\": \"Aardvark.aa_find_devices\", \"params\" : { \"num_devices\": 5  }, \"id\" : 97}")
  data = s.recv(1024)
  print 'Received', repr(data)
  
  print "Find devices ext"
  s.send("{\"jsonrpc\": \"2.0\", \"method\": \"Aardvark.aa_find_devices_ext\", \"params\" : { \"num_devices\": 5  }, \"id\" : 98}")
  data = s.recv(1024)
  print 'Received', repr(data)

  s.close()