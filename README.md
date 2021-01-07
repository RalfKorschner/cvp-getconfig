# cvp-getconfig Python Script

Even though this script is best effort supported, please send any issues you find, suggestions for improvements etc to: [ralf@arista.com](mailto:ralf@arista.com).  Please use the subject: **CVP GETCONFIG**

This tool can be used to retrieve the EOS device config from CVP.

Tested with CVP Versions 2020.2.3

Below is an explanation of all command line options to `cvp-getconfig.py`:

```
  -h --help            show this help message and exit
  -c CVPHOST, --cvphost CVPHOST
                        CVP host name FQDN or IP
  -u USER, --user USER  CVP username
  -p PASSWD, --password PASSWD
                        <cvpuser> password
  -d TARGETDEV, --device TARGETDEV
                        Target Devices IP(s) or Device hostname(s), -d
                        leaf1[,leaf2]
  -v {1,2}, --verbose {1,2}
                        Verbose level 1 or 2 (just for debugging purposes)


```

Thx, Ralf Korschner, Systems Engineer Arista Networks


 
