# HSRP + ACL + NAT Lab

In modern-day computer networking, High Availability (HA) is critical to ensuring continuous service during downtime, glitches, or failures. To do this, we need to be able to add redundancy to a system on every level: power, data, geographic, and pathway. This includes load balancing, data redundancy, failover mechanisms, and a flexible routing design. 

In this lab, I'll focus on three key technologies: HSRP, ACLs, and NAT. These protocols contribute to a resilient and secure network design. They provide gateway redundancy, enforce access control based on IP addresses, and enable private networks to communicate with external resources.

Here is the step-by-step we're going to go over in this lab:
1. **Initial Setup**
2. **VLANs**
3. **IP Addresses + Static Routes (IPv4/IPv6)**
4. **OSPF Configuration (OSPFv2 + OSPFv3)**
5. **HSRP (IPv4/IPv6)**
6. **Extended ACLs (IPv4/IPv6)**
7. **NAT Overload (PAT) Configuration**
8. **Endpoint Configuration**

Let's take a look at how these protocols ensure an HA design.

### **Part 1: Initial Setup**

To set up this lab, I wanted to add an initial setup when it comes to assigning hostnames and making sure there weren't any interruptions to console configurations through CML. For this, I wanted:
- Hostnames set
- Avoid delays if mistyping a command
- Add a new line if system messages occur

R1:
```bash
conf t
!
hostname R1
!
no ip domain-lookup
!
line console 0
 logging synchronous
exit
!
do wr
end
```

R2:
```bash
conf t
!
hostname R2
!
no ip domain-lookup
!
line console 0
 logging synchronous
exit
!
do wr
end
```

ISP:
```bash
conf t
!
hostname ISP
!
no ip domain-lookup
!
line console 0
 logging synchronous
exit
!
do wr
end
```

SW1:
```bash
conf t
!
hostname SW1
!
no ip domain-lookup
!
line console 0
 logging synchronous
exit
!
do wr
end
```

SW2
```bash
conf t
!
hostname SW2
!
no ip domain-lookup
!
line console 0
 logging synchronous
exit
!
do wr
end
```
Command Breakdown:
* `hostname`: Assigns a hostname to a device.
* `no ip domain-lookup`: Prevents a device from trying to resolve a mistyped command as a hostname.
* `logging synchronous`: Stops system messages from interrupting CLI command input.

**Verify**

```bash
show running-config
```

With this very simple setup completed, we should be all good to continue with setting up the VLANs for this lab.

### **Part 2: VLANs**

Next, we'll need to have switches in our topology that our hosts can connect to, as well as logically segment our LAN into separate broadcast domains. To do this, I created VLAN10 for the Marketing department and VLAN20 for the IT department in our enterprise network. I did this because it would make it easier to implement HSRP, ACLs, and NAT when working with VLANs, as well as segmenting the network.

A few caveats about this topology are that I didn't use:
1. **Trunk Connections**
2. **ROAS (Router on a Stick)**
3. **SVI (Switch Virtual Interfaces)**

I only have access switchports on the interfaces between the hosts and the uplink routers. I mainly did this to make the topology easier, as well as focus on the HSRP, ACLs, and NAT of this lab. Typically, you'd want VLANs to be routable across your entire network, thus having multiple VLANs on trunk links.

SW1:
```bash
conf t
!
vlan 10
 name MARKETING
exit
!
int gi0/0
 switchport mode access
 switchport access vlan 10
exit
!
int gi0/1
 switchport mode access
 switchport access vlan 10
exit
!
int gi0/2
 switchport mode access
 switchport access vlan 10
exit
!
int gi0/3
 switchport mode access
 switchport access vlan 10
exit
!
do wr
end
```

SW2:
```bash
conf t
!
vlan 20
 name IT
exit
!
int gi0/0
 switchport mode access
 switchport access vlan 20
exit
!
int gi0/1
 switchport mode access
 switchport access vlan 20
exit
!
int gi0/2
 switchport mode access
 switchport access vlan 20
exit
!
int gi0/3
 switchport mode access
 switchport access vlan 20
exit
!
do wr
end
```
Command Breakdown:
* `switchport mode access`: Sets the interface as an access port.
* `switchport access vlan XX`: Sets the VLAN associated with the access port.

