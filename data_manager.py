import json
import os
from typing import List, Dict, Any
from config import RULES_FILE, ADMINS_FILE, BANNED_WORDS_FILE, INFO_FILE, SCRIPTS_FILE

class DataManager:
    def __init__(self):
        self._ensure_data_files_exist()

    def _ensure_data_files_exist(self):
        """Ensure all required data files exist with default values."""
        if not os.path.exists('data'):
            os.makedirs('data')

        default_files = {
            RULES_FILE: {"rules": "Правила пока не установлены."},
            ADMINS_FILE: {"admins": []},
            BANNED_WORDS_FILE: {"words": []},
            INFO_FILE: {"info": "Информация пока не установлена."},
            SCRIPTS_FILE: {"scripts": []},
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

    def get_rules(self) -> str:
        """Get current rules."""
        data = self._read_json(RULES_FILE)
        return data.get("rules", "Правила пока не установлены.")

    def set_rules(self, rules: str) -> bool:
        """Set new rules."""
        return self._write_json(RULES_FILE, {"rules": rules})

    def get_admins(self) -> List[int]:
        """Get list of admin IDs."""
        data = self._read_json(ADMINS_FILE)
        return data.get("admins", [])

    def add_admin(self, admin_id: int) -> bool:
        """Add new admin."""
        data = self._read_json(ADMINS_FILE)
        admins = data.get("admins", [])
        if admin_id not in admins:
            admins.append(admin_id)
            return self._write_json(ADMINS_FILE, {"admins": admins})
        return False

    def remove_admin(self, admin_id: int) -> bool:
        """Remove admin."""
        data = self._read_json(ADMINS_FILE)
        admins = data.get("admins", [])
        if admin_id in admins:
            admins.remove(admin_id)
            return self._write_json(ADMINS_FILE, {"admins": admins})
        return False

    def get_banned_words(self) -> List[str]:
        """Get list of banned words."""
        data = self._read_json(BANNED_WORDS_FILE)
        return data.get("words", [])

    def add_banned_word(self, word: str) -> bool:
        """Add new banned word."""
        data = self._read_json(BANNED_WORDS_FILE)
        words = data.get("words", [])
        if word.lower() not in words:
            words.append(word.lower())
            return self._write_json(BANNED_WORDS_FILE, {"words": words})
        return False

    def remove_banned_word(self, word: str) -> bool:
        """Remove banned word."""
        data = self._read_json(BANNED_WORDS_FILE)
        words = data.get("words", [])
        if word.lower() in words:
            words.remove(word.lower())
            return self._write_json(BANNED_WORDS_FILE, {"words": words})
        return False

    def get_info(self) -> str:
        """Get current info."""
        data = self._read_json(INFO_FILE)
        return data.get("info", "Информация пока не установлена.")

    def set_info(self, info: str) -> bool:
        """Set new info."""
        info = info.replace("<", "&lt;").replace(">", "&gt;")
        return self._write_json(INFO_FILE, {"info": info})

    def get_scripts(self) -> List[str]:
        """Get list of scripts."""
        data = self._read_json(SCRIPTS_FILE)
        return data.get("scripts", [])

    def add_script(self, script: str) -> bool:
        """Add new script."""
        data = self._read_json(SCRIPTS_FILE)
        scripts = data.get("scripts", [])
        scripts.append(script)
        return self._write_json(SCRIPTS_FILE, {"scripts": scripts})

    def remove_script(self, index: int) -> bool:
        """Remove script by index."""
        try:
            data = self._read_json(SCRIPTS_FILE)
            scripts = data.get("scripts", [])
            print(f"Current scripts before removal: {scripts}")  # Debug log

            if 0 <= index < len(scripts):
                removed_script = scripts.pop(index)
                print(f"Removing script at index {index}: {removed_script}")  # Debug log
                success = self._write_json(SCRIPTS_FILE, {"scripts": scripts})
                print(f"Write operation success: {success}")  # Debug log
                return success
            else:
                print(f"Invalid index {index} for scripts list of length {len(scripts)}")  # Debug log
                return False
        except Exception as e:
            print(f"Error in remove_script: {e}")  # Debug log
            return False

    def get_rank_message(self) -> str:
        """Get rank message."""
        data = self._read_json("data/rank.json")
        return data.get("rank_message", "Информация о рангах пока не установлена.")

    def set_rank_message(self, message: str) -> bool:
        """Set rank message."""
        message = message.replace("<", "&lt;").replace(">", "&gt;")
        return self._write_json("data/rank.json", {"rank_message": message})