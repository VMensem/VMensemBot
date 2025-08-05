#!/usr/bin/env python3
"""
Main entry point for the unified MensemBot
Supports both Telegram and Discord platforms with Arizona RP statistics
"""

import asyncio
import sys

# Import the unified bot
from unified_bot import main

if __name__ == "__main__":
    try:
        # Run the unified bot
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Боты остановлены")
    except SystemExit:
        pass
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)