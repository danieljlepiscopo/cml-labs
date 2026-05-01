# HSRP + ACL + NAT Lab

In modern-day computer networking, we strive to implement High Availability (HA) designs to continue providing services to users during downtime, glitches, or failures. To do this, we need to be able to add redundancy to a system on every level: power, data, geographic, and pathway. Essentially, load-balancing a system, backing up data, failovers, and using the appropriate networking protocols that HA designs need to function properly. 

A few of these networking protocols I want to go over in this lab are HSRP, ACLs, and NAT. These protocols I'll dig into much deeper with every step of this lab, but as an overview, these three protocols help ensure a HA design by making sure users are abstracted from a router failover, security practices like Least Privilege, and can access the internet with an IPv4 IP address.

Here is the step-by-step we're going to go over in this lab:
1. **Initial Setup**
2. **VLANs**
3. **IP Addresses + Static Routes (IPv4/IPv6)**
4. **OSPF Configuration (OSPFv2 + OSPFv3)**
5. **HSRP (IPv4/IPv6)**
6. **Extended ACLs (IPv4/IPv6)**
7. **NAT Configuration**
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
* `no ip domain-name`: Prevents a device from trying to resolve a mistyped command as a hostname.
* `logging synchronous`: Stops system messages from interrupting CLI command input.

**Verify**

```bash
show running-config
```

With this very simple setup completed, we should be all good to continue with setting up the VLANs for this lab.

### **Part 2: VLANs**



SW1:
```bash
conf t
!
vlan 10
 name MARKETING
vlan 20
 name IT
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
vlan 10
 name MARKETING
vlan 20
 name IT
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

### **Part 3: IP Addresses + Static Routes (IPv4/IPv6)**

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

### **Part 4: OSPF Configuration (OSPFv2 + OSPFv3)**

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

### **Part 5: HSRP (IPv4/IPv6)**

VLAN10

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

VLAN20

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

### **Part 6: Extended ACLs**

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

### **Part 7: NAT Configuration**

NAT is ONLY for IPv4; IPv6 is globally routable, so there's no need for it on IPv6.

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
ip nat inside source list 1 interface g0/0 overload
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
ip nat inside source list 1 interface g0/0 overload
!
do wr
end
```

### **Part 8: Endpoint Configuration**

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
