# OSPF and BGP

In modern computer networking, the two major protocols stand out when it comes to dynamic routing in both preservation and scale of enterprises, internet service providers (ISPs), and how the internet functions today. Interior Gateway Protocol (IGP) and Exterior Gateway Protocol (EGP) work on the Network layer (Layer 3) of the OSI Model, which dynamically learns the destinations of routes on a network (both internally and externally). Both utilize different algorithms for this to function properly.

IGP has a couple of different algorithms used to learn how to dynamically route traffic:
 1. Distance Vector: RIP, EIGRP
 2. Link State: OSPF, IS-IS

EBG only has a single algorithm used to learn how to dynamically route traffic:
1. Path Vector: BGP (iBGP and eBGP)

Without going too deep into all of these concepts, in this lab, I utilized **OSPF** and **BGP** for both interior and exterior examples of how routing works on the Internet. 

We will go through these concepts 
