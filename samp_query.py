"""
SAMP (San Andreas Multiplayer) Query Protocol Implementation
Direct UDP queries to SAMP servers to get real-time player count and server info
"""

import asyncio
import socket
import struct
import logging
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ServerInfo:
    """Server information from SAMP query"""
    is_online: bool
    players: int
    max_players: int
    hostname: str = ""
    gamemode: str = ""
    language: str = ""
    error: Optional[str] = None

class SAMPQueryClient:
    """Client for querying SAMP servers directly via UDP"""
    
    # SAMP Query opcodes
    OPCODE_SERVER_INFO = ord('i')
    OPCODE_DETAILED_PLAYER_INFO = ord('d') 
    OPCODE_BASIC_PLAYER_INFO = ord('c')
    OPCODE_RULES = ord('r')
    
    def __init__(self, timeout: float = 3.0):
        self.timeout = timeout
    
    def _create_query_packet(self, ip: str, port: int, opcode: int, extra_data: bytes = b'') -> bytes:
        """Create SAMP query packet"""
        # Convert IP to 4-byte format
        ip_parts = ip.split('.')
        ip_bytes = struct.pack('BBBB', *[int(part) for part in ip_parts])
        
        # Pack: IP (4 bytes) + Port (2 bytes, little-endian) + Magic (4 bytes) + Opcode (1 byte) + Extra
        magic = b'SAMP'
        packet = ip_bytes + struct.pack('<H', port) + magic + struct.pack('B', opcode) + extra_data
        
        return packet
    
    def _parse_server_info_response(self, data: bytes) -> ServerInfo:
        """Parse server info response packet"""
        try:
            if len(data) < 11:
                return ServerInfo(False, 0, 0, error="Response too short")
            
            # Skip IP (4) + Port (2) + Magic (4) + Opcode (1) = 11 bytes
            offset = 11
            
            # Password flag (1 byte)
            if offset >= len(data):
                return ServerInfo(False, 0, 0, error="Invalid response format")
            password = data[offset]
            offset += 1
            
            # Players (2 bytes, little-endian) 
            if offset + 2 > len(data):
                return ServerInfo(False, 0, 0, error="Invalid response format")
            players = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # Max players (2 bytes, little-endian)
            if offset + 2 > len(data):
                return ServerInfo(False, 0, 0, error="Invalid response format")
            max_players = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # Hostname length (4 bytes, little-endian)
            if offset + 4 > len(data):
                return ServerInfo(False, 0, 0, error="Invalid response format")
            hostname_len = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # Hostname string
            hostname = ""
            if hostname_len > 0 and offset + hostname_len <= len(data):
                try:
                    hostname = data[offset:offset+hostname_len].decode('utf-8', errors='ignore')
                except:
                    hostname = ""
                offset += hostname_len
            
            # Gamemode length (4 bytes, little-endian)
            gamemode = ""
            if offset + 4 <= len(data):
                gamemode_len = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                
                if gamemode_len > 0 and offset + gamemode_len <= len(data):
                    try:
                        gamemode = data[offset:offset+gamemode_len].decode('utf-8', errors='ignore')
                    except:
                        gamemode = ""
                    offset += gamemode_len
            
            # Language length (4 bytes, little-endian)
            language = ""
            if offset + 4 <= len(data):
                language_len = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
                
                if language_len > 0 and offset + language_len <= len(data):
                    try:
                        language = data[offset:offset+language_len].decode('utf-8', errors='ignore')
                    except:
                        language = ""
            
            return ServerInfo(
                is_online=True,
                players=players,
                max_players=max_players,
                hostname=hostname,
                gamemode=gamemode,
                language=language
            )
            
        except Exception as e:
            logger.error(f"Error parsing server info response: {e}")
            return ServerInfo(False, 0, 0, error=f"Parse error: {str(e)}")
    
    async def query_server(self, ip: str, port: int) -> ServerInfo:
        """Query SAMP server for basic info (players, max_players, etc.)"""
        try:
            # Create query packet for server info
            packet = self._create_query_packet(ip, port, self.OPCODE_SERVER_INFO)
            
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            try:
                # Send query
                sock.sendto(packet, (ip, port))
                
                # Receive response
                response_data, addr = sock.recvfrom(4096)
                
                # Parse response
                server_info = self._parse_server_info_response(response_data)
                
                return server_info
                
            finally:
                sock.close()
                
        except socket.timeout:
            return ServerInfo(False, 0, 0, error="Connection timeout")
        except socket.gaierror as e:
            return ServerInfo(False, 0, 0, error=f"DNS error: {str(e)}")
        except Exception as e:
            logger.error(f"Error querying server {ip}:{port}: {e}")
            return ServerInfo(False, 0, 0, error=f"Query error: {str(e)}")
    
    async def query_server_async(self, ip: str, port: int) -> ServerInfo:
        """Async wrapper for server query"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: asyncio.run(self.query_server(ip, port)))

# Arizona RP Servers List
ARIZONA_SERVERS = [
    {"id": 1, "name": "Phoenix", "ip": "176.57.147.190", "port": 7777},
    {"id": 2, "name": "Tucson", "ip": "176.57.147.191", "port": 7777},
    {"id": 3, "name": "Scottdale", "ip": "176.57.147.192", "port": 7777},
    {"id": 4, "name": "Chandler", "ip": "176.57.147.193", "port": 7777},
    {"id": 5, "name": "Brainburg", "ip": "176.57.147.194", "port": 7777},
    {"id": 6, "name": "Saint-Rose", "ip": "176.57.147.195", "port": 7777},
    {"id": 7, "name": "Mesa", "ip": "176.57.147.196", "port": 7777},
    {"id": 8, "name": "Red-Rock", "ip": "176.57.147.197", "port": 7777},
    {"id": 9, "name": "Yuma", "ip": "176.57.147.198", "port": 7777},
    {"id": 10, "name": "Surprise", "ip": "176.57.147.199", "port": 7777},
    {"id": 11, "name": "Prescott", "ip": "176.57.147.200", "port": 7777},
    {"id": 12, "name": "Glendale", "ip": "176.57.147.201", "port": 7777},
    {"id": 13, "name": "Kingman", "ip": "176.57.147.202", "port": 7777},
    {"id": 14, "name": "Winslow", "ip": "176.57.147.203", "port": 7777},
    {"id": 15, "name": "Payson", "ip": "176.57.147.204", "port": 7777},
    {"id": 16, "name": "Gilbert", "ip": "176.57.147.205", "port": 7777},
    {"id": 17, "name": "Show Low", "ip": "176.57.147.206", "port": 7777},
    {"id": 18, "name": "Casa-Grande", "ip": "176.57.147.207", "port": 7777},
    {"id": 19, "name": "Page", "ip": "176.57.147.208", "port": 7777},
    {"id": 20, "name": "Sun-City", "ip": "176.57.147.209", "port": 7777},
    {"id": 21, "name": "Queen-Creek", "ip": "176.57.147.210", "port": 7777},
    {"id": 22, "name": "Sedona", "ip": "176.57.147.211", "port": 7777},
    {"id": 23, "name": "Holiday", "ip": "176.57.147.212", "port": 7777},
    {"id": 24, "name": "Wednesday", "ip": "176.57.147.213", "port": 7777},
    {"id": 25, "name": "Yava", "ip": "176.57.147.214", "port": 7777},
    {"id": 26, "name": "Faraway", "ip": "176.57.147.215", "port": 7777},
    {"id": 27, "name": "Bumble Bee", "ip": "176.57.147.216", "port": 7777},
    {"id": 28, "name": "Christmas", "ip": "176.57.147.217", "port": 7777},
    {"id": 29, "name": "Mirage", "ip": "176.57.147.218", "port": 7777},
    {"id": 30, "name": "Love", "ip": "176.57.147.219", "port": 7777},
    {"id": 31, "name": "Drake", "ip": "176.57.147.220", "port": 7777},
]

async def query_all_servers() -> Dict[int, ServerInfo]:
    """Query all Arizona RP servers and return results"""
    client = SAMPQueryClient(timeout=2.0)
    results = {}
    
    # Create tasks for all servers
    tasks = []
    for server in ARIZONA_SERVERS:
        task = client.query_server(server["ip"], server["port"])
        tasks.append((server["id"], task))
    
    # Execute all queries concurrently
    for server_id, task in tasks:
        try:
            result = await task
            results[server_id] = result
        except Exception as e:
            logger.error(f"Failed to query server {server_id}: {e}")
            results[server_id] = ServerInfo(False, 0, 0, error=str(e))
    
    return results

def format_servers_status(server_results: Dict[int, ServerInfo]) -> str:
    """Format server status for display"""
    msg = "🌐 **Серверы Arizona RP**\n\n"
    msg += "📝 **Доступность серверов:**\n\n"
    
    total_online = 0
    online_count = 0
    
    for server in ARIZONA_SERVERS:
        server_id = server["id"]
        server_name = server["name"]
        info = server_results.get(server_id, ServerInfo(False, 0, 0, error="No data"))
        
        if info.is_online:
            msg += f"✅ {server_id}. {server_name} | Онлайн: {info.players} / {info.max_players}\n"
            total_online += info.players
            online_count += 1
        else:
            error_msg = info.error if info.error else "Сервер недоступен"
            msg += f"❌ {server_id}. {server_name} | {error_msg}\n"
    
    msg += f"\n📊 **Общая статистика:**\n"
    msg += f"🎮 Всего игроков онлайн: **{total_online:,}**\n"
    msg += f"⚡ Серверов онлайн: **{online_count}/{len(ARIZONA_SERVERS)}**\n"
    
    msg += f"\n📝 Статистика игрока: /stats <ник> <ID сервера>\n"
    msg += f"💡 Пример: /stats PlayerName 1"
    
    return msg