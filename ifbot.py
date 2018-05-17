# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 11:58:56 2018

@author: User
"""
from telegram.ext import CommandHandler, MessageHandler, Filters
import os

#Process of interaction(how do i represent this as a decision tree? or as a class?)
#swap out handlers as appropriate? use them in if conditions - need to use functions as objs
#/start gives 2 choices, start new game, continue saved game
#pick a game: shows list of games from folder 
#game chosen, game starts



# List storing Handler objects
handlers = []

# Checks if /start has been called
isStart = False

# Checks if game is currently in progress
inProgress = False

# Command handlers
# /start wakes the bot up if it isnt already awake
def start(bot, update):
    global isStart
    
    if isStart == False:
        isStart = True
        update.message.reply_text('Hi! Use /n to choose a new game, '
                                  '/c to continue saved game')
    
    else:
        update.message.reply_text("I'm already awake! :P")
    
# Appends start command handler to list of handlers    
handlers.append(CommandHandler("start", start))

# /help gives instructions
def help(bot, update):
    update.message.reply_text('/start to wake the bot up' + '\n'
                              '/n to start a new game' + '\n'
                              '/c to continue saved game')

handlers.append(CommandHandler("help", help))

#starts a new game if bot is awake and no game is running
def n(bot, update):
    global isStart, inProgress
    
    if isStart == True:
        if inProgress == False:        
            inProgress = True
            update.message.reply_text('New game started, please choose a game')
            
            #returns list of games available
            path = "C:/Users/User/Desktop/TelegramBot/ifbot/games"
            dirs = os.listdir(path)
            for file in dirs:
                update.message.reply_text(file)

        elif inProgress == True:
            update.message.reply_text('Sorry, you are already playing a game. /end '
                                      'to end current game')

    else:
        update.message.reply_text('zzz...')
    
handlers.append(CommandHandler("n", n))

#continues saved game if bot is awake and no game is running
def c(bot, update):
    global isStart, inProgress
    
    if isStart == True:
        if inProgress == False:
            inProgress = True
            update.message.reply_text('You have chosen to continue a previous game, '
                                      'please choose a game')
            
            #returns list of saved files in folder
            path = "C:/Users/User/Desktop/TelegramBot/ifbot/saves"
            dirs = os.listdir(path)
            for file in dirs:
                update.message.reply_text(file)
            
            #save file should contain the file address of the 
            #story and all the actions taken by the user (use qwertzal)

        elif inProgress == True:
            update.message.reply_text('Sorry, you are already playing a game. /end '
                                      'to end current game')

    else:
        update.message.reply_text('zzz...')
    
    
handlers.append(CommandHandler("c", c))

#ends game if bot is awake and game is running
def end(bot, update):
    global isStart, inProgress
    
    if isStart == True:
        if inProgress == False:        
            update.message.reply_text('There is no game in progress')
            #return list of saved games

        elif inProgress == True:
            inProgress = False
            update.message.reply_text('Game ended')

    else:
        update.message.reply_text('zzz...')
    
handlers.append(CommandHandler("end", end))

# Non-command handlers
#filters out text messages
def foo(bot, update):
    global isStart
    
    if isStart == True:
        #stores the text message in string variable 'message'
        message = update.message.text
        update.message.reply_text("I don't understand " + message)
    
    else:
        update.message.reply_text('zzz')
    
handlers.append(MessageHandler(Filters.text, foo))