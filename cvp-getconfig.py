#!/usr/bin/env python
#
#
# Copyright (c) 2020, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Description:
#
# Syntax:
# cvp_getarp -c --cvphost <cvphostname or ip-address>
#            -u --user <username>
#            -p --password <password> If omitted, password will be prompted.
#            -d <EOS device either hostname or ip address, or a list ','separated
#            -v verbose level=1,2, if level-identifier is omitted default=1
#
# Revision Level: 1.0 Date 6/1/2021

#
# Note: For any question of comment: please email ralf-at-arista-dot-com with "cvp-getconfig" in the subject.
#
#============
#
# Functions
#
def verbose_func(level,c_line):
    if level=="1":
        print("\nCVP_GETCONFIG: %s" % (c_line))
    return
#
# Main code
#
import ssl
import json
import sys
import requests
import argparse
import getpass
import urllib3
#
# Init & Argument parsing
#
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#
args = argparse.ArgumentParser()
args.add_argument(
    "-c",
    "--cvphost",
    dest="cvphost",
    action="store",
    required=True,
    help="CVP host name FQDN or IP",
)
args.add_argument(
    "-u",
    "--user",
    dest="user",
    action="store",
    required=True,
    help="CVP username",
)
args.add_argument(
    "-p",
    "--password",
    dest="passwd",
    action="store",
    required=False,
    default="",
    help="<cvpuser> password",
)
args.add_argument(
    "-d",
    "--device",
    dest="targetdev",
    action="store",
    required=False,
    default="ALL",
    help="Target Devices IP(s) or Device hostname(s), -d leaf1[,leaf2]",
)
args.add_argument(
    "-v",
    "--verbose",
    dest="verbose",
    action="store",
    required=False,
    choices=["0","1","2"],
    default="0",
    help="Verbose level 1 or 2",
)
#
# Prepare the arguments
#
opts = args.parse_args()
host = opts.cvphost
user = opts.user
passwd = opts.passwd
targetdevs = opts.targetdev
verbose= opts.verbose
#
# Check if passwd was provided
#
if passwd == "":
    passwd =  getpass.getpass(prompt='CVP Password: ', stream=None)
#
# Check targetip
#
targetlist=targetdevs.split(",")
#
# Prep CVP login
#
cvpIP = "https://"+host
#
headers = { 'Content-Type': 'application/json'}
#
# login API - you will need to login first
# and save the credentials in a cookie
loginURL = "/web/login/authenticate.do"
#
# send login request. If failed errormsg+sys.exit(-1)
#
try:
    response = requests.post(cvpIP+loginURL,json={'userId':user,'password':passwd},headers=headers,verify=False,timeout=5)
except:
    print("CVP-GETCONFIG: HTTPS connection to CVP Host %s failed please check CVP host or IP address" % host)
    sys.exit(-1)
#
cookies = response.cookies
#
# Retrieve all provisioned EOS devices on CVP
# Create a list of dictionaries with: Serials, IP-address, Hostname 
#
url="/cvpservice/inventory/devices?provisioned=true"
try:
    response= requests.get(cvpIP+url,cookies=cookies, verify=False)
except:
    print("CVP-GETCONFIG: CVP Inventory/devices failed status %s " % response)
    sys.exit(-1)
#
if response.status_code!=200:
    if response.status_code==401:
        print("CVP-GETCONFIG: Status code %s from CVP Server %s please check your login credentials" % (response.status_code,host))
    else:
        print("CVP-GETCONFIG: Status code %s from CVP Server %s to retrieve /cvpservice/inventory/devices" % (response.status_code,host))
    sys.exit(-1)
#
# Get the device list and match against the targetdevs
#
Mdevice_list=[]
Tdevice_list=[]
device_list=response.json()
verbose_func(verbose,device_list)
verbose_func(verbose,targetlist)
#
# search for target_device
#
for i in range(len(device_list)):
    device=device_list[i]
    verbose_func(verbose,device)

#
# Compare Device again target_device(s)
#
    for j in range(len(targetlist)):
        TFlag=False
        if device['hostname'].upper()==targetlist[j].upper():
            TFlag=True
        elif device['ipAddress']==targetlist[j]:
            TFlag=True
        if targetdevs.upper()=="ALL":
            TFlag=True
        if TFlag:
#
# Match found either IP or HOSTNAME
#
            verbose_func(verbose,"Match found "+targetlist[j])
            Mdevice_list.append(device['systemMacAddress'])
            Tdevice_list.append(device['hostname'])
#
# Device Dataset and associated tarlet list created
#
verbose_func(verbose,"Mdevice_list "+str(Mdevice_list))
verbose_func(verbose,"Tdevice_list"+str(Tdevice_list))
#
# Now have the serialnumbers why can use the this a SMASH dataset
#
url="/cvpservice/inventory/device/config?netElementId="
#
for i in range(len(Mdevice_list)):
    dataset=Mdevice_list[i]
    try:
        response = requests.get(cvpIP+url+Mdevice_list[i],cookies=cookies, verify=False)
    except:
        print("CVP-GETCONFIG: Config retrival failed for %s connection to CVP Host %s " % (dataset,host))
        sys.exit(-1)
    if response.status_code!=200:
        print("CVP-GETCONFIG: Status code %s from CVP Server %s to retrieve "+url % (response.status_code,host))
        sys.exit(-1)
    verbose_func(verbose,"Device="+Tdevice_list[i]+" config")
    deviceconfig=response.json()
    runningconfig=deviceconfig['output']
    print ("CVP-GETCONFIG: Device config %s retrieved" % Tdevice_list[i])
    f = open(Tdevice_list[i]+"-"+deviceconfig['deviceConfigTimeStamp']+".cvpcfg", "wt")
    a=(f.write(runningconfig))
    f.close   