**Verify**
```bash
show vlan brief
show vlans
```

With that, our Layer 2 configuration is complete! Let's now move on to the IP addressing and static routing of this lab.

### **Part 3: IP Addresses + Static Routes (IPv4/IPv6)**

Similar to my last lab [Lab 1. OSPF + BGP](https://github.com/danieljlepiscopo/cml_labs/tree/main/lab1-ospf-bgp), utilizing both IPv4 and IPv6 on each of the interfaces, is a modern approach to networking with dual-stack IP configuration. Making sure that we enable IPv6 routing, as well as configuring static default routes to the ISP router. 

R1:
```bash
conf t
!
ipv6 unicast-routing
!
ip route 0.0.0.0 0.0.0.0 100.0.0.1
!
ipv6 route ::/0 GigabitEthernet0/0 fd00:100::1
!
int lo0
 ip address 1.1.1.1 255.255.255.255
 ipv6 address fd00:1::1/128
exit
!
int gi0/0
 ip address 100.0.0.2 255.255.255.252
 ipv6 address fd00:100::2/64
 ipv6 enable
 no shut
 description Connection to ISP
exit
!
int gi0/1
 ip address 12.0.0.1 255.255.255.252
 ipv6 address fd00:12::1/64
 ipv6 enable
 no shut
 description Connection to R2
exit
!
int gi0/2
 ip address 10.10.10.2 255.255.255.0
 ipv6 address fd00:10::2/64
 ipv6 enable
 no shut
 description Connection to SW1
exit
!
int gi0/3
 ip address 10.20.20.3 255.255.255.0
 ipv6 address fd00:20::3/64
 ipv6 enable
 no shut
 description Connection to SW2
exit
!
do wr
end
```

R2:
```bash
conf t
!
ipv6 unicast-routing
!
ip route 0.0.0.0 0.0.0.0 100.1.0.1
!
ipv6 route ::/0 GigabitEthernet0/0 fd00:101::1
!
int lo0
 ip address 2.2.2.2 255.255.255.255
 ipv6 address fd00:2::1/128
exit
!
int gi0/0
 ip address 100.0.1.2 255.255.255.252
 ipv6 address fd00:101::2/64
 ipv6 enable
 no shut
 description Connection to ISP
exit
!
int gi0/1
 ip address 12.0.0.2 255.255.255.252
 ipv6 address fd00:12::2/64
 ipv6 enable
 no shut
 description Connection to R1
exit
!
int gi0/2
 ip address 10.20.20.2 255.255.255.0
 ipv6 address fd00:20::2/64
 ipv6 enable
 no shut
 description Connection to SW2
exit
!
int gi0/3
 ip address 10.10.10.3 255.255.255.0
 ipv6 address fd00:10::3/64
 ipv6 enable
 no shut
 description Connection to SW1
exit
!
do wr
end
```

#ISP
```bash
conf t
!
ipv6 unicast-routing
!
ip route 10.10.10.0 255.255.255.0 100.0.0.2
ip route 10.20.20.0 255.255.255.0 100.1.0.2
!
ipv6 route fd00:10::1/64 GigabitEthernet0/0 fd00:100::2
ipv6 route fd00:20::1/64 GigabitEthernet0/0 fd00:101::2
!
int lo0
 ip address 3.3.3.3 255.255.255.255
 ipv6 address fd00:3::1/128
exit
!
int gi0/0
 ip address 100.0.0.1 255.255.255.252
 ipv6 address fd00:100::1/64
 ipv6 enable
 no shut
 description Connection to R1
exit
!
int gi0/1
 ip address 100.0.1.1 255.255.255.252
 ipv6 address fd00:101::1/64
 ipv6 enable
 no shut
 description Connection to R2
exit
!
int gi0/2
 description Not in Use
exit
!
int gi0/3
 description Not in Use
exit
!
do wr
end
```

**Verify**
```bash
show ip interface brief
show running-config
show ip route
show ipv6 route
```

All of the IP addresses have now been configured on all of the interfaces and the loopbacks. Let's continue and move on to Configuring OSPF as well.

### **Part 4: OSPF Configuration (OSPFv2 + OSPFv3)**

Moving on to OSPF (Open Shortest Path First), I decided to simulate a more realistic enterprise environment where dynamic routing typically would be placed. I could have just added static routes between R1/R2 to not take away from HSRP, ACLs, and NAT in this lab; however, the inclusion of OSPF reflects how HSRP and IGPs typically coexist in production networks. 

With the inclusion of OSPFv2 and OSPFv3, I've dual-stacked IPv4/IPv6 in this lab to create a more modern production environment as well.

Let's take a look at it:

R1:
```bash
conf t
!
router ospf 1
 router-id 1.1.1.1
 log-adjacency-changes
 passive-interface default
 no passive-interface g0/1
exit
!
ipv6 router ospf 1
 router-id 1.1.1.1
 log-adjacency-changes
 passive-interface default
 no passive-interface g0/1
exit
!
int lo0
 ip ospf 1 area 0
 ipv6 ospf 1 area 0
exit
!
int gi0/1
 ip ospf 1 area 0
 ipv6 ospf 1 area 0
exit
!
do wr
end
```

R2:
```bash
conf t
!
router ospf 1
 router-id 2.2.2.2
 log-adjacency-changes
 passive-interface default
 no passive-interface g0/1
exit
!
ipv6 router ospf 1
 router-id 2.2.2.2
 log-adjacency-changes
 passive-interface default
 no passive-interface g0/1
exit
!
int lo0
 ip ospf 1 area 0
 ipv6 ospf 1 area 0
exit
!
int gi0/1
 ip ospf 1 area 0
 ipv6 ospf 1 area 0
exit
!
do wr
end
```
Command Breakdown:
* `router ospf 1`: Enables OSPFv2 on process-id 1.
* `ipv6 router ospf 1`: Enables OSPFv3 on process-id 1.
* `passive-interface default`: Stops Hello messages from being sent to networks where no neighbors exist.
* `ip ospf 1 area 0`: Enables OSPFv2 on an interface with process-id 1 in backbone area 0.
* `ipv6 ospf 1 area 0`: Enables OSPFv3 on an interface with process-id 1 in backbone area 0.
* `ip ospf network point-to-point`: Stops DR/DBR elections on P2P OSPF connections.

**Verify**
```bash
show ip protocols
show ip ospf database
show ip ospf neighbor
show ip ospf interface brief
show ipv6 ospf neighbor
```

OSPF (both OSPFv2 and OSPFv3) is now properly configured between R1/R2's G0/1 interface. With that now completed, let's move on to configuring HSRP.

### **Part 5: HSRP (IPv4/IPv6)**

HSRP (Hot Standby Routing Protocol) is a Cisco proprietary FHRP (First Hop Redundancy Protocol) that allows for gateway redundancy for hosts connected to the network. If, for instance, R1 went down (network or hardware failure occurs), hosts that have R1 as their default gateway would lose access to the internet. To prevent this from happening, HSRP allows us to configure an 'Active' and 'Standby' router, where hosts are dynamically connected to the active router. If R1 went down as the active router and R2 was the standby router, R2 would take R1's place as the active router. This allows for an HA design where hosts should always have a connection to the internet without disruptions. 

HSRP version 2 allows us to configure both IPv4/IPv6 on routers, setting even more redundancy across the network layer (layer 3) of our network. We can also set preemption and priorities on our routers so they know which router is the 'Active' and 'Standby' router, as well as resetting the active/standby status dynamically if R1 comes back from being offline.

Let's take a look at the configuration for each:

**VLAN10**

R1 (Active):
```bash
conf t
!
int gi0/2
 standby version 2
 standby 10 ip 10.10.10.1
 standby 10 priority 110
 standby 10 preempt
 standby 110 ipv6 fd00:10::1/64
 standby 110 priority 110
 standby 110 preempt
exit
!
do wr
end
```

R2 (Standby):
```bash
conf t
!
int gi0/3
 standby version 2
 standby 10 ip 10.10.10.1
 standby 110 ipv6 fd00:10::1/64
exit
!
do wr
end
```

**VLAN20**

R1 (Standby):
```bash
conf t
!
int gi0/3
 standby version 2
 standby 20 ip 10.20.20.1
 standby 120 ipv6 fd00:20::1/64
exit
!
do wr
end
```

R2 (Active):
```bash
conf t
!
int gi0/2
 standby version 2
 standby 20 ip 10.20.20.1
 standby 20 priority 110
 standby 20 preempt
 standby 120 ipv6 fd00:20::1/64
 standby 120 priority 110
 standby 120 preempt
exit
!
do wr
end
```
Command Breakdown:
* `standby version 2`: Supports IPv6 and increases the number of HSRP groups (from 256 - 4096).
* `standby XX ip X.X.X.X`: Sets the virtual IPv4 address for the group.
* `standby XX ipv6 XX:XX::X/XX`: Sets the virtual IPv6 address for the group. 
* `standby XX priority XX`: Sets the priority of the group; the higher the priority is, the higher they're preferred (default 100).
* `standby XX preempt`: Allows the router with the higher priority to immediately take over as the active router.

**Verify**
```bash
show standby
show hsrp
```

With HSRP now functional between R1 and R2 (both IPv4/IPv6), our FHRP is now set for this lab and our hosts in our enterprise network. Next, let's take a look at ACLs.

### **Part 6: Extended ACLs**

When it comes to ACLs, there are a couple of different configuration standards we can choose:
1. **Standard IPv4 ACLs**
2. **Named ACLs**
3. **Extended ACLs**

In most modern production networks, Extended ACLs are the current approach to configuring both IPv4/IPv6 ACLs, allowing for more descriptive Access Control Entries (ACEs). You can example multiple fields within the packet header, matching every parameter of a packet that the ACL can consider in an ACE match, making them significantly more granular. 

Let's take a look at one now:

R1:
```bash
conf t
!
ip access-list extended VLAN20_ADMIN
 permit ip host 10.20.20.11 host 10.20.20.12
 deny ip 10.10.10.0 0.0.0.255 host 10.20.20.12
 permit ip any any
exit
!
ipv6 access-list VLAN20_ADMIN_V6
 permit ipv6 host fd00:20::11 host fd00:20::12
 deny ipv6 fd00:10::/64 host fd00:20::12
 permit ipv6 any any
!
int gi0/2
 ip access-group VLAN20_ADMIN in
 ipv6 traffic-filter VLAN20_ADMIN_V6 in
exit
!
do wr
end
```
Command Breakdown:
* `ip access-list extended VLAN20_ADMIN`: Starts the extended ACL configuration by naming it `VLAN20_ADMIN`.
* `permit ip host 10.20.20.11 host 10.20.20.12`: Allows IP `10.20.20.11` to access host `10.20.20.12`.
* `permit ipv6 host fd00:20::11 host fd00:20::12`: Allows IPv6 `fd00:20::11` to access host `fd00:20::12`.
* `deny ip 10.10.10.0 0.0.0.255 host 10.20.20.12`: Denies IPs within the `10.10.10.0/24` range to access host `10.20.20.12`.
* `deny ipv6 fd00:10::/64 host fd00:20::12`: Denies IPv6 IPs within the `fd00:10::/64` range to access host `fd00:20::12`.
* `permit ip any any`: Explicitly allows all other IP traffic.
* `ip access-group VLAN20_ADMIN in`: Applies this ACL to the IPv4 traffic going into interface Gi0/2 on R1.
* `ipv6 traffic-filter VLAN20_ADMIN_V6 in`: Applies this ACL to the IPv6 traffic going into interface Gi0/2 on R1.

**Verify**
PC1/PC2:
```bash
ping 10.20.20.12
ping -6 fd00:20::12
ping 10.20.20.11
ping -6 fd00:20::11
```

R1:
```bash
clear access-list counters
show access-lists
show ip interface GigabitEthernet0/2
```

Once we've verified that pings result in 100% packet loss from PC1/PC2, as well as incrementing matches for denying the IPv4/IPv6 of SVR1 on R1, we should be all set! We've successfully blocked VLAN10 hosts from accessing the IT department's server. Up next is our NAT configuration for internet accessibility.

### **Part 7: NAT Overload (PAT) Configuration**

NAT (Network Address Translation) was invented in the 1990s to help conserve IPv4 addresses, since IPv4 was starting to run out. Because of this, NAT itself has a couple of different configurations that can be utilized:
1. **Static NAT**
2. **Dynamic NAT**
3. **NAT Overload (PAT)**

Static NAT and Dynamic NAT don't technically conserve IP addresses; however, NAT Overload (PAT) (Port Address Translation) has a one-to-many mapping. Meaning we only need one public IP address to create an unlimited number of private IP addresses in our own network. 

Let's take a look at how NAT Overload is configured:

R1:
```bash
conf t
!
int gi0/0
 ip nat outside
exit
!
int gi0/1
 ip nat inside
exit
!
int gi0/2
 ip nat inside
exit
!
int gi0/3
 ip nat inside
exit
!
access-list 1 permit 10.10.10.0 0.0.0.255
access-list 1 permit 10.20.20.0 0.0.0.255
!
ip nat inside source list 1 interface GigabitEthernet0/0 overload
!
do wr
end
```

R2:
```bash
conf t
!
int gi0/0
 ip nat outside
exit
!
int gi0/1
 ip nat inside
exit
!
int gi0/2
 ip nat inside
exit
!
int gi0/3
 ip nat inside
exit
!
access-list 1 permit 10.10.10.0 0.0.0.255
access-list 1 permit 10.20.20.0 0.0.0.255
!
ip nat inside source list 1 interface GigabitEthernet0/0 overload
!
do wr
end
```
Command Breakdown:
* `ip nat outside`: Marks Gi0/0 as the outside (public) interface.
* `ip nat inside`: Marks Gi0/1, Gi0/2, and Gi0/3 as the inside (private) interfaces.
* `access-list 1 permit X.X.X.X X.X.X.X`: Permits the addresses that are allowed to use the public IP address(s).
* `ip nat inside source list 1 interface GigabitEthernet0/0 overload`: Using ACL 1, tell R1/R2 that the interface of Gi0/0 will be "overloaded" to enable NAT Overload (PAT).

Verify
```bash
show ip route
show ip nat translations
show ip nat statistics
```

With NAT Overload (PAT) now configured on our lab, our enterprise can now have access to the ISP router with the "public" IP address of this lab. To close out this lab, let's next configure the end hosts.

### **Part 8: Endpoint Configuration**

Lastly, configuring our endpoints correctly with both IPv4/IPv6 configurations as well as their default gateways, so HSRP, ACLs, and NAT all work appropriately. Without our endpoints being configured correctly, everything else in this lab wouldn't work the way it should. 

Let's take a look at the configuration for each of our end hosts in this lab:

PC1:
```bash
sudo hostname PC1
sudo ifconfig eth0 10.10.10.11 netmask 255.255.255.0
sudo ifconfig eth0 add fd00:10::11/64
sudo route add default gw 10.10.10.1 eth0
sudo ip -6 route add default via fd00:10::1
```

PC2:
```bash
sudo hostname PC2
sudo ifconfig eth0 10.10.10.12 netmask 255.255.255.0
sudo ifconfig eth0 add fd00:10::12/64
sudo route add default gw 10.10.10.1 eth0
sudo ip -6 route add default via fd00:10::1
```

PC3:
```bash
sudo hostname PC3
sudo ifconfig eth0 10.20.20.11 netmask 255.255.255.0
sudo ifconfig eth0 add fd00:20::11/64
sudo route add default gw 10.20.20.1 eth0
sudo ip -6 route add default via fd00:20::1
```

SVR1:
```bash
sudo hostname SVR1
sudo ifconfig eth0 10.20.20.12 netmask 255.255.255.0
sudo ifconfig eth0 add fd00:20::12/64
sudo route add default gw 10.20.20.1 eth0
sudo ip -6 route add default via fd00:20::1
```
Command Breakdown:
* `sudo ifconfig eth0 X.X.X.X netmask X.X.X.X`: Sets the IPv4 address of the end host.
* `sudo ifconfig eth0 add XX:XX::X/XX`: Sets the IPv6 address of the end host.
* `sudo route add default gw X.X.X.X eth0`: Sets the IPv4 default-gateway.
* `sudo ip -6 route add default via XX:XX::X`: Sets the IPv6 default-gateway.

### **Wrap-Up**
With our HSRP, ACLs, and NAT lab now done, it tells a story of how HA design is needed within an enterprise and why production environments are set up for success with hosts in mind. The best thing you can do as an engineer is to design, implement, and troubleshoot with the users in mind. Networking not only connects computers/hardware but also connects people, businesses, and service providers. Without an HA design in mind, we lose the entire idea of networking itself.
