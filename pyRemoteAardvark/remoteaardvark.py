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

from JsonRPCClient import *

class RemoteAardvark(object):

    def __init__(self, port=0, remote=False):
        self.rpc = JsonRPCClient()


    def find_devices(self, num_devices):
        params = {"num_devices" : num_devices}
        response = self.rpc.send_request("Aardvark.aa_find_devices", params)
        val = find_json_object("result", response)
        num_devices = find_json_object("num_devices", val)
        devices = find_json_object("devices", val)
        return num_devices, devices


    def open_ext(self, port):
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

    def close(self, handle):
        """Close the device."""
        params = {"Aardvark" : handle}
        self.rpc.send_request("Aardvark.aa_close", params)
        return None
        
    def unique_id(self, handle):
        params = {"Aardvark" : handle}
        response = self.rpc.send_request("Aardvark.aa_unique_id", params)
        uniqueId = find_json_object("result", response)
        return uniqueId
        
    def i2c_bitrate(self, handle, value):
        params = {"Aardvark" : handle, "bitrate" : value}
        response = self.rpc.send_request("Aardvark.aa_i2c_bitrate", params)
        returnCode = find_json_object("result", response)
        returnCode = find_json_object("returnCode", returnCode)
        return returnCode
        
    def spi_bitrate(self, handle, value):
        params = {"Aardvark" : handle, "bitrate" : value}
        response = self.rpc.send_request("Aardvark.aa_spi_bitrate", params)
        returnCode = find_json_object("result", response)
        returnCode = find_json_object("returnCode", returnCode)
        return returnCode
        
        
