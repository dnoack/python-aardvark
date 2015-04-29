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


import array
import sys
import socket

remoteAddress = ***REMOVED***
remotePort = 1234


from JsonRPCClient import *

class RemoteAardvarkAPI(object):

    def __init__(self, port=0):
        self.rpc = JsonRPCClient(remoteAddress, remotePort)
        
    def __exit__(self):
        self.rpc.close()
        
        
    def getReturnCode(self, value):
        returnCode = find_json_object("result", value)
        return find_json_object("returnCode", returnCode)
        

        
    def py_aa_find_devices(self, num_devices, devices):
        params = {"num_devices" : num_devices}
        response = self.rpc.send_request("Aardvark.aa_find_devices", params)
        val = find_json_object("result", response)
        num_devices = find_json_object("num_devices", val)
        devices = find_json_object("devices", val)
        return num_devices


    def py_aa_open_ext(self, port):
        params = {"port" : port}
        ret = 0
        
        response = self.rpc.send_request("Aardvark.aa_open_ext", params)
        ver = []
        val = find_json_object("result", response)
        ret = find_json_object("Aardvark", val)
        val = find_json_object("AardvarkExt", val)
        val = find_json_object("AardvarkVersionValue", val)
        ver.append(find_json_object("software", val))
        ver.append(find_json_object("firmware", val))
        ver.append(find_json_object("hardware", val))
        ver.append(find_json_object("sw_req_by_fw", val))
        ver.append(find_json_object("fw_req_by_sw", val))
        ver.append(find_json_object("api_req_by_sw", val))
        return ret, ver

        
    def py_aa_close(self, handle):
        """Close the device."""
        params = {"Aardvark" : handle}
        self.rpc.send_request("Aardvark.aa_close", params)
        return None
        
        
    def py_aa_unique_id(self, handle):
        params = {"Aardvark" : handle}
        response = self.rpc.send_request("Aardvark.aa_unique_id", params)
        uniqueId = find_json_object("result", response)
        return uniqueId
        
        
    def py_aa_target_power(self, handle, value):
        params = {"Aardvark" : handle, "powerMask" : value}
        response = self.rpc.send_request("Aardvark.aa_target_power", params)
        return self.getReturnCode(response)
        
        
    def py_aa_i2c_bitrate(self, handle, value):
        params = {"Aardvark" : handle, "bitrate" : value}
        response = self.rpc.send_request("Aardvark.aa_i2c_bitrate", params)
        return self.getReturnCode(response)
    
    
    def py_aa_i2c_slave_enable(self, handle, slave_addr, maxTxBytes, maxRxBytes):
        params = {"Aardvark" : handle, "slave_addr": slave_addr, "maxTxBytes": maxTxBytes, "maxRxBytes": maxRxBytes}
        response = self.rpc.send_request("Aardvark.aa_i2c_slave_enable", params)
        return self.getReturnCode(response)
    
    
    def py_aa_i2c_pullup(self, handle, value):
        params = {"Aardvark" : handle, "pullup_mask": value}
        response = self.rpc.send_request("Aardvark.aa_i2c_pullup", params)
        return self.getReturnCode(response)
        
        
    def py_aa_i2c_write(self, handle, i2c_address, flags, len ,data):
        params = {"Aardvark": handle, "slave_addr" : i2c_address, "AardvarkI2cFlags" : flags, "data_out": data.tolist()}
        response = self.rpc.send_request("Aardvark.aa_i2c_write", params)
        return self.getReturnCode(response)
        
        
    def py_aa_i2c_read(self, handle, addr, flags, length, data):
        params = {"Aardvark": handle, "slave_addr": addr, "AardvarkI2cFlags" : flags, "num_bytes": length}
        response = self.rpc.send_request("Aardvark.aa_i2c_read", params)
        val = find_json_object("result", response)
        returnCode = find_json_object("returnCode", val)
        data2 = find_json_object("data_in", val)
        if(len(data2) <= length):
            for i in range(len(data2)):
                data[i] = data2[i]
        else:
            returnCode = -1
        return returnCode
    
        
    def py_aa_configure(self, handle, value):
        params = {"Aardvark" : handle, "AardvarkConfig" : value}
        response = self.rpc.send_request("Aardvark.aa_configure", params)
        return self.getReturnCode(response)
        
        
    def py_aa_spi_configure(self, handle, polarity, phase, bitorder):
        params = {"Aardvark": handle, "polarity": polarity, "phase": phase, "bitorder": bitorder}
        response = self.rpc.send_request("Aardvark.aa_spi_configure", params)
        return self.getReturnCode(response)
        
        
    def py_aa_spi_bitrate(self, handle, value):
        params = {"Aardvark" : handle, "bitrate" : value}
        response = self.rpc.send_request("Aardvark.aa_spi_bitrate", params)
        return self.getReturnCode(response)
        
        
    def py_aa_async_poll(self, handle, timeout):
        params = {"Aardvark" : handle, "timeout": timeout}
        response = self.rpc.send_request("Aardvark.aa_async_poll", params)
        return self.getReturnCode(response)
        
        
    def py_aa_spi_master_ss_polarity(self, handle, polarity):
        params = {"Aardvark" : handle, "polarity": polarity}
        response = self.rpc.send_request("Aardvark.aa_spi_master_ss_polarity", params)
        return self.getReturnCode(response)
        
        
    def py_aa_spi_write(self, handle, length_out, data_out, length_in, data_in):
        params = {"Aardvark": handle, "num_bytes" : num_bytes, "data_out" : data_out}
        response = self.rpc.send_request("Aardvark.aa_spi_write", params)
        val = find_json_object("result", response)
        data2_in = find_json_object("data_in", val)
        if(len(data2) <= length_in):
            for i in range(length_in):
                data_in[i] = data2[i]
        else:
            returnCode = -1
        return returnCode


from pyaardvark import *
aardvark.api = RemoteAardvarkAPI()
from pyaardvark import open, find_devices
