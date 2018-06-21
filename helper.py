# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 17:21:11 2018

@author: User
"""
#records most predetermined values and distinguishes between z machine versions
#also includes helper functions
#should this be the base class? that other classes inherit from?
from op_table import *

class Helper():
    def __init__(self, ver_num):
        #version number
        self.ver_num = ver_num
        
        #memory addresses
        #memory addresses for starts and ends of dynamic, static,
        #high memory
        self.dyn_end_add = int.from_bytes(b'\x0e', byteorder='big')
        self.hi_start_add = int.from_bytes(b'\x04', byteorder='big')
        
        #memory address storing byte address to initialize program counter
        self.pc_add = int.from_bytes(b'\x06', byteorder='big')
        
        #address for abbrev table
        self.abbrev_add = int.from_bytes(b'\x18', byteorder='big')
        
        #address for dictionary
        self.dict_add = int.from_bytes(b'\x08', byteorder='big')
        
        #(only for versions 6 and 7) the routine and string offsets
        if self.ver_num in [6,7]:
            self.ro_add = int.from_bytes(b'\x28', byteorder='big')            
            self.so_add = int.from_bytes(b'\x2a', byteorder='big')
        
        
        #zscii strings - need to introduce more for different zmachine vers
        self.lower = '      abcdefghijklmnopqrstuvwxyz'
        self.upper = '      ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if self.ver_num == 1:
            self.punct = """       0123456789.,!?_#'"/\<-:()"""
        else:
            self.punct = """       ^0123456789.,!?_#'"/\-:()"""
        
        
        #op_table - distinguishes between z machine versions
        self.op_table = make_table(self.ver_num)

# =============================================================================
# Helper Functions
# =============================================================================

# =============================================================================
# get_string
# =============================================================================

    #functions to check for special codes - needed in get_string
    #space
    def check_space(self, zchar, shift):
        if zchar == 0:
            return True
            
        else:
            return False
            
    #shift to uppercase
    def check_upper(self, zchar, shift):
        if self.ver_num in [1, 2]:
            if zchar in [2, 3, 4, 5]:
                return True
            else:
                return False
                
        elif self.ver_num in [3, 4, 5, 6, 7, 8]:
            if zchar == 4:
                return True
            else:
                return False
                
    #shift to punctuation
    def check_punct(self, zchar, shift):
        # CHECK AGAIN
        if self.ver_num in [1, 2]:
            if zchar in [2, 3, 4, 5]:
                return True
            else:
                return False
               
        elif self.ver_num in [3, 4, 5, 6, 7, 8]:
            if zchar in [4, 5]:
                return True
            else:
                return False
        
    #newline
    def check_newline(self, zchar, shift):
        if self.ver_num in [1]:
            if zchar == 1:
                return True
            else:
                return False
                
        elif self.ver_num in [2, 3, 4, 5, 6, 7, 8]:
            if zchar == 7 and shift == 2:
                return True
            else:
                return False
            
    #abbreviated words
    def check_abbrev(self, zchar, shift):
        if self.ver_num in [2]:
            if zchar == 1:
                return True
            else:
                return False
            
        elif self.ver_num in [3, 4, 5, 6, 7, 8]:
            if zchar in [1, 2, 3]:
                return True
            else:
                return False
            
        else:
            return False
        
    #literal output character
    def check_output(self, zchar, shift):
        if zchar == 6 and shift == 2:
            return True
        else:
            return False

# =============================================================================
#  Table 2: summary of the ZSCII rules 0 	null 	Output
# 1-7 	---- 	
# 8 	delete 	Input
# 9 	tab (V6) 	Output
# 10 	---- 	
# 11 	sentence space (V6) 	Output
# 12 	---- 	
# 13 	newline 	Input/Output
# 14-26 	---- 	
# 27 	escape 	Input
# 28-31 	---- 	
# 32-126 	standard ASCII 	Input/Output
# 127-128 	---- 	
# 129-132 	cursor u/d/l/r 	Input
# 133-144 	function keys f1 to f12 	Input
# 145-154 	keypad 0 to 9 	Input
# 155-251 	extra characters 	Input/Output
# 252 	menu click (V6) 	Input
# 253 	double-click (V6) 	Input
# 254 	single-click 	Input
# 255-1023 	---- 	
# 3.8.1
# 
# The codes 256 to 1023 are undefined, so that for all
#  practical purposes ZSCII is an 8-bit unsigned code. 
# =============================================================================

        
# =============================================================================
# get_instr        
# =============================================================================

class Instruction():
    #initiated by ver num, kind, op_num
    #should contain mnemonic, operands and args
    def __init__(self, name, operands, str_arg, res_arg, br_arg, is_reversed, offset):
        # CHECK
        # use * before an iterable to expand it before a function call
        self.name = name
        self.operands = operands
        self.str_arg = str_arg
        self.res_arg = res_arg
        self.br_arg = br_arg
        self.is_reversed = is_reversed
        self.offset = offset