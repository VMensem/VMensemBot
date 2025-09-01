import json
import os
import logging
from typing import List, Dict, Any, Optional
from config import RULES_FILE, ADMINS_FILE, BANNED_WORDS_FILE, INFO_FILE, RANK_FILE

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self._ensure_data_files_exist()

    def _ensure_data_files_exist(self):
        """Ensure all required data files exist with default values."""
        if not os.path.exists('data'):
            os.makedirs('data')

        default_files = {
            RULES_FILE: {"rules": "Правила пока не установлены."},
            RANK_FILE: {"rank": "Правила пока не установлены."},
            ADMINS_FILE: {"admins": [6766653541, 8259872971]},
            BANNED_WORDS_FILE: {"words": []},
            INFO_FILE: {"info": "Информация пока не установлена."},
            "data/rank.json": {"rank_message": "Информация о рангах пока не установлена."} 
        }

        for file_path, default_data in default_files.items():
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(default_data, f, indent=4)

    def _read_json(self, file_path: str) -> Dict[str, Any]:
        """Read data from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return {}

    def _write_json(self, file_path: str, data: Dict[str, Any]) -> bool:
        """Write data to JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False

    # -----------------------------
    # Rules
    # -----------------------------
    def get_rules(self) -> str:
        data = self._read_json(RULES_FILE)
        return data.get("rules", "Правила пока не установлены.")

    def set_rules(self, rules: str) -> bool:
        return self._write_json(RULES_FILE, {"rules": rules})

    # -----------------------------
    # Admins
    # -----------------------------
    def get_admins(self) -> dict:
        """Get admins as dict[str, username]. Always returns dict for consistency."""
        data = self._read_json(ADMINS_FILE)
        admins = data.get("admins", [])

        # Конвертируем старый формат list[int] в dict[str, username]
        if isinstance(admins, list):
            admin_dict = {str(admin_id): f"ID_{admin_id}" for admin_id in admins}
            # Обновляем JSON
            self._write_json(ADMINS_FILE, {"admins": admin_dict})
            return admin_dict

        # Если уже dict — оставляем как есть
        elif isinstance(admins, dict):
            return admins

        return {}

    def get_admin_usernames(self) -> Dict[int, str]:
        """Get dict of admin IDs to usernames."""
        admins = self.get_admins()
        return {int(k): v for k, v in admins.items()}

    def add_admin(self, admin_id: int, username: str = None) -> bool:
        """Add new admin with username."""
        admins = self.get_admins()
        admin_id_str = str(admin_id)
        if admin_id_str not in admins:
            admins[admin_id_str] = username or f"ID_{admin_id}"
            return self._write_json(ADMINS_FILE, {"admins": admins})
        return False

    def remove_admin(self, admin_id: int) -> bool:
        """Remove admin."""
        admins = self.get_admins()
        admin_id_str = str(admin_id)
        if admin_id_str in admins:
            del admins[admin_id_str]
            return self._write_json(ADMINS_FILE, {"admins": admins})
        return False

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        admins = self.get_admins()
        return str(user_id) in admins

    # -----------------------------
    # Banned words
    # -----------------------------
    def get_banned_words(self) -> List[str]:
        data = self._read_json(BANNED_WORDS_FILE)
        return data.get("words", [])

    def add_banned_word(self, word: str) -> bool:
        data = self._read_json(BANNED_WORDS_FILE)
        words = data.get("words", [])
        if word.lower() not in words:
            words.append(word.lower())
            return self._write_json(BANNED_WORDS_FILE, {"words": words})
        return False

    def remove_banned_word(self, word: str) -> bool:
        data = self._read_json(BANNED_WORDS_FILE)
        words = data.get("words", [])
        if word.lower() in words:
            words.remove(word.lower())
            return self._write_json(BANNED_WORDS_FILE, {"words": words})
        return False

    # -----------------------------
    # Info
    # -----------------------------
    def get_info(self) -> str:
        data = self._read_json(INFO_FILE)
        return data.get("info", "Информация пока не установлена.")

    def set_info(self, info: str) -> bool:
        info = info.replace("<", "&lt;").replace(">", "&gt;")
        return self._write_json(INFO_FILE, {"info": info})

    # -----------------------------
    # Rank
    # -----------------------------
    def get_rank(self) -> str:
        data = self._read_json("data/rank.json")
        return data.get("rank_message", "Информация о рангах пока не установлена.")

    def set_rank(self, message: str) -> bool:
        message = message.replace("<", "&lt;").replace(">", "&gt;")
        return self._write_json("data/rank.json", {"rank_message": message})

    # -----------------------------
    # Family chat ID
    # -----------------------------
    def get_family_chat_id(self) -> Optional[int]:
        data = self._read_json(INFO_FILE)
        family_chat = data.get("family_chat_id")
        if family_chat:
            try:
                return int(family_chat)
            except ValueError:
                return None
        return None

    def set_family_chat_id(self, chat_id: int) -> bool:
        try:
            data = self._read_json(INFO_FILE)
            data["family_chat_id"] = chat_id
            self._write_json(INFO_FILE, data)
            return True
        except Exception as e:
            logger.error(f"Error setting family chat ID: {e}")
            return False
