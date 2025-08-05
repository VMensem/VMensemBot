import os
from typing import Optional

class Config:
    """Configuration class for bot settings and API credentials"""
    
    # Discord Bot Configuration
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    
    # Telegram Bot Configuration
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    
    # Gaming API Configuration
    API_KEY: str = os.getenv("API_KEY", "")
    API_URL: str = os.getenv("API_URL", "https://api.depscian.tech/v2/player/find")
    
    # Bot Settings
    DISCORD_COMMAND_PREFIX: str = os.getenv("DISCORD_COMMAND_PREFIX", "!")
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present"""
        required_vars = [
            ("DISCORD_TOKEN", cls.DISCORD_TOKEN),
            ("TELEGRAM_TOKEN", cls.TELEGRAM_TOKEN),
            ("API_KEY", cls.API_KEY),
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            print(f"❌ Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
            return False
        
        return True

# Global config instance
config = Config()
