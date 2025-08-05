# Dual-Platform Arizona RP Player Information Bot

## Overview

This is a dual-platform bot that fetches player information from the Arizona RP server using the Deps API and serves them through both Discord and Telegram platforms. The bot allows users to query Arizona RP player data by providing a nickname and server ID. The application uses an asynchronous architecture to handle concurrent requests across both platforms efficiently.

## User Preferences

Preferred communication style: Simple, everyday language.
Response language: Russian (all bot responses in Russian)
Data requirement: Use authentic data from Arizona RP APIs when available, graceful error handling when API access is restricted

## System Architecture

### Bot Framework Architecture
The application implements a dual-platform approach using separate bot frameworks:
- **Discord Integration**: Uses discord.py library with commands extension for slash commands and event handling
- **Telegram Integration**: Uses aiogram library for async Telegram bot operations
- **Unified Command Interface**: Both platforms expose the same core functionality through platform-specific handlers

### Asynchronous Design Pattern
The entire application is built on asyncio for non-blocking operations:
- **Concurrent Platform Support**: Both Discord and Telegram bots run simultaneously in separate async tasks
- **Non-blocking API Calls**: External API requests use aiohttp for async HTTP operations
- **Timeout Management**: Configurable request timeouts prevent hanging operations

### Configuration Management
Centralized configuration system using environment variables:
- **Environment-based Config**: All sensitive data (tokens, API keys) loaded from environment variables
- **Validation Layer**: Built-in validation ensures all required configuration is present before startup
- **Default Values**: Sensible defaults provided for non-critical settings like timeouts and command prefixes

### Input Validation and Error Handling
Comprehensive validation system for user inputs:
- **Nickname Validation**: Enforces character limits and allowed character sets (alphanumeric + underscore)
- **Server ID Validation**: Validates against Arizona RP server IDs (Phoenix, Tucson, Scottdale, etc.)
- **Graceful Error Handling**: Platform-specific error responses with user-friendly messages in Russian

### API Client Architecture
Enhanced API client with new Depscian API integration:
- **Updated API Endpoint**: Now uses api.depscian.tech/v2/player/find (latest working endpoint)
- **X-API-Key Authentication**: Updated to new authentication header format
- **Parameter Mapping**: Supports new nickname/serverId parameter structure
- **Enhanced Error Handling**: Specific handling for IP confirmation and access restrictions, null value safety
- **Beautiful Formatting**: Rich Arizona RP-style output with progress bars, emojis, and structured display
- **Comprehensive Data**: Player stats, finances, organizations, family, VIP status, and online presence
- **Response Processing**: Handles various HTTP status codes with detailed Russian error messages
- **Server List Updated**: Now supports correct Arizona RP server structure (ПК 1-31, Мобайл 101-103)
- **Commands Available**: /stats for player information, /servers for server list display
- **Telegram Markdown Fix**: Enhanced error handling for Telegram message formatting to prevent parse errors

### Logging and Monitoring
Multi-destination logging system:
- **Console Output**: Real-time logging to stdout for development and monitoring
- **File Logging**: Persistent log storage in bot.log file with UTF-8 encoding
- **Structured Logging**: Consistent log format across all components with timestamps and log levels

### Utility Functions
Shared utility functions for data processing:
- **Message Formatting**: Functions for truncating and escaping markdown in messages
- **Input Sanitization**: Centralized validation functions used across both platforms

## External Dependencies

### Bot Platform APIs
- **Discord API**: Integration through discord.py library for Discord bot functionality
- **Telegram Bot API**: Integration through aiogram library for Telegram bot operations

### Gaming API Integration
- **Deps API**: External API for fetching Arizona RP player information
- **API Endpoint**: Default endpoint set to api.deps.su/v2/player/find
- **Authentication**: Requires API key for authenticated requests with Bearer token

### HTTP Client Libraries
- **aiohttp**: Async HTTP client for external API requests with timeout support
- **asyncio**: Core async framework for concurrent operations

### Configuration and Environment
- **Environment Variables**: All configuration loaded from environment variables for security
- **Required Variables**: DISCORD_TOKEN, TELEGRAM_TOKEN, API_KEY must be provided
- **Optional Variables**: API_URL, DISCORD_COMMAND_PREFIX, REQUEST_TIMEOUT have defaults

### Logging Dependencies
- **Python Logging**: Built-in logging module for structured log output
- **File System**: Log file persistence requires write access to application directory