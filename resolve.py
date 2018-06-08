#!/usr/bin/env python

# Produce by Jim Reynolds - jvr1967@gmail.com - May 2018
# Please contact me if you discover a bug or wish to suggest an enhancement

# This command accepts a destination IP address as an argument and determines how packets to this destination will egress the N7K
# The IP interface and the physical interface are resolved since they are not always the same.


from cisco import cli
import sys
import xml.etree.cElementTree as ET

no_of_args = len(sys.argv);

if no_of_args == 1:
        print 'Usage : %s <Destination IP Address>' % str(sys.argv[0])
        exit(0);

ipToResolve = str(sys.argv[1])
DEBUG = 0
if no_of_args == 3:
 DEBUG=1;

#DEBUG = str(sys.argv[2])

def extract_arp_info():
    #cli | xml
        global ipToResolve


        state = 1

        while state > 0:
                if DEBUG == 1:
                        print 'state: %s' % state;
                if state == 4:#Resolve interface to a port
                        print 'Egress Port: %s' % (intf);
                        state = 0


                if state == 3:#Get the interface
                        #Find egress interface for macad (state=1)
                        if "Eth" in ifname:
                                intf = ifname
                                state = 4;
                        if "Vlan" in ifname:
                                intf = resolveMAC(macad);
                                state = 4;
                        print 'Egress Interface: %s' % (ifname);


                if state == 2:
                        #Next-Hop is not the destination. Check the interface
                        macad = resolveARP(ipnexthop)
                        if macad == '0000.0000.0000':
                                #print 'No ARP entry exists'
                                intf = ifname;
                                #Check the IP assigned to the egress interface
                                ipOfe = getIPofInterface(intf);
                                #print 'The NH is asssigned to the egress interf
ace'
                                print 'MAC Address: Assigned to the egress inter
face';
                        else:
                                print 'MAC Address: %s' % (macad);
                        state = 3;

                if state == 1:
                        raw = cli('show ip route ' + ipToResolve + ' | xml | exc
lude "]]>]]>"')

                        # Load and parse XML
                        tree = ET.ElementTree(ET.fromstring(raw))
                        data = tree.getroot()
                        ipnexthop = 'xxx';
                        rib_info = '{http://www.cisco.com/nxos:1.0:urib}'
                        for i in data.iter(rib_info + 'ROW_path'):
                                ipnexthop = i.find(rib_info + 'ipnexthop').text
                                clientname = i.find(rib_info + 'clientname').tex
t
                                ubest = i.find(rib_info + 'ubest').text
                                print 'IP Next-Hop: %s, Source: %s' % (ipnexthop
,clientname);
                                state = 1
                                ipToResolve = ipnexthop
                                if clientname == 'am':
                                        ifname = i.find(rib_info + 'ifname').tex
t
                                        uptime = i.find(rib_info + 'uptime').tex
t
                                        state=2
                                if clientname == 'local':
                                        ifname = i.find(rib_info + 'ifname').tex
t
                                        uptime = i.find(rib_info + 'uptime').tex
t
                                        state=2
                                if clientname == 'hsrp':
                                        ifname = i.find(rib_info + 'ifname').tex
t
                                        uptime = i.find(rib_info + 'uptime').tex
t
                                        state=2

def resolveARP(ipadd):
        rawARP = cli('show ip arp ' + ipadd + ' | xml | exclude "]]>]]>"')
        treeARP = ET.ElementTree(ET.fromstring(rawARP))
        dataARP = treeARP.getroot()
        arpINFO = '{http://www.cisco.com/nxos:1.0:arp}'
        for ia in dataARP.iter(arpINFO + 'ROW_vrf'):
                count = ia.find(arpINFO + 'cnt-total').text
                if count == '0':
                        return '0000.0000.0000'

        mac = '0000.0000.0000'
        arpINFO = '{http://www.cisco.com/nxos:1.0:arp}'
        for ia in dataARP.iter(arpINFO + 'ROW_adj'):
                mac = ia.find(arpINFO + 'mac').text
        return mac;

def resolveMAC(macadd):
        int = 'None';
        rawMAC = cli('show mac add add ' + macadd + ' | xml | exclude "]]>]]>"')

        treeMAC = ET.ElementTree(ET.fromstring(rawMAC))
        dataMAC = treeMAC.getroot()
        macINFO = '{http://www.cisco.com/nxos:1.0:l2fm}'
        for ia in dataMAC.iter(macINFO + 'ROW_mac_address'):
                int = ia.find(macINFO + 'disp_port').text
        return int;

def getIPofInterface(IPintf):
        rawIP = cli('show ip int ' + IPintf + ' | xml | exclude "]]>]]>"')
        treeIP = ET.ElementTree(ET.fromstring(rawIP))
        dataIP = treeIP.getroot()
        ipINFO = '{http://www.cisco.com/nxos:1.0:ip}'
        for X in dataIP.iter(ipINFO + 'ROW_intf'):
                ipa = X.find(ipINFO + 'prefix').text
                return ipa;


def main():
        # Get interface information in XML format
        print
        print 'Resolving Destination'
        print
        #extract urib neighbors info
        extract_arp_info()



if __name__=="__main__":
    sys.exit(main())
