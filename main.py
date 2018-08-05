# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 11:48:04 2018

@author: User
"""


from telegram.ext import Updater
import logging
import ifbot

# Authentication token
# NOT SAFE
token = "568205953:AAHvWcHW_KrMuyEs28-PMjaYkRMVPGv8FCE"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    # Starts Updater
    updater = Updater(token)
    
    # Locally introduces dispatcher for easier access
    dp = updater.dispatcher
    
    # Registers handlers
    for handler in ifbot.handlers:
        dp.add_handler(handler)
        
    # Log all errors
    dp.add_error_handler(error)
        
    # Starts the bot
    updater.start_polling()
        
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    

if __name__ == '__main__':
        main()