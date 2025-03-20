

| **Feature**                           | **Application Load Balancer (ALB)**                                              | **Network Load Balancer (NLB)**                                                   |
|---------------------------------------|----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **OSI Layer Operation**               | Operates at Layer 7 (Application layer)                                          | Operates at Layer 4 (Transport layer)                                             |
| **Protocol Support**                  | Supports HTTP, HTTPS, and WebSocket                                              | Supports TCP, UDP, and TLS                                                        |
| **Routing Capabilities**              | Content-based routing (URL paths, host headers, application-level attributes)    | IP-based routing (IP addresses and ports)                                         |
| **Target Types**                      | EC2 instances, IP addresses, Lambda functions, containers                        | EC2 instances, IP addresses, Application Load Balancers                           |
| **SSL/TLS Termination**               | Can terminate SSL/TLS and offload encryption/decryption                          | Can terminate TLS but passes decrypted traffic to targets                         |
| **Health Checks**                     | Application-level (HTTP/HTTPS)                                                   | Network-level (TCP, HTTP, HTTPS)                                                  |
| **Sticky Sessions**                   | Supports sticky sessions (session affinity)                                      | Does not natively support sticky sessions                                         |
| **Use Cases**                         | Web applications, microservices, containerized applications                      | High-performance, low-latency apps, gaming, IoT, streaming                        |
| **Static IP and Source IP Preservation** | No static IPs by default, source IP may not be preserved                         | Provides static IPs per AZ and preserves client source IP                         |

