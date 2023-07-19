# zookeeper

Create a three-server distributed system that allows you to store key-value pairs
(also called KV System or Key-Value Store) in a replicated and consistent way,
using TCP as the transport layer protocol.
The system will work in a similar way (but very simplified) to the Zookepeer system, a
distributed system that allows the coordination of servers.

The system will consist of 3 servers (with known IPs and ports) and many clients.
Clients will be able to make requests to any server, both to insert information
key-value in the system (i.e., PUT) and to get them (i.e., GET). Servers, on the other hand,
must meet customer requirements. Among the three servers, choose
initially one of them as leader, who will be the only one who can perform a PUT. For another
On the other hand, any server can respond to the GET.