"""
API client for fetching player statistics from Arizona RP servers via Deps API
"""

import asyncio
import aiohttp
from typing import Dict, Any, Tuple, Optional
import logging
import re

from unified_config import API_URL, API_KEY, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

class ArizonaRPAPIClient:
    """Client for fetching Arizona RP player information from Deps API"""
    
    def __init__(self):
        self.api_url = API_URL
        self.api_key = API_KEY
        self.timeout = REQUEST_TIMEOUT

    def validate_nickname(self, nickname: str) -> Tuple[bool, Optional[str]]:
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

    def validate_server_id(self, server_id: int) -> Tuple[bool, Optional[str]]:
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
            return False, f"Неверный ID сервера. Доступные серверы Arizona RP: ПК 1-31, Мобайл 101-103"
        
        return True, None

    async def fetch_player_stats(self, nickname: str, server_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Fetch player statistics from the gaming API
        
        Args:
            nickname: Player's nickname
            server_id: Server identifier
            
        Returns:
            Tuple of (data, error_message). If successful, data contains stats and error is None.
            If failed, data is None and error contains the error message.
        """
        if not self.api_key:
            return None, "❌ API ключ не настроен. Обратитесь к администратору."
        
        headers = {
            "X-API-Key": self.api_key,
            "User-Agent": "MensemBot/1.0"
        }
        
        params = {
            "nickname": nickname,
            "serverId": server_id
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.api_url, headers=headers, params=params) as response:
                    logger.info(f"API request for {nickname} on server {server_id}: {response.status}")
                    
                    if response.status == 401:
                        return None, "❌ Ошибка авторизации API. Проверьте API ключ."
                    
                    if response.status == 429:
                        return None, "⏳ Слишком много запросов. Попробуйте позже."
                    
                    if response.status != 200:
                        return None, f"❌ Ошибка сервера API: {response.status}"
                    
                    try:
                        data = await response.json()
                    except Exception as e:
                        logger.error(f"Failed to parse JSON response: {e}")
                        return None, "❌ Ошибка обработки ответа от API."
                    
                    # Check for API-specific errors
                    if "error_code" in data:
                        error_code = data.get("error_code", "")
                        error_msg = data.get("error_message", "Неизвестная ошибка")
                        
                        if error_code == "FORBIDDEN":
                            return None, f"🔒 **Требуется подтверждение IP адреса**\n\n{error_msg}\n\n💡 Обратитесь к администратору для активации API доступа с этого сервера."
                        
                        return None, f"❌ Ошибка API ({error_code}): {error_msg}"
                    
                    if "error" in data:
                        error_msg = data.get("error", {}).get("message", "Неизвестная ошибка")
                        return None, f"❌ Ошибка API: {error_msg}"
                    
                    if "status" in data and data["status"] == "error":
                        error_msg = data.get("error", {}).get("message", "Неизвестная ошибка")
                        return None, f"❌ Ошибка API: {error_msg}"
                    
                    # Validate response structure
                    if not self._validate_response(data):
                        return None, "❌ Некорректный формат ответа от API."
                    
                    return data, None
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching stats for {nickname}")
            return None, "⏰ Превышено время ожидания ответа от API."
        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {e}")
            return None, "🌐 Ошибка сетевого соединения."
        
        except Exception as e:
            logger.error(f"Unexpected error fetching stats: {e}")
            return None, "❌ Произошла неожиданная ошибка при получении статистики."
    
    def _validate_response(self, data: Dict[str, Any]) -> bool:
        """Validate that the API response has expected structure"""
        if not isinstance(data, dict):
            return False
        
        # Check for new API structure
        if "id" in data and "level" in data:
            return True
        
        # Alternative structure check
        if any(key in data for key in ["statistics", "account_id", "nickname"]):
            return True
        
        return False
    
    def create_progress_bar(self, value, max_value: int = 100, length: int = 10) -> str:
        """Create a progress bar for health, hunger, etc."""
        if value is None:
            value = 0
        try:
            value = int(value)
            filled = int((value / max_value) * length)
            bar = "█" * filled + "░" * (length - filled)
            return f"[{bar}] {value}%"
        except (ValueError, TypeError, ZeroDivisionError):
            return f"[{'░' * length}] 0%"

    def format_money(self, amount) -> str:
        """Format money with thousand separators"""
        if amount is None:
            return "$0"
        try:
            return f"${int(amount):,}"
        except (ValueError, TypeError):
            return f"${amount}"

    def format_stats(self, data: Dict[str, Any], nickname: str, server_id: int) -> str:
        """
        Format Arizona RP player statistics for display with beautiful formatting
        
        Args:
            data: Raw API response data 
            nickname: Player nickname
            server_id: Server ID
            
        Returns:
            Formatted statistics string matching Arizona RP style
        """
        try:
            # Handle the new API response format directly
            player_data = data
            
            if not player_data or "error" in data or "id" not in player_data:
                return f"❌ Игрок '{nickname}' не найден на сервере {server_id}."
            
            # Get server name from the API response
            server_info = player_data.get("server", {})
            server_name = server_info.get("name", f"Сервер {server_id}")
            
            # Start building the formatted message
            msg = f"👤 Информация об игроке {nickname}\n\n"
            msg += f"🌐 Сервер: {server_name} (ID: {server_info.get('id', server_id)})\n\n"
            
            # Player ID and basic info
            msg += f"🆔 ID игрока: {player_data['id']}\n"
            msg += f"📱 Телефон: {player_data.get('phone_number', 'Неизвестно')}\n"
            msg += f"⏱ Отыграно часов: {player_data.get('hours_played', 0)}\n\n"
            
            # Level and Experience
            level_info = player_data.get("level", {})
            if isinstance(level_info, dict):
                current_level = level_info.get("level", 0)
                current_exp = level_info.get("current_exp", 0)
                next_exp = level_info.get("next_exp", 100)
                msg += f"🌟 Уровень: {current_level}\n"
                msg += f"📊 Опыт: {current_exp}/{next_exp}\n\n"
            elif isinstance(level_info, (int, str)):
                msg += f"🌟 Уровень: {level_info}\n\n"
            
            # Health, Hunger, Drug addiction
            health = player_data.get("health", 0)
            hunger = player_data.get("hunger", 0)
            drug_addiction = player_data.get("drug_addiction", 0)
            
            health_bar = self.create_progress_bar(health)
            hunger_bar = self.create_progress_bar(hunger)
            msg += f"❤️ Здоровье: {health_bar}\n"
            msg += f"🍗 Голод: {hunger_bar}\n"
            msg += f"💉 Наркозависимость: {drug_addiction}%\n\n"
            
            # VIP Status
            vip_info = player_data.get("vip_info", {})
            if vip_info:
                vip_level = vip_info.get("level", "None")
                add_vip = vip_info.get("add_vip", "Нет")
                msg += f"👑 VIP: {vip_level}\n"
                if add_vip != "Нет":
                    msg += f"➕ Доп. VIP: {add_vip}\n"
                msg += "\n"
            
            # Financial Information
            money_info = player_data.get("money", {})
            if money_info:
                msg += f"💰 Финансы:\n"
                total = money_info.get("total", 0)
                hand = money_info.get("hand", 0)
                bank = money_info.get("bank", 0)
                deposit = money_info.get("deposit", 0)
                donate_currency = money_info.get("donate_currency", 0)
                phone_balance = money_info.get("phone_balance", 0)
                charity = money_info.get("charity", 0)
                
                msg += f"  💵 Всего: {self.format_money(total)}\n"
                msg += f"  💴 Наличные: {self.format_money(hand)}\n"
                msg += f"  🏦 Банк: {self.format_money(bank)}\n"
                msg += f"  💼 Депозит: {self.format_money(deposit)}\n"
                msg += f"  💎 Донат валюта: {donate_currency}\n"
                msg += f"  📱 Баланс телефона: {self.format_money(phone_balance)}\n"
                msg += f"  ❤️ Благотворительность: {self.format_money(charity)}\n\n"
            
            # Job and Organization
            job = player_data.get("job", "Безработный")
            msg += f"💼 Работа: {job}\n"
            
            org_info = player_data.get("organization", {})
            if org_info:
                org_name = org_info.get("name", "Нет")
                org_rank = org_info.get("rank", "Нет")
                uniform = org_info.get("uniform", False)
                
                msg += f"🏢 Организация: {org_name}\n"
                msg += f"  🏅 Должность: {org_rank}\n"
                uniform_status = "👔 В форме" if uniform else "👕 Не в форме"
                msg += f"  {uniform_status}\n\n"
            else:
                msg += f"🏢 Организация: Нет\n\n"
            
            # Law and Order
            law_abiding = player_data.get("law_abiding", 0)
            wanted_level = player_data.get("wanted_level", 0)
            warnings = player_data.get("warnings", 0)
            
            law_bar = self.create_progress_bar(law_abiding)
            msg += f"⚖️ Законопослушность: {law_bar}\n"
            msg += f"🚨 Уровень розыска: {wanted_level}\n"
            msg += f"⚠️ Предупреждения: {warnings}\n\n"
            
            # Family information
            family_info = player_data.get("family", {})
            if family_info:
                family_name = family_info.get("name", "Неизвестно")
                family_leader = family_info.get("leader", "Неизвестно")
                member_info = family_info.get("member_info", {})
                member_rank = member_info.get("rank", 0)
                is_leader = member_info.get("is_leader", False)
                
                msg += f"👥 Семья: {family_name}\n"
                msg += f"  👑 Лидер: {family_leader}\n"
                leader_status = "Да" if is_leader else "Нет"
                msg += f"  🏆 Я лидер: {leader_status}\n"
                msg += f"  🎖️ Ранг в семье: {member_rank}\n\n"
            
            # Online Status
            status_info = player_data.get("status", {})
            if status_info:
                online = status_info.get("online", False)
                player_id = status_info.get("player_id", "Неизвестно")
                online_status = "🟢 В сети" if online else "🔴 Не в сети"
                msg += f"Статус: {online_status}\n"
                if online:
                    msg += f"🎮 ID в игре: {player_id}\n"
            
            return msg
            
        except Exception as e:
            logger.error(f"Error formatting Arizona RP stats: {e}")
            return f"❌ Ошибка при форматировании информации для игрока {nickname}."

    def get_servers_info(self) -> str:
        """Get information about all Arizona RP servers"""
        msg = "💻 ПК серверы (1-31):\n"
        msg += " 1: Phoenix\n 2: Tucson\n 3: Scottdale\n 4: Chandler\n 5: Brainburg\n 6: Saint Rose\n 7: Mesa\n 8: Red Rock\n 9: Yuma\n10: Surprise\n11: Prescott\n12: Glendale\n13: Kingman\n14: Winslow\n15: Payson\n16: Gilbert\n17: Show Low\n18: Casa Grande\n19: Page\n20: Sun City\n21: Queen Creek\n22: Sedona\n23: Holiday\n24: Wednesday\n25: Yava\n26: Faraway\n27: Bumble Bee\n28: Christmas\n29: Mirage\n30: Love\n31: Drake\n\n"
        
        msg += "📱 Мобайл серверы:\n"
        msg += "101: Mobile 1\n102: Mobile 2\n103: Mobile 3\n\n"
        
        msg += "Использование: /stats <ник> <ID сервера>\n"
        msg += "Пример: /stats PlayerName 1"
        
        return msg

# Global API client instance
arizona_api = ArizonaRPAPIClient()