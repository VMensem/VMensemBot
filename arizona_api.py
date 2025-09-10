"""
API client for fetching player statistics and server status from Arizona RP (Deps API)
"""

import asyncio
import aiohttp
from typing import Dict, Any, Tuple, Optional
import logging
import re
from datetime import datetime

from unified_config import API_URL, API_KEY, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)


class ArizonaRPAPIClient:
    """Client for fetching Arizona RP player information and server status"""

    def __init__(self):
        self.api_url = API_URL
        self.api_key = API_KEY
        self.timeout = REQUEST_TIMEOUT

        # Кэш для статуса серверов
        self._servers_cache: Dict[int, Dict[str, Any]] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = 300  # 5 минут

    # =============== Проверки ===============
    def validate_nickname(self, nickname: str) -> Tuple[bool, Optional[str]]:
        """Проверка ника"""
        if not nickname:
            return False, "Ник игрока не может быть пустым."
        if len(nickname) < 3:
            return False, "Ник игрока должен содержать минимум 3 символа."
        if len(nickname) > 24:
            return False, "Ник игрока не может содержать более 24 символов."
        if not re.match(r'^[a-zA-Z0-9_]+$', nickname):
            return False, "Ник может содержать только буквы, цифры и подчёркивания."
        return True, None

    def validate_server_id(self, server_id: int) -> Tuple[bool, Optional[str]]:
        """Проверка ID сервера"""
        valid_servers = list(range(1, 33)) + [200] + list(range(101, 104))
        if server_id not in valid_servers:
            return False, "Неверный ID сервера. Доступные: ПК 1–32, ViceCity (200), Мобайл 101–103"
        return True, None

    # =============== API игрока ===============
    async def fetch_player_stats(
        self, nickname: str, server_id: int
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Получение статистики игрока"""
        if not self.api_key:
            return None, "❌ API ключ не настроен. Обратитесь к администратору."

        headers = {"X-API-Key": self.api_key, "User-Agent": "MensemBot/1.0"}
        params = {"nickname": nickname, "serverId": server_id}

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

                    if "error_code" in data:
                        return None, f"❌ Ошибка API ({data.get('error_code')}): {data.get('error_message','Неизвестная ошибка')}"
                    if "error" in data:
                        return None, f"❌ Ошибка API: {data.get('error',{}).get('message','Неизвестная ошибка')}"
                    if "status" in data and data["status"] == "error":
                        return None, f"❌ Ошибка API: {data.get('error',{}).get('message','Неизвестная ошибка')}"
                    if not self._validate_response(data):
                        return None, "❌ Некорректный формат ответа от API."

                    return data, None

        except asyncio.TimeoutError:
            return None, "⏰ Превышено время ожидания ответа от API."
        except aiohttp.ClientError:
            return None, "🌐 Ошибка сетевого соединения."
        except Exception as e:
            return None, f"❌ Непредвиденная ошибка: {e}"

    def _validate_response(self, data: Dict[str, Any]) -> bool:
        """Валидация структуры ответа"""
        if not isinstance(data, dict):
            return False
        if "id" in data and "level" in data:
            return True
        if any(key in data for key in ["statistics", "account_id", "nickname"]):
            return True
        return False

    # =============== Серверы ===============
    def get_server_name(self, server_id: int) -> str:
        """Названия серверов"""
        server_names = {
            1: "Phoenix", 2: "Tucson", 3: "Scottdale", 4: "Chandler", 5: "Brainburg",
            6: "Saint Rose", 7: "Mesa", 8: "Red-Rock", 9: "Yuma", 10: "Surprise",
            11: "Prescott", 12: "Glendale", 13: "Kingman", 14: "Winslow", 15: "Payson",
            16: "Gilbert", 17: "Show Low", 18: "Casa-Grande", 19: "Page", 20: "Sun-City",
            21: "Queen-Creek", 22: "Sedona", 23: "Holiday", 24: "Wednesday", 25: "Yava",
            26: "Faraway", 27: "Bumble Bee", 28: "Christmas", 29: "Mirage", 30: "Love",
            31: "Drake", 32: "Space", 200: "ViceCity",
            101: "Mobile I", 102: "Mobile II", 103: "Mobile III"
        }
        return server_names.get(server_id, f"Server {server_id}")

    async def fetch_server_status(self, server_id: int) -> Dict[str, Any]:
        """Фейковый пример (заменить на реальный запрос к API онлайн-серверов)"""
        return {"server_id": server_id, "online": 500, "max_online": 1000, "is_online": True}

    async def fetch_all_servers_status(self) -> Dict[int, Dict[str, Any]]:
        """Получение статуса всех серверов"""
        if self._is_cache_valid() and self._servers_cache:
            return self._servers_cache.copy()

        servers_info: Dict[int, Dict[str, Any]] = {}
        server_ids = list(range(1, 33)) + [200] + list(range(101, 104))

        try:
            batch_size = 5
            for i in range(0, len(server_ids), batch_size):
                batch = server_ids[i:i + batch_size]
                tasks = [self.fetch_server_status(sid) for sid in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for sid, res in zip(batch, results):
                    if isinstance(res, Exception):
                        servers_info[sid] = {"server_id": sid, "online": 0, "max_online": 0, "is_online": False, "error": str(res)}
                    else:
                        servers_info[sid] = res

                if i + batch_size < len(server_ids):
                    await asyncio.sleep(1)

            self._servers_cache = servers_info.copy()
            self._cache_timestamp = datetime.now()

        except Exception as e:
            logger.error(f"Error fetching all servers status: {e}")

        return servers_info

    def _is_cache_valid(self) -> bool:
        if not self._cache_timestamp:
            return False
        return (datetime.now() - self._cache_timestamp).total_seconds() < self._cache_duration

    async def get_servers_info(self) -> str:
        """Формирует текст со списком серверов с онлайном"""
        servers_data = await self.fetch_all_servers_status()

        def fmt(sid: int) -> str:
            s = servers_data.get(sid, {})
            name = self.get_server_name(sid)
            if not s or not s.get("is_online", False):
                return f"🔴 [{sid:02}] {name} — Offline"
            return f"🟢 [{sid:02}] {name} — {s['online']} / {s['max_online']}"

        msg = "📊 Онлайн серверов Arizona RP\n\n"

        msg += "💻 ПК серверы (1–32):\n"
        for sid in range(1, 33):
            msg += fmt(sid) + "\n"

        msg += "\n🌆 ViceCity:\n"
        msg += fmt(200) + "\n"

        msg += "\n📱 Мобайл серверы:\n"
        for sid in range(101, 104):
            msg += fmt(sid) + "\n"

        return msg


# Глобальный клиент
arizona_api = ArizonaRPAPIClient()