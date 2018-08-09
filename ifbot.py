# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 11:58:56 2018

@author: User
"""
from telegram.ext import CommandHandler, MessageHandler, Filters
import os
import sys
from io import StringIO
from interpreter import Interpreter

#swap out handlers as appropriate? use them in if conditions - need to use functions as objs

# List storing Handler objects
handlers = []

# Checks if /start has been called
isStart = False

# Checks if game is currently in progress
inProgress = False

machine = None
game = None
f = StringIO()
f1 = sys.stdin

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
    global isStart, game
    
    if isStart == True:
        if game == None:        
            update.message.reply_text('New game started, please choose a game')
            
            #returns list of games available
            path = '/Users/kaizhe/Desktop/Telegram/ifbot/games/'
            dirs = os.listdir(path)
            for file in dirs:
                update.message.reply_text(file)
        else:
            update.message.reply_text('Sorry, you are already playing a game. /end '
                                      'to end current game')
    else:
        update.message.reply_text('zzz...')
    
handlers.append(CommandHandler("n", n))

#continues saved game if bot is awake and no game is running
def c(bot, update):
    global isStart, game
    
    if isStart == True:
        if game == None:
            update.message.reply_text('You have chosen to continue a previous game, '
                                      'please choose a game')
            
            #returns list of saved files in folder
            path = '/Users/kaizhe/Desktop/Telegram/ifbot/saves/'
            dirs = os.listdir(path)
            for file in dirs:
                update.message.reply_text(file)
            
            #save file should contain the file address of the 
            #story and all the actions taken by the user (use qwertzal)
        else:
            update.message.reply_text('Sorry, you are already playing a game. /end '
                                      'to end current game')
    else:
        update.message.reply_text('zzz...')
    
    
handlers.append(CommandHandler("c", c))

#ends game if bot is awake and game is running
def end(bot, update):
    global isStart, game
    
    if isStart == True:
        if game == None:        
            update.message.reply_text('There is no game in progress')
            #return list of saved games

        else:
            game = None
            update.message.reply_text('Game ended')
    else:
        update.message.reply_text('zzz...')
    
handlers.append(CommandHandler("end", end))

# Non-command handlers
#filters out text messages
def foo(bot, update):
    global isStart, machine, game, f, f1
    message = update.message.text
    if isStart == True:
        if game == None:
            path = '/Users/kaizhe/Desktop/Telegram/ifbot/games/'
            dirs = os.listdir(path)
            if message in dirs:
                sys.stdin = f
                game = message
                file_name = path + game
                file = open(file_name, "rb")
                machine = Interpreter(file, '')
                try:
                    machine.start(0)
                except KeyboardInterrupt:
                    update.message.reply_text(machine.o)
                    sys.stdin = f1
                except:
                    sys.stdin = f1
                    raise
        else:
            sys.stdin = f
            f.seek(0)
            f.write(message + '\n')
            f.seek(0)
            machine.o = ''
            try:
                machine.start(0, True)
            except KeyboardInterrupt:
                update.message.reply_text(machine.o)
                sys.stdin = f1
            except:
                sys.stdin = f1
                raise
    else:
        update.message.reply_text('zzz')
    
handlers.append(MessageHandler(Filters.text, foo))