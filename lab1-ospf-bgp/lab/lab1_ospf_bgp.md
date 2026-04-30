# OSPF and BGP

In modern computer networking, the two major protocols stand out when it comes to dynamic routing in both preservation and scale of enterprises, internet service providers (ISPs), and how the internet functions today. Interior Gateway Protocol (IGP) and Exterior Gateway Protocol (EGP) work on the Network layer (Layer 3) of the OSI Model, which dynamically learns the destinations of routes on a network (both internally and externally). Both utilize different algorithms for this to function properly.

IGP has a couple of different algorithms used to learn how to dynamically route traffic:
 1. Distance Vector: RIP, EIGRP
 2. Link State: OSPF, IS-IS

EGP only has a single algorithm used to learn how to dynamically route traffic:
1. Path Vector: BGP (iBGP and eBGP)

Without going too deep into all of these concepts, in this lab, I utilized **OSPF** and **BGP** for both interior and exterior examples of how routing works on the Internet. 

We will go through these concepts in this specific lab:
1. **Initial Setup**
2. **IP Addressing (IPv4/IPv6)**
3. **OSPF Configuration (OSPFv2 + OSPFv3)**
4. **BGP Configuration (IPv4/IPv6)**
5. **Endpoint Configuration**
6. **Wrap-Up**

Let's get started!

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
no ip domain-name
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
no ip domain-name
!
line console 0
 logging synchronous
exit
!
do wr
end
```

R3:
```bash
conf t
!
hostname R3
!
no ip domain-name
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
no ip domain-name
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

With this very simple setup completed, we should be all good to continue with the more sophisticated aspects of this lab.

### **Part 2: IP Addressing + Default Routes (IPv4/IPv6)**
When it comes to configuring IP addresses on Cisco, we want to make sure that we have the correct syntax between IPv4 and IPv6, as well as enabling the interface. I'm also going to be adding static default routes on **R1** to **ISP** as a best practice. This ensures that if any IPs don't match within R1's routes, it will automatically be set to the ISP router:

R1:
```bash
ip route 0.0.0.0 0.0.0.0 100.0.0.1
ipv6 route ::/0 GigabitEthernet0/0 fd00:100::1
```
* As you can see, I've set an IPv4 default route to the ISP's next hop address, as well as a recursive IPv6 default route through R1's Gi0/0 interface.

One last point on this step is to make sure you enable IPv6 routing using the IPv6 unicast command:
```bash
ipv6 unicast-routing
```
* Without it, IPv6 routing won't work even if you configure the interfaces appropriately.

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
 description Loopback 1.1.1.1
exit
!
int gi0/0
 ip address 100.0.0.2 255.255.255.252
 ipv6 address fd00:100::2/64
 ipv6 enable
 no shutdown
 description Connection to ISP
exit
!
int gi0/1
 ip address 10.0.12.1 255.255.255.252
 ipv6 address fd00:12::1/64
 ipv6 enable
 no shutdown
 description Connection to R2
exit
!
int gi0/2
 ip address 10.0.13.1 255.255.255.252
 ipv6 address fd00:13::1/64
 ipv6 enable
 no shutdown
 description Connection to R3
exit
!
int gi0/3
 description Not in Use
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
interface lo0
 ip address 2.2.2.2 255.255.255.255
 ipv6 address fd00:2::1/128
 description Loopback 2.2.2.2
exit
!
interface gi0/0
 ip address 10.0.12.2 255.255.255.252
 ipv6 address fd00:12::2/64
 ipv6 enable
 no shutdown
 description Connection to R1
exit
!
interface gi0/1
 ip address 10.0.23.1 255.255.255.252
 ipv6 address fd00:23::1/64
 ipv6 enable
 no shutdown
 description Connection to R3
exit
!
interface gi0/2
 description Not in Use
exit
!
interface gi0/3
 description Not in Use
exit
!
do wr
end
```

R3:
```bash
conf t
!
ipv6 unicast-routing
!
interface lo0
 ip address 3.3.3.3 255.255.255.255
 ipv6 address fd00:3::1/128
 description Loopback 3.3.3.3
exit
!
interface gi0/0
 ip address 10.0.13.2 255.255.255.252
 ipv6 address fd00:13::2/64
 ipv6 enable
 no shutdown
 description Connection to R1
exit
!
interface gi0/1
 ip address 10.0.23.2 255.255.255.252
 ipv6 address fd00:23::2/64
 ipv6 enable
 no shutdown
 description Connection to R2
exit
!
interface gi0/2
 description Not in Use
exit
!
interface gi0/3
 description Not in Use
exit
!
do wr
end
```

ISP:
```bash
conf t
!
ipv6 unicast-routing
!
interface lo0
 ip address 4.4.4.4 255.255.255.255
 ipv6 address fd00:4::1/128
 description Loopback 4.4.4.4
exit
!
interface gi0/0
 ip address 100.0.0.1 255.255.255.252
 ipv6 address fd00:100::1/64
 ipv6 enable
 no shutdown
 description Connection to R1
exit
!
interface gi0/1
 ip address 15.0.0.2 255.255.255.252
 ipv6 address fd00:15::2/64
 ipv6 enable
 no shutdown
 description Connection to Internet
exit
!
interface gi0/2
 description Not in Use
exit
!
interface gi0/3
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

With all of the IP addresses configured on the interfaces, as well as loopback addresses set, we can continue on and set up OSPF on our enterprise network next.

### **Part 3: OSPF Configuration (OSPFv2 + OSPFv3)**
Up next is setting up our enterprise with its IGP of OSPF! I decided to dual-stack IPv4/IPv6 to showcase modern-day networking design/functionality, so **OSPFv2** and **OSPFv3** will be integrated in this lab. To set up both versions of OSPF, we need to not only utilize the **router ospf** command, but as well as enabling ospf on interfaces as well. 

Typically, most enterprises will enable OSPF on the interface instead of the "network" command, just to simplify the configuration and verification of OSPF without it seeping into unnecessary networks.

Let's see how the configuration looks for each of our enterprise routers:

R1:
```bash
conf t
!
router ospf 1
 router-id 1.1.1.1
 log-adjacency-changes
 passive-interface default
 no passive-interface gi0/1
 no passive-interface gi0/2
exit
!
ipv6 router ospf 1
 router-id 1.1.1.1
 log-adjacency-changes
 passive-interface default
 no passive-interface gi0/1
 no passive-interface gi0/2
!
interface lo0
 ip ospf 1 area 0
 ipv6 ospf 1 area 0
exit
!
int range gi0/1,gi0/2
 ip ospf 1 area 0
 ipv6 ospf 1 area 0
 ip ospf network point-to-point
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
 no passive-interface gi0/0
 no passive-interface gi0/1
exit
!
ipv6 router ospf 1
 router-id 2.2.2.2
 log-adjacency-changes
 passive-interface default
 no passive-interface gi0/0
 no passive-interface gi0/1
exit
!
int range gi0/0,gi0/1
 ip ospf 1 area 0
 ipv6 ospf 1 area 0
 ip ospf network point-to-point
exit
!
interface lo0
 ip ospf 1 area 0
 ipv6 ospf 1 area 0
exit
!
do wr
end
```

R3:
```bash
conf t
!
router ospf 1
 router-id 3.3.3.3
 passive-interface default
 no passive-interface gi0/0
 no passive-interface gi0/1
exit
!
ipv6 router ospf 1
 router-id 3.3.3.3
 passive-interface default
 no passive-interface gi0/0
 no passive-interface gi0/1
exit
!
int range gi0/0,gi0/1
 ip ospf 1 area 0
 ipv6 ospf 1 area 0
 ip ospf network point-to-point
exit
!
interface lo0
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
show ip ospf neighbor
show ipv6 ospf neighbor
```

With OSPFv2 and OSPFv3 now configured within our enterprise network, IP routing will now dynamically be learned for both IPv6/IPv6. Now is the WN connection between R1 and ISP, and establishing a BGP connection between both of them.

### **Part 4: BGP Configuration (IPv4 + IPv6)**
When it comes to connections between different IGPs, this is where EGP shines with eBGP. With BGP being a path-vector protocol, its function is to be able to exchange network information between different autonomous systems (in this case, AS65000 and AS65001). A TCP connection is established, and peering allows for policies, security, and scalability to happen between different IGPs. Convergence takes longer compared to OSPF, but it is the best way to connect networks together.

R1:
```bash
conf t
!
router bgp 65000
 no auto-summary
 bgp log-neighbor-changes
 neighbor 100.0.0.1 remote-as 65001
 neighbor 100.0.0.1 description ISP
 neighbor fd00:100::1 remote-as 65001
 neighbor fd00:100::1 description ISP
!
 address-family ipv4
  network 1.1.1.1 mask 255.255.255.255
  neighbor 100.0.0.1 activate
 exit-address-family
!
 address-family ipv6 unicast
  network fd00:1::1/128
  neighbor fd00:100::1 activate
 exit-address-family
!
exit
!
do wr
end
```

ISP:
```bash
conf t
!
router bgp 65001
 no auto-summary
 bgp log-neighbor-changes
 neighbor 100.0.0.2 remote-as 65000
 neighbor 100.0.0.2 description R1
 neighbor fd00:100::2 remote-as 65000
 neighbor fd00:100::2 description R1
!
 address-family ipv4
  neighbor 100.0.0.2 default-originate
  neighbor 100.0.0.2 activate
 exit-address-family
!
 address-family ipv6 unicast
  neighbor fd00:100::2 default-originate
  neighbor fd00:100::2 activate
 exit-address-family
!
exit
!
do wr
end
```
Command Breakdown:
* `router bgp 65000`: Enables BGP with AS65000.
* `no auto-summary`: Disables subnet routes into classful network routes.
* `bgp log-neighbor-changes`: Enables logging of messages when the status of a BGP neighbor changes.
* `neighbor 100.0.0.1 remote-as 65001`: Establishes an IPv4 BGP peering with IP 100.0.0.1 to AS65001.
* `neighbor fd00:100::1 remote-as 65001`: Establishes an IPv6 BGP peering with IP fd00:100::1 to AS65001.
* `address-family ipv4`: Activates IPv4 address family for BGP routing.
* `neighbor 100.0.0.1 activate`: Activates a BGP neighbor relationship with IP address 100.0.0.1.
* `address-family ipv6`: Activates IPv6 address family for BGP routing.
* `neighbor fd00:100::2 activate`: Activates a BGP neighbor relationship with IP address fd00:100::2.
* `neighbor fd00:100::2 default-originate`: Advertise the default route of fd00:100::2.

**Verify**
```bash
show bgp summary
show bgp ipv4 unicast summary
show bgp ipv6 unicast summary
```

With BGP established between R1 and ISP, our WAN connection is complete! Although BGP can go WAY more in-depth with policies and security, this gives a great overview of how BGP works at a fundamental level. Lastly, let's configure our External Server over the "internet".

### **Part 5: Endpoint Configuration**
Our last step in this lab was to be able to connect to the external internet, showcasing this thought with an "external server," figuratively in the cloud. This gives us an idea of how ISPs have other connections as well as how an enterprise may still be able to connect over the internet through their edge router. 

Here is the configuration I added to the external server in my lab:

SVR:
```bash
sudo hostname SVR1
sudo ifconfig eth0 15.0.0.1 netmask 255.255.255.252
sudo ifconfig eth0 add fd00:15::1/64
sudo route add default gw 15.0.0.2 eth0
sudo ip -6 route add default via fd00:15::2
```
Command Breakdown:
* `sudo ifconfig eth0 15.0.0.1 netmask 255.255.255.252`: Sets the IPv4 address of the server.
* `sudo ifconfig eth0 add fd00:15::1/64`: Sets the IPv6 address of the server.
* `sudo route add default gw 15.0.0.2 eth0`: Sets the IPv4 default-gateway.
* `sudo ip -6 route add default via fd00:15::2`: Sets the IPv6 default-gateway.

**Verify**
```bash
ping 15.0.0.2
ping fd00:15::2
```

With our server now set up appropriately, this completes our OSPF and BGP lab!

### **Wrap-Up**
With our entire OSPF + BGP lab now complete, this demonstrates a very simple example of how an enterprise edge router (CE router) connects to a service provider's edge router (PE router). This is the fabric of how the internet functions at the infrastructure level, as well as giving you an idea of how many more connections can be made for many more IGPs and EGP connections. 
