# TCP Socket Chat Application

A professional client-server chat application built with Python using TCP sockets. This application demonstrates the fundamentals of socket programming, TCP/IP communication, and real-time message transmission over networks.

## Features

### Server Features
- **Multi-client support**: Handles multiple simultaneous client connections
- **Real-time messaging**: Instant message broadcasting to all connected clients
- **User management**: Username validation and duplicate prevention
- **Connection monitoring**: Automatic cleanup of disconnected clients
- **Message framing**: Proper JSON message boundaries with newline delimiters
- **Thread safety**: Safe concurrent access to shared client data
- **Comprehensive logging**: Detailed server activity and error logging
- **Graceful shutdown**: Clean resource cleanup on server termination

### Client Features
- **Interactive chat interface**: User-friendly command-line chat experience
- **Real-time message display**: Instant display of messages from other users
- **Connection status**: Visual indicators for user joins/leaves
- **Built-in commands**: `/quit`, `/ping`, `/help` commands
- **Input validation**: Username and message validation
- **Error handling**: Robust connection error management
- **Timestamps**: Message timestamps for better context

## Technical Implementation

### Network Protocol
- **Transport**: TCP (Transmission Control Protocol)
- **Message Format**: JSON with newline delimiters
- **Connection**: Persistent connections with keep-alive support
- **Error Handling**: Comprehensive network error management

### Message Types
```json
// Join request
{"type": "join", "username": "alice"}

// Chat message
{"type": "chat", "message": "Hello everyone!"}

// Server responses
{"type": "welcome", "message": "Welcome!", "users": ["alice", "bob"]}
{"type": "chat", "username": "alice", "message": "Hello!", "timestamp": 1234567890}
{"type": "user_joined", "username": "bob", "message": "bob joined the chat"}
{"type": "user_left", "username": "bob", "message": "bob left the chat"}
{"type": "error", "message": "Username already taken"}
```

### Architecture
- **Server**: Multi-threaded with one thread per client connection
- **Client**: Two threads - one for receiving, one for sending
- **Synchronization**: Thread-safe operations with proper locking
- **Resource Management**: Automatic cleanup of connections and threads

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

## Installation

1. Clone or download the project files:
```bash
git clone <repository-url>
cd socket_chat
```

2. Ensure Python 3.7+ is installed:
```bash
python3 --version
```

3. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv socket_chat

# Activate virtual environment
source socket_chat/bin/activate

# You should see (socket_chat) in your prompt
```

4. The application uses only Python standard library modules, so no additional packages need to be installed.

## Usage

### Starting the Server

1. Open a terminal and navigate to the project directory
2. Activate the virtual environment:
```bash
source socket_chat/bin/activate
```
3. Run the server:
```bash
python server.py
```

The server will start on `localhost:12345` by default and display:
```
2024-01-15 10:30:00,123 - INFO - Chat server started on localhost:12345
2024-01-15 10:30:00,124 - INFO - Waiting for connections...
```

### Connecting Clients

1. Open a new terminal for each client
2. Activate the virtual environment:
```bash
source socket_chat/bin/activate
```
3. Run the client:
```bash
python client.py
```

4. Follow the prompts:
```
💬 TCP Chat Client
==============================
Server host (default: localhost): 
Server port (default: 12345): 
Enter your username: alice
```

5. Start chatting! The client will show:
```
✅ Welcome to the chat, alice!
💬 Chat started! Type your messages and press Enter.
💡 Commands: /quit to exit, /ping to test connection
alice> 
```

### Client Commands

- **Regular messages**: Just type and press Enter
- **`/quit`** or **`/exit`** or **`/q`**: Leave the chat
- **`/ping`**: Test connection to server
- **`/help`**: Show available commands

### Example Chat Session

```
alice> Hello everyone!
[14:30:15] alice: Hello everyone!

🟢 bob joined the chat
[14:30:20] bob: Hi alice!
bob> How's everyone doing?
[14:30:25] bob: How's everyone doing?

alice> Great! Welcome to the chat, bob
[14:30:30] alice: Great! Welcome to the chat, bob

🔴 bob left the chat
```

## Configuration

### Server Configuration
Edit the `main()` function in `server.py` to customize:
```python
server = ChatServer(host='0.0.0.0', port=8080)  # Listen on all interfaces
```

### Client Configuration
The client will prompt for connection details, or you can modify the defaults in `client.py`:
```python
host = input("Server host (default: localhost): ").strip() or 'localhost'
port_input = input("Server port (default: 12345): ").strip()
port = int(port_input) if port_input else 12345
```

## Network Concepts Demonstrated

### TCP Socket Programming
- **Socket creation**: `socket.socket(AF_INET, SOCK_STREAM)`
- **Server binding**: Binding to host and port
- **Client connection**: Connecting to remote server
- **Data transmission**: Reliable, ordered data delivery

### Stream Management
- **Message boundaries**: JSON with newline delimiters
- **Buffer handling**: Proper data buffering and parsing
- **Connection state**: Managing connection lifecycle

### Concurrency
- **Threading**: One thread per client connection
- **Synchronization**: Thread-safe shared data access
- **Non-blocking operations**: Timeout-based socket operations

### Error Handling
- **Connection errors**: Network connectivity issues
- **Protocol errors**: Invalid message formats
- **Resource cleanup**: Proper socket and thread cleanup

## Troubleshooting

### Common Issues

**"Address already in use" error:**
```bash
# Activate virtual environment first
source socket_chat/bin/activate
# Wait a moment and try again, or use a different port
python server.py  # Will use port 12345
```

**"Connection refused" error:**
- Ensure the server is running before starting clients
- Check if the host and port are correct
- Verify firewall settings if connecting remotely

**Client disconnects unexpectedly:**
- Check network connectivity
- Look at server logs for error messages
- Ensure proper message formatting

### Server Logs
The server provides detailed logging:
```
2024-01-15 10:30:05,123 - INFO - New connection from ('127.0.0.1', 54321)
2024-01-15 10:30:05,125 - INFO - alice: Hello everyone!
2024-01-15 10:30:10,200 - INFO - bob disconnected
```

## Security Considerations

This is a basic implementation for learning purposes. For production use, consider:

- **Authentication**: User authentication and authorization
- **Encryption**: TLS/SSL for encrypted communication  
- **Input validation**: Comprehensive message sanitization
- **Rate limiting**: Prevent spam and abuse
- **Access control**: IP-based or user-based access restrictions

## Quick Start

### Prerequisites
1. Ensure you have Python 3.7+ installed
2. Set up the virtual environment (one-time setup):
```bash
python3 -m venv socket_chat
```

### Running the Chat Application

**Terminal 1 (Server):**
```bash
# Activate virtual environment
source socket_chat/bin/activate

# Run server
python server.py
```

**Terminal 2+ (Clients):**
```bash
# Activate virtual environment
source socket_chat/bin/activate

# Run client
python client.py
```

### Deactivating Virtual Environment
When you're done, deactivate the virtual environment:
```bash
deactivate
```

## Learning Outcomes

By building and running this chat application, you'll learn:

1. **TCP Socket Programming**: How to create and manage TCP connections
2. **Client-Server Architecture**: Understanding of distributed system basics
3. **Network Protocols**: How data is transmitted over networks
4. **Concurrency**: Multi-threading and synchronization concepts
5. **Error Handling**: Robust network error management
6. **Message Framing**: Proper data boundaries in stream protocols
7. **Real-time Communication**: Instant message delivery mechanisms

## Extension Ideas

- Add private messaging between users
- Implement chat rooms/channels
- Add file transfer capability
- Create a GUI client using tkinter or PyQt
- Add message persistence with a database
- Implement user authentication
- Add emoji and formatting support
- Create a web-based client using WebSockets

## License

This project is provided for educational purposes. Feel free to modify and extend it for your learning needs.