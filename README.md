# A simple client-server communication 
This is a simple client-server communication system where multiple clients can communicate with a central server by using websockets.
Each side can send text messages and multimedia messages (by sending streams of bytes). If the server receives a multimedia message, it will save it to a file and send a custom respond based on the type of message received.

## Getting Started
This project is built using Python 3.12.3. In the project directory, run:

```
python3 -m venv .venv # Create a virtual environment
source .venv/bin/activate # Activate the virtual environment
pip install -r requirements.txt # Install dependencies
```
Start the server with default port 8000:

```
python3 server.py
```
On a different terminal, start the client:

```
python3 client.py
```
## Server endpoints
- `/ws/{client_id}`: Websocket endpoint for clients to connect to the server. The `client_id` is a unique identifier for each client.
- `/chats?client_id={client_id}`: GET endpoint to retrieve all chats for a client with `client_id`.
- `/messages?chat_id={chat_id}&limit={limit}&offset={offset}`: GET endpoint to retrieve all messages for a chat with `chat_id`.