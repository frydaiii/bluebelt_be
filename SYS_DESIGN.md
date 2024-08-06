
---

# Client-Server Communication System Design Document

## Table of Contents
1. Introduction
2. Components
    - Client
    - Server
3. System Architecture
4. Communication Protocol
5. Heart-Beating by using Ping-Pong Mechanism
6. Sequence Diagrams
7. Scalability considerations
8. Plan to execute the implementation

## Introduction
This document outlines the design of a client-server communication system where the client can initialize and disable connections, exchange messages with the server, and maintain a heart-beating connection to ensure the connection is alive.

## Components
1. Client:
    - Initialize connection to the server
    - Disable connection from the server
    - Send and receive text and multimedia messages. Save to file if the incoming message from server is multimedia
    - Maintain an active connection through Ping-Pong frame

2. Server:
    - Accept connections from multiple clients
    - Send and receive text and multimedia messages. Accept the incomming message if it is in a valid time range:
        - Text message: Save to database
        - Multimedia message: Save to file and save the file path to the database
    - Expose an API to retrieve messages with pagination
    - Maintain an active connection through Ping-Pong frame

## System Architecture
The system follows a client-server architecture where multiple clients can communicate with a central server.

### Diagram
```
+---------+        +---------+
|  Client |<------>|  Server |
+---------+        +---------+
```

## Communication Protocol

### Message Format
- Text Message: Plain string
- Multimedia Message: Bytes stream

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
  |                            Create new chat in DB
  |                                 if not exist
  |                                      |

```
### Messaging
```
Client                           Server
  |                                 |
  |------ Send Text Message ------->|
  |                                 |
  |                            Save if valid
  |                                 |
  |<--------- Send Status ----------|
  |                                 |
  |--- Send Multimedia Message ---->|
  |                                 |
  |                            Save if valid
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
- **Vertical Scaling**: Increase the resources (CPU, RAM) of the server. This is limited by the physical capabilities of the server hardware
- **Horizontal Scaling**: Distribute the load across multiple servers. This typically involves:
    - **Load Balancers**: Use load balancers to distribute incoming WebSocket connections across multiple server instances
    - **Sticky Sessions**: Ensure that once a WebSocket connection is established, subsequent communication from that client is directed to the same server instance to maintain the connection

*Note: ensure data consistency when implementing a distributed system.*
## Plan to execute the implementation
- Implement the client with required functions
- Implement the server with required functions
- Design DB schema for the server
- ~Implement unittest for these function, and intergration test for the system~
- Manual test workflow of the system
