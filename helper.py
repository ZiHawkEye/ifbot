# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 17:21:11 2018

@author: User
"""
# records most predetermined values 
# also includes data structures as objects
# should this be the base class? that other classes inherit from?
from op_table import *

class Helper():
    def __init__(self, ver_num):
        # version number
        self.ver_num = ver_num
        
        # memory addresses
        # memory addresses for starts and ends of dynamic, static,
        # high memory
        self.dyn_end_add = int.from_bytes(b'\x0e', byteorder='big')
        self.hi_start_add = int.from_bytes(b'\x04', byteorder='big')
        
        # memory address storing byte address to initialize program counter
        self.pc_add = int.from_bytes(b'\x06', byteorder='big')
        
        # address for abbrev table
        self.abbrev_add = int.from_bytes(b'\x18', byteorder='big')
        
        # address for object table
        self.obj_add = int.from_bytes(b'\x0a', byteorder='big')

        # address for dictionary
        self.dict_add = int.from_bytes(b'\x08', byteorder='big')
        
        # address for global variables
        self.gvar_add = int.from_bytes(b'\x0c', byteorder='big')

        # (only for versions 6 and 7) the routine and string offsets
        if self.ver_num in [6,7]:
            self.ro_add = int.from_bytes(b'\x28', byteorder='big')            
            self.so_add = int.from_bytes(b'\x2a', byteorder='big')
        
        
        # zscii strings - need to introduce more for different zmachine vers
        self.lower = '      abcdefghijklmnopqrstuvwxyz'
        self.upper = '      ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if self.ver_num == 1:
            self.punct = """       0123456789.,!?_#'"/\<-:()"""
        else:
            self.punct = """       ^0123456789.,!?_#'"/\-:()"""
        
        
        # op_table - distinguishes between z machine versions
        self.op_table = make_table(self.ver_num)

# =============================================================================
# Helper Classes
# =============================================================================

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
    # initiated by ver num, kind, op_num
    # should contain mnemonic, operands and args
    def __init__(self, name, operands, str_arg, res_arg, is_reversed, offset):
        # use * before an iterable to expand it before a function call
        self.name = name
        self.arguments = []
        if str_arg != None:
            self.arguments.append(str_arg)
        elif res_arg != None:
            self.arguments.append(res_arg)
        elif is_reversed != None and offset != None:
            self.arguments.append(is_reversed)
            self.arguments.append(offset)
        self.operands = operands

class Object():
    def __init__(self, flags, parent, sibling, child, properties):
        self.flags = flags[:]
        self.parent = parent
        self.sibling = sibling
        self.child = child
        self.properties = properties
