
---

# Client-Server Communication System Design Document

## Table of Contents
1. Introduction
2. Requirements
3. System Architecture
4. Components
    - Client
    - Server
5. Communication Protocol
6. Heart-Beating by using Ping-Pong Mechanism
7. Sequence Diagrams
8. Scalability considerations.
9. Plan to execute the implementation.

## Introduction
This document outlines the design of a client-server communication system where the client can initialize and disable connections, exchange text messages with the server, and maintain a heart-beating connection to ensure the connection is alive.

## Requirements
1. Client Features:
    - Initialize connection to the server
    - Disable connection from the server
    - Send and receive text messages
    - Send bytes stream for multimedia messages
    - Maintain an active connection through Ping-Pong frame.

2. Server Features:
    - Accept connections from multiple clients
    - Receive and send text messages to clients
    - Receive and save bytes stream to files
    - Maintain an active connection through Ping-Pong frame.

## System Architecture
The system follows a client-server architecture where multiple clients can communicate with a central server. The communication will be facilitated over TCP/IP for reliable transmission.

### Diagram
```
+---------+        +---------+
|  Client |<------>|  Server |
+---------+        +---------+
```

## Components

### Client
- Connection Initialization: Establish a connection to the server.
- Connection Termination: Disconnect from the server.
- Messaging: Send and receive text messages.
- Messaging: Send bytes stream for multimedia messages
- Heart-Beat Response: Periodically send a ping signal and respond to incoming ping signals from others with a pong.

### Server
- Connection Handling: Accept connections from clients.
- Messaging: Send and receive text messages.
- Messaging: Receive and save bytes stream to files
- Heart-Beat Response: Periodically send a ping signal and respond to incoming ping signals from others with a pong.

## Communication Protocol

### Message Format
- Text Message: Plain string.
- Multimedia Message: Bytes

### Port
- The server will listen on a specified TCP port (e.g., 8000).

## Sequence Diagrams

### Connection Initialization
```
Client                                Server
  |                                      |
  |---------- Init Connection ---------->|
  |                                      |
  |<-------- Connection accepted --------|
  |                                      |
  |---- Send timezone as first msg ----->|
  |                                      |

```
### Messaging
```
Client                           Server
  |                                 |
  |------ Send Text Message ------->|
  |                                 |
  |<--------- Send Status ----------|
  |                                 |
  |--- Send Multimedia Message ---->|
  |                                 |
  |<--------- Send Status ----------|
  |                                 |
```
### Heart-Beating
```
Machine                    Machine
  |                           |
  |---------- Ping ---------->|
  |                           |
  |<--------- Pong -----------|
  |                           |
```
### Connection Termination
```
Client                     Server
  |                           |
  |-- Terminate Connection -->|
  |                           |
```
## Scalability considerations
- **Vertical Scaling**: Increase the resources (CPU, RAM) of the server. This is limited by the physical capabilities of the server hardware.
- **Horizontal Scaling**: Distribute the load across multiple servers. This typically involves:
    - **Load Balancers**: Use load balancers to distribute incoming WebSocket connections across multiple server instances.
    - **Sticky Sessions**: Ensure that once a WebSocket connection is established, subsequent communication from that client is directed to the same server instance to maintain the connection.
  <br>
*Note: ensure data consistency when implementing a distributed system.*
## Plan to execute the implementation
- Implement the client with required functions
- Implement the server with required functions
- ~Implement unittest for these function, and intergration test for the system~
- Manual test workflow of the system
