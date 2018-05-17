# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 15:58:27 2018

@author: User
"""

class Stack:
    def __init__(self):
        #a stack is a stack of frames
        #each frame consists of a program counter, up to 15 local variables and
        #a routine stack and some admin info
        #on initialization a single frame is put on the call stack 
        #(ie the main is the bottom frame)
        #when a routine is called a new frame is pushed on top
        #upon return, the top frame is popped
        #only the top frame can be modified and processed
        
        
        #a frame consists of the following elements
        #program counter containing mem add where next instr is stored 
        #(can also be treated as the end of the current instruction?)
        #routine stack used to store values within a routine, cannot be used to
        #pass values from one routine to another
        #it is an error to pull a word from an empty routine stack
        #local variables 
        
        #in v3, each frame also contains the number of values passed with the call
        #that created this frame 
        #in v5, each fram also contains the numbr of values passed with the call
        #that created this frame (used to implement the check_arg_count instruction)
        
        
        #in v5 a frame on the call stack can be tagged with a word, called the frame pointer;
        #at any time, all frame pointers on the stack must be different
        #a frame pointer is created by the catch instruction, and is removed when its frame is 
        #removed from the call stack
        #frame pointers are used in instructions catch and throw
        #the call stack has a link to a save file outside the Z machine
        
        
        #size of the routine stack should be the num of local variables,
        #plus length of routine stack plus 4
        
        #total size of frames on call stack should be less than 1020
        