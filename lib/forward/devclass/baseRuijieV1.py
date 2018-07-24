#!/usr/bin/env python
# coding:utf-8

"""
-----Introduction-----
[Core][forward] Device class for Ruijie.
Author: Cheung Kei-Chuen
"""
import re
from forward.devclass.baseSSHV1 import BASESSHV1
from forward.utils.forwardError import ForwardError


class BASERUIJIE(BASESSHV1):
    """This is a manufacturer of maipu, using the
    SSHV2 version of the protocol, so it is integrated with BASESSHV2 library.
    """

    def __init__(self, *args, **kws):
        """Since the device's host prompt is different from BASESSHV2,
        the basic prompt for the device is overwritten here.
        """
        BASESSHV1.__init__(self, *args, **kws)
        self.basePrompt = r'(>|#.*#|\]|\$|\)) *$'

    def showNtp(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = '''show run |  include  ntp'''
        prompt = {
            "success": "[\s\S]+(>|#|\$){1,}$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("ntp server ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showSnmp(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = '''show run |  include  snmp'''
        prompt = {
            "success": "[\s\S]+(>|#|\$){1,}$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.findall("snmp-server host ([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                             result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showVersion(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show  version"
        prompt = {
            "success": "[\s\S]+(>|#|\$){1,}$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            tmp = re.search("Software version : (.*)", result["content"], flags=re.IGNORECASE)
            if tmp:
                njInfo["content"] = tmp.group(1).strip()
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showVlan(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show  vlan"
        prompt = {
            "success": "[\s\S]+(>|#|\$){1,}$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            currentSection = "vlanName"
            isContinueLine = False
            for _vlanInfo in result["content"].split("\r\n"):
                _vlanInfo = _vlanInfo.strip()
                if re.search("\-\-\-\-", _vlanInfo):
                    continue
                if re.search("^[0-9]", _vlanInfo) and currentSection == "vlanName":
                    isContinueLine = True
                    # Get the line of vlan.
                    lineInfo = {
                        "id": "",
                        "description": "",
                        "status": "",
                        "interface": [],
                        "type": "",
                    }
                    tmp = re.search("([0-9]+)\s+(\S+)\s+(\S+)(.*)", _vlanInfo)
                    if tmp:
                        lineInfo["id"] = tmp.group(1)
                        lineInfo["description"] = tmp.group(2)
                        lineInfo["status"] = tmp.group(3)
                        if tmp.lastindex == 4:
                            lineInfo["interface"] = tmp.group(4).split(", ")
                        njInfo["content"].append(lineInfo)
                elif isContinueLine is True:
                    for _interface in _vlanInfo.split(", "):
                        lineInfo = njInfo["content"].pop()
                        lineInfo["interface"].append(_interface.strip())
                        njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showRoute(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show ip route"
        prompt = {
            "success": "[\s\S]+(>|#|\$){1,}$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            for _interfaceInfo in result["content"].split("\r\n"):
                lineInfo = {
                    "net": "",
                    "mask": "",
                    "metric": "",
                    "via": [{"interface": "", "via": "", "type": ""}],
                    # "via": [],
                }
                tmp = re.search("([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/([0-9]{1,2})", _interfaceInfo)
                if tmp:
                    lineInfo["net"] = tmp.group(1)
                    lineInfo["mask"] = tmp.group(2)
                    via = re.search("via ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", _interfaceInfo)
                    if via:
                        lineInfo["via"][0]["via"] = via.group(1)
                    # Match the route table
                    tmp = re.search("([A-Za-z0-9])\*? +([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/([0-9]{1,2})", _interfaceInfo)
                    if tmp:
                        _type = tmp.group(1)
                        if _type == "C":
                            _type = "connected"
                        elif _type == "S":
                            _type = "static"
                        elif _type == "R":
                            _type = "rip"
                        elif _type == "O":
                            _type = "ospf"
                        elif _type == "K":
                            _type = "kernel"
                        elif _type == "I":
                            _type = "isis"
                        elif _type == "B":
                            _type = "bgp"
                        elif _type == "G":
                            _type == "guard"
                        elif _type == "*":
                            _type = "fib"
                    else:
                        _type = "default"
                    lineInfo["via"][0]["type"] = _type
                    njInfo["content"].append(lineInfo)
            njInfo["status"] = True
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo

    def showInterface(self):
        njInfo = {
            'status': False,
            'content': [],
            'errLog': ''
        }
        cmd = "show interface"
        prompt = {
            "success": "Index\(dec\):[\s\S]+#.*#\$ ?$",
            "error": "Unrecognized[\s\S]+",
        }
        result = self.command(cmd=cmd, prompt=prompt)
        if result["state"] == "success":
            interfacesFullInfo = re.split("========================== ", result["content"])[1::]
            for _interfaceInfo in interfacesFullInfo:
                lineInfo = {"members": [],
                            "interfaceState": "",
                            "speed": "",
                            "type": "",
                            "inputRate": "",
                            "outputRate": "",
                            "crc": ""}
                # Get name of the interface.
                lineInfo['interfaceName'] = _interfaceInfo.split("\r")[0].strip(" ")
        else:
            njInfo["errLog"] = result["errLog"]
        return njInfo