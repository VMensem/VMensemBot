import re
from typing import Tuple, Optional

def validate_nickname(nickname: str) -> Tuple[bool, Optional[str]]:
    """
    Validate player nickname format
    
    Args:
        nickname: Player nickname to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not nickname:
        return False, "Ник игрока не может быть пустым."
    
    if len(nickname) < 3:
        return False, "Ник игрока должен содержать минимум 3 символа."
    
    if len(nickname) > 24:
        return False, "Ник игрока не может содержать более 24 символов."
    
    # Check for valid characters (letters, numbers, underscore)
    if not re.match(r'^[a-zA-Z0-9_]+$', nickname):
        return False, "Ник может содержать только буквы, цифры и подчёркивания."
    
    return True, None

def validate_server_id(server_id: int) -> Tuple[bool, Optional[str]]:
    """
    Validate server ID for Arizona RP
    
    Args:
        server_id: Server ID to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Arizona RP server IDs (ПК серверы 1-31, мобайл 101-103)
    valid_servers = {}
    # ПК серверы
    for i in range(1, 32):  # Серверы с 1 по 31
        valid_servers[i] = f"ПК-{i}"
    # Мобайл серверы
    for i in range(101, 104):  # Серверы 101, 102, 103
        valid_servers[i] = f"Мобайл-{i}"
    
    if server_id not in valid_servers:
        server_list = "\n".join([f"{id}: {name}" for id, name in sorted(valid_servers.items())])
        return False, f"Неверный ID сервера. Доступные серверы Arizona RP:\n{server_list}"
    
    return True, None

def truncate_message(message: str, max_length: int = 2000) -> str:
    """
    Truncate message to fit platform limits
    
    Args:
        message: Message to truncate
        max_length: Maximum allowed length
        
    Returns:
        Truncated message if needed
    """
    if len(message) <= max_length:
        return message
    
    return message[:max_length - 3] + "..."

def escape_markdown(text: str) -> str:
    """
    Escape markdown characters in text
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    # Characters that need escaping in Discord markdown
    escape_chars = ['*', '_', '`', '~', '\\', '|']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text
