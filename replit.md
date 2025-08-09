# Overview

MensemBot is a unified multi-platform bot supporting both Telegram and Discord, built with Python using aiogram and discord.py frameworks. The bot serves as a comprehensive tool for community management and gaming statistics, providing features like moderation, rules management, banned word filtering, user rank information, admin controls, and Arizona RP player statistics lookup. It's designed to help maintain order and provide information in gaming community chats, specifically for "Mensem Family" related to SAMP (San Andreas Multiplayer) and Arizona RP servers.

## Key Features

- **Multi-Platform Support**: Simultaneous operation on Telegram and Discord
- **Community Management**: Rules, ranks, admin controls, banned words filtering
- **Arizona RP Integration**: Player statistics lookup via Deps API
- **24/7 Operation**: Continuous running with Flask keep-alive server
- **Modular Architecture**: Separated concerns across multiple specialized files

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Core Frameworks**: 
  - aiogram (asynchronous Telegram Bot API framework)
  - discord.py (Discord API framework)
- **Architecture Pattern**: Unified event-driven command handling with custom filters
- **Multi-Platform Design**: Single codebase supporting both platforms simultaneously
- **Deployment**: Designed for cloud hosting with Flask keep-alive functionality

## Data Management
- **Storage**: JSON file-based data persistence
- **Data Structure**: Separate JSON files for different data types (rules, admins, banned words, info, ranks)
- **Location**: All data stored in `/data` directory
- **Manager Pattern**: Centralized DataManager class handles all file operations

## Authentication & Authorization
- **Role-Based Access**: Three-tier permission system (Creator > Admin > User)
- **Custom Filters**: IsAdmin and IsCreator filters for command access control
- **Admin Management**: Dynamic admin list stored in JSON file
- **Creator Privileges**: Hardcoded creator ID with highest permissions

## Command Structure
- **Public Commands**: /start, /help, /rules, /rank, /info, /staff, /id, /shop
- **Arizona RP Commands**: /stats <nickname> <server_id>, /servers
- **Admin Commands**: /setrules, /setinfo, /setrank, /addword, /unword, /words, /addadmin, /unadmin
- **Creator Commands**: /botstats (bot statistics access)
- **Platform Differences**: Discord uses ! prefix (!stats, !help), Telegram uses /
- **Private vs Group**: Some commands restricted to private messages

## Message Processing
- **Content Filtering**: Banned words system with automatic detection
- **Template System**: Predefined message templates in config
- **Markdown Support**: HTML parsing mode for formatted messages
- **Inline Keyboards**: Dynamic button generation for user interactions

## Application Logic
- **Modular Design**: Separated concerns across multiple files
- **Error Handling**: Comprehensive logging and exception management
- **Reconnection Logic**: Built-in bot reconnection with retry attempts
- **Threading**: Separate thread for keep-alive web server

# External Dependencies

## Core Dependencies
- **aiogram**: Telegram Bot API framework for Python
- **discord.py**: Discord API framework for Python
- **aiohttp**: Asynchronous HTTP client for API requests
- **Flask**: Web server for keep-alive functionality

## Infrastructure
- **Environment Variables**: Bot token stored securely in environment
- **File System**: Local JSON file storage for persistence
- **Web Server**: Flask-based keep-alive server on port 5000
- **Logging**: File and console logging for monitoring

## Platform Integration
- **Telegram Integration**: Full integration with Telegram Bot API, group management, user tracking
- **Discord Integration**: Full integration with Discord API, guild management, embed support
- **Arizona RP API**: Integration with Deps API for player statistics
- **Unified Commands**: Same functionality across both platforms with platform-specific formatting
- **Cross-Platform Features**: Shared data management and admin controls

## Hosting Environment
- **Cloud Platform**: Designed for platforms like Replit, Heroku
- **Port Configuration**: Web server on port 5000 for keep-alive
- **Environment Setup**: Requires BOT_TOKEN, optionally DISCORD_TOKEN and API_KEY
- **Continuous Operation**: Keep-alive mechanism prevents sleeping
- **Multi-Platform Deployment**: Single deployment supports both Telegram and Discord

## Recent Changes (August 2025)

### Single Session and Auto-Restart System (August 9, 2025)
- Implemented SessionManager to prevent multiple bot instances
- Added RestartScheduler for automatic restart every 5 hours
- Enhanced bot stability with proper session management
- Added uptime monitoring and restart countdown in /botstats
- Improved logging and error handling for autonomous operation

### Servers Command Update (August 9, 2025)
- Updated /servers command across all platform implementations
- Replaced simple server numbering with detailed server names (1: Phoenix, 2: Tucson, etc.)
- Added 🌐 emoji to "Серверы Arizona RP:" header for visual consistency
- Fixed token validation to strip whitespace from environment variables
- Improved error handling for invalid tokens containing spaces

## Previous Changes

### Rank Application System (August 7, 2025)
- Fixed /shop functionality - now processes rank applications instead of shop requests
- Added inline keyboard buttons (Выдано/Отказано) for family leadership
- Rank applications sent to family leadership chat with approval buttons
- Creator receives only notification messages, not full applications
- Added callback handler for rank approval/rejection with user notifications
- Updated SHOP_HELP_MESSAGE to reflect rank application process

### Idea System Improvements (August 7, 2025)
- /idea command sends full message to family leadership chat
- Creator receives only notification "Новая идея в руководстве семьи!"
- Streamlined notification system to reduce creator message volume

## Previous Changes

### GameStatFinder Integration
- Successfully integrated GameStatFinder.zip functionality
- Added Arizona RP player statistics lookup via Deps API
- Implemented unified API client with validation and error handling
- Added /stats and /servers commands for both platforms

### Multi-Platform Architecture
- Unified bot architecture supporting both Telegram and Discord
- Created separate Discord bot handlers with embed support
- Maintained existing Telegram functionality while adding Discord support
- Implemented platform-specific command formatting and error handling

### Configuration Updates
- Updated configuration system to support multiple platforms
- Added validation for optional API keys (DISCORD_TOKEN, API_KEY)
- Maintained backward compatibility with existing Telegram-only setup
- Enhanced logging and monitoring for dual-platform operation

### Discord Interactions Support (August 2025)
- Added Discord Interactions Endpoint URL support as alternative to WebSocket
- Created discord_interactions.py for HTTP webhook handling
- Implemented slash commands with embed responses
- Added health check endpoint for monitoring
- Enhanced Flask server with Discord webhook routes
- Reduced resource consumption by eliminating persistent WebSocket connection