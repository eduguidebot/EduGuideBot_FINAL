#!/usr/bin/env python3
"""
EduGuideBot - Main application entry point.
This script initializes and runs the Telegram bot for educational recommendations.
"""
import os
import logging
from dotenv import load_dotenv
from src.bot.app import main as run_bot

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the EduGuideBot application.
    """
    # Load environment variables
    load_dotenv()
    
    # Check if required environment variables are set
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        logger.error("TELEGRAM_BOT_TOKEN not set in .env file. Bot cannot start.")
        return
    
    # Check if GitHub Pages URL is set
    github_pages_url = os.getenv("GITHUB_PAGES_URL")
    if not github_pages_url:
        logger.warning("GITHUB_PAGES_URL not set in .env file. Web features may not work correctly.")
    
    # Run the bot
    logger.info("Starting EduGuideBot...")
    run_bot()

if __name__ == "__main__":
    main() 