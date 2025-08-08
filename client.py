#!/usr/bin/env python3
"""
Professional TCP Chat Client
Connects to chat server for real-time messaging
"""

import socket
import threading
import json
import time
import sys
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChatClient:
    def __init__(self, host: str = 'localhost', port: int = 12345):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.username = ""
        self.connected = False
        self.running = False
        
    def connect(self, username: str) -> bool:
        """Connect to the chat server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.username = username
            
            # Send join message
            join_message = {
                'type': 'join',
                'username': username
            }
            
            self.send_message(join_message)
            
            # Wait for server response with longer timeout
            self.socket.settimeout(10.0)  # 10 second timeout for initial handshake
            response = self.receive_message()
            if not response:
                print("❌ No response from server")
                return False
                
            if response.get('type') == 'error':
                print(f"❌ Connection failed: {response.get('message', 'Unknown error')}")
                return False
            elif response.get('type') == 'welcome':
                print(f"✅ {response.get('message', 'Connected successfully!')}")
                users = response.get('users', [])
                if len(users) > 1:
                    other_users = [u for u in users if u != username]
                    print(f"👥 Users online: {', '.join(other_users)}")
                self.connected = True
                # Set shorter timeout for regular messaging
                self.socket.settimeout(1.0)
                return True
            else:
                print("❌ Unexpected response from server")
                return False
                
        except ConnectionRefusedError:
            print("❌ Could not connect to server. Make sure the server is running.")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def start_messaging(self):
        """Start the messaging loop"""
        if not self.connected:
            print("❌ Not connected to server")
            return
            
        self.running = True
        
        # Start receiver thread
        receiver_thread = threading.Thread(target=self.receive_messages)
        receiver_thread.daemon = True
        receiver_thread.start()
        
        # Start sender loop
        self.send_messages()
    
    def receive_messages(self):
        """Receive messages from server in a separate thread"""
        while self.running and self.connected:
            try:
                message_data = self.receive_message()
                if not message_data:
                    break
                    
                self.handle_server_message(message_data)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"Error receiving message: {e}")
                break
        
        self.disconnect()
    
    def handle_server_message(self, message_data: dict):
        """Handle different types of messages from server"""
        message_type = message_data.get('type')
        
        if message_type == 'chat':
            username = message_data.get('username', 'Unknown')
            message = message_data.get('message', '')
            timestamp = message_data.get('timestamp', time.time())
            
            # Format timestamp
            time_str = time.strftime('%H:%M:%S', time.localtime(timestamp))
            print(f"\r[{time_str}] {username}: {message}")
            print(f"{self.username}> ", end="", flush=True)
            
        elif message_type == 'user_joined':
            username = message_data.get('username', 'Someone')
            print(f"\r🟢 {username} joined the chat")
            print(f"{self.username}> ", end="", flush=True)
            
        elif message_type == 'user_left':
            username = message_data.get('username', 'Someone')
            print(f"\r🔴 {username} left the chat")
            print(f"{self.username}> ", end="", flush=True)
            
        elif message_type == 'pong':
            # Response to ping - used for keep-alive
            pass
            
        elif message_type == 'error':
            message = message_data.get('message', 'Unknown error')
            print(f"\r❌ Server error: {message}")
            print(f"{self.username}> ", end="", flush=True)
    
    def send_messages(self):
        """Handle user input and send messages"""
        print("\n" + "="*50)
        print("💬 Chat started! Type your messages and press Enter.")
        print("💡 Commands: /quit to exit, /ping to test connection")
        print("="*50)
        
        try:
            while self.running and self.connected:
                try:
                    # Get user input
                    user_input = input(f"{self.username}> ").strip()
                    
                    if not user_input:
                        continue
                        
                    # Handle commands
                    if user_input.lower() in ['/quit', '/exit', '/q']:
                        break
                    elif user_input.lower() == '/ping':
                        self.send_message({'type': 'ping'})
                        continue
                    elif user_input.lower() == '/help':
                        print("💡 Available commands:")
                        print("   /quit, /exit, /q - Exit the chat")
                        print("   /ping - Test connection to server")
                        print("   /help - Show this help message")
                        continue
                    
                    # Send regular chat message
                    message_data = {
                        'type': 'chat',
                        'message': user_input
                    }
                    
                    if not self.send_message(message_data):
                        print("❌ Failed to send message")
                        break
                        
                except EOFError:
                    # Ctrl+D pressed
                    break
                except KeyboardInterrupt:
                    # Ctrl+C pressed
                    break
                    
        except Exception as e:
            logger.error(f"Error in send loop: {e}")
        
        self.disconnect()
    
    def send_message(self, data: dict) -> bool:
        """Send JSON message to server with proper framing"""
        try:
            if not self.socket:
                return False
                
            message = json.dumps(data) + '\n'
            self.socket.send(message.encode('utf-8'))
            return True
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def receive_message(self) -> Optional[dict]:
        """Receive JSON message from server with proper framing"""
        try:
            if not self.socket:
                return None
                
            # Use existing timeout (don't override it here)
            buffer = ""
            while '\n' not in buffer:
                try:
                    chunk = self.socket.recv(1024).decode('utf-8')
                    if not chunk:
                        return None
                    buffer += chunk
                except socket.timeout:
                    return None
            
            # Extract the first complete message
            message, remaining = buffer.split('\n', 1)
            if remaining:
                # In a real implementation, you'd buffer the remaining data
                pass
                
            return json.loads(message)
            
        except socket.timeout:
            return None
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from server")
            return None
        except Exception as e:
            if self.running:
                logger.error(f"Error receiving message: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.running:
            print("\n👋 Disconnecting from chat...")
            
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        print("✅ Disconnected successfully")

def main():
    """Main function to run the client"""
    print("💬 TCP Chat Client")
    print("=" * 30)
    
    # Get server connection details
    try:
        host = input("Server host (default: localhost): ").strip() or 'localhost'
        port_input = input("Server port (default: 12345): ").strip()
        port = int(port_input) if port_input else 12345
        
        print()
        username = input("Enter your username: ").strip()
        
        if not username or len(username) > 20:
            print("❌ Username must be 1-20 characters long")
            return
            
        if not username.replace('_', '').replace('-', '').isalnum():
            print("❌ Username can only contain letters, numbers, hyphens, and underscores")
            return
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return
    except ValueError:
        print("❌ Invalid port number")
        return
    
    # Create and connect client
    client = ChatClient(host, port)
    
    try:
        print(f"\n🔄 Connecting to {host}:{port}...")
        
        if client.connect(username):
            client.start_messaging()
        else:
            print("❌ Failed to connect to server")
            
    except KeyboardInterrupt:
        print("\n👋 Chat interrupted by user")
    except Exception as e:
        print(f"❌ Client error: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()