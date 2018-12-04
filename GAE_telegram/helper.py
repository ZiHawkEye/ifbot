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
        self.dyn_end_add = 0x0e
        self.hi_start_add = 0x04
        
        # memory address storing byte address to initialize program counter
        self.pc_add = 0x06
        
        # address for abbrev table
        self.abbrev_add = 0x18
        
        # address for object table (starts with property defaults table, then lists objects)
        self.obj_add = 0x0a
        self.obj_size = 9 if self.ver_num in [1, 2, 3] else 14

        # address for dictionary
        self.dict_add = 0x08
        
        # address for global variables
        self.gvar_add = 0x0c

        # (only for versions 6 and 7) the routine and string offsets
        if self.ver_num in [6,7]:
            self.ro_add = 0x28          
            self.so_add = 0x2a
        
        
        # zscii strings - need to introduce more for different zmachine vers
        self.lower = '      abcdefghijklmnopqrstuvwxyz'
        self.upper = '      ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if self.ver_num == 1:
            self.punct = """       0123456789.,!?_#'"/\<-:()"""
        else:
            self.punct = """       ^0123456789.,!?_#'"/\-:()"""
        self.char_map = [self.lower,
                         self.upper,
                         self.punct]
        
        # op_table - distinguishes between z machine versions
        self.op_table = make_table(self.ver_num)

# =============================================================================
# Helper Classes
# =============================================================================
class Instruction():
    # initiated by ver num, kind, op_num
    # should contain mnemonic, operands and args
    def __init__(self, name, types, op_types, operands, str_arg, res_arg, is_reversed, offset):
        # use * before an iterable to expand it before a function call
        self.name = name
        self.arguments = []
        self.args = {}
        if str_arg != None:
            self.args["string"] = str_arg
            self.arguments.append(str_arg)
        if res_arg != None:
            self.args["result"] = res_arg
            self.arguments.append(res_arg)
        if is_reversed != None and offset != None:
            self.args["is_reversed"] = is_reversed
            self.args["offset"] = offset
            self.arguments.append(is_reversed)
            self.arguments.append(offset)
        self.operands = operands
        self.types = types
        self.op_types = op_types

class Object():
    def __init__(self, flags, parent, sibling, child, properties_add):
        self.flags = flags[:]
        self.parent = parent
        self.sibling = sibling
        self.child = child
        self.properties_add = properties_add
