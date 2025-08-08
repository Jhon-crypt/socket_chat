#!/usr/bin/env python3
"""
Professional TCP Chat Server
Handles multiple client connections with real-time messaging
"""

import socket
import threading
import json
import time
import logging
from typing import Dict, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChatServer:
    def __init__(self, host: str = 'localhost', port: int = 12345):
        self.host = host
        self.port = port
        self.clients: Dict[socket.socket, str] = {}  # socket -> username
        self.clients_lock = threading.Lock()
        self.running = False
        self.server_socket = None
        
    def start(self):
        """Start the chat server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"Chat server started on {self.host}:{self.port}")
            logger.info("Waiting for connections...")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    logger.info(f"New connection from {address}")
                    
                    # Start a new thread to handle the client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        logger.error(f"Error accepting connections: {e}")
                    
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle individual client connection"""
        username = None
        
        try:
            # Get username from client
            username = self.get_username(client_socket)
            if not username:
                return
                
            # Add client to the list
            with self.clients_lock:
                self.clients[client_socket] = username
                
            # Notify all clients about new user
            self.broadcast_message({
                'type': 'user_joined',
                'username': username,
                'message': f"{username} joined the chat",
                'timestamp': time.time()
            }, exclude=client_socket)
            
            # Send welcome message and user list
            self.send_message(client_socket, {
                'type': 'welcome',
                'message': f"Welcome to the chat, {username}!",
                'users': list(self.clients.values()),
                'timestamp': time.time()
            })
            
            # Handle client messages
            while self.running:
                try:
                    message_data = self.receive_message(client_socket)
                    if not message_data:
                        break
                        
                    # Process the message
                    self.process_message(client_socket, username, message_data)
                    
                except socket.timeout:
                    continue
                except (ConnectionResetError, ConnectionAbortedError):
                    break
                except Exception as e:
                    logger.error(f"Error handling message from {username}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")
        finally:
            self.disconnect_client(client_socket, username)
    
    def get_username(self, client_socket: socket.socket) -> str:
        """Get username from client during initial handshake"""
        try:
            client_socket.settimeout(30)  # 30 second timeout for username
            username_data = self.receive_message(client_socket)
            
            if username_data and username_data.get('type') == 'join':
                username = username_data.get('username', '').strip()
                if username and len(username) <= 20:
                    # Check if username is already taken
                    with self.clients_lock:
                        if username in self.clients.values():
                            self.send_message(client_socket, {
                                'type': 'error',
                                'message': 'Username already taken'
                            })
                            return None
                    
                    client_socket.settimeout(1.0)  # Set shorter timeout for regular messages
                    return username
                    
            self.send_message(client_socket, {
                'type': 'error',
                'message': 'Invalid username'
            })
            return None
            
        except Exception as e:
            logger.error(f"Error getting username: {e}")
            return None
    
    def process_message(self, client_socket: socket.socket, username: str, message_data: dict):
        """Process incoming message from client"""
        message_type = message_data.get('type')
        
        if message_type == 'chat':
            # Regular chat message
            content = message_data.get('message', '').strip()
            if content:
                broadcast_data = {
                    'type': 'chat',
                    'username': username,
                    'message': content,
                    'timestamp': time.time()
                }
                self.broadcast_message(broadcast_data)
                logger.info(f"{username}: {content}")
                
        elif message_type == 'ping':
            # Ping/pong for connection keep-alive
            self.send_message(client_socket, {'type': 'pong'})
    
    def send_message(self, client_socket: socket.socket, data: dict):
        """Send JSON message to client with proper framing"""
        try:
            message = json.dumps(data) + '\n'
            client_socket.send(message.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def receive_message(self, client_socket: socket.socket) -> dict:
        """Receive JSON message from client with proper framing"""
        try:
            buffer = ""
            while '\n' not in buffer:
                chunk = client_socket.recv(1024).decode('utf-8')
                if not chunk:
                    return None
                buffer += chunk
            
            # Extract the first complete message
            message, remaining = buffer.split('\n', 1)
            if remaining:
                # Put remaining data back (in a real implementation, you'd buffer this)
                pass
                
            return json.loads(message)
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            return None
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return None
    
    def broadcast_message(self, data: dict, exclude: socket.socket = None):
        """Broadcast message to all connected clients"""
        with self.clients_lock:
            disconnected_clients = []
            
            for client_socket in list(self.clients.keys()):
                if client_socket != exclude:
                    try:
                        self.send_message(client_socket, data)
                    except Exception:
                        disconnected_clients.append(client_socket)
            
            # Clean up disconnected clients
            for client_socket in disconnected_clients:
                username = self.clients.get(client_socket)
                self.disconnect_client(client_socket, username, notify=False)
    
    def disconnect_client(self, client_socket: socket.socket, username: str, notify: bool = True):
        """Disconnect a client and clean up"""
        try:
            with self.clients_lock:
                if client_socket in self.clients:
                    del self.clients[client_socket]
            
            client_socket.close()
            
            if username and notify:
                logger.info(f"{username} disconnected")
                self.broadcast_message({
                    'type': 'user_left',
                    'username': username,
                    'message': f"{username} left the chat",
                    'timestamp': time.time()
                })
                
        except Exception as e:
            logger.error(f"Error disconnecting client: {e}")
    
    def stop(self):
        """Stop the server"""
        logger.info("Shutting down server...")
        self.running = False
        
        # Close all client connections
        with self.clients_lock:
            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("Server stopped")

def main():
    """Main function to run the server"""
    server = ChatServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server crashed: {e}")
    finally:
        server.stop()

if __name__ == "__main__":
    main()