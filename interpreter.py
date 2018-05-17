# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 22:09:06 2018

@author: User
"""

#TODO
#map opcodes to functions 
#finish the stack class and program counter
#link the stack to the memory so interpreter can execute instructions
#map instruction code to instructions

from memory import Memory
from helper import Helper

#implement program counter and stack
#map instructions to functions

class Interpreter():
    def __init__(self, file):        
        #represents story file/memory
        #need to account for decoding and encoding of data?
        self.memory = Memory(file)

        #version number of z machine
        self.ver_num = self.memory.get_ver()
        
        #set of predetermined values and functions
        self.help = Helper(self.ver_num)
        
        #parts of the z machine not included in the story file
        #define the state of play to be saved
        #maybe converted to classes?
        self.program_counter = self.memory.get_pc()
        self.stack = []
        self.routine_call_state = 0
        
# =============================================================================
# Get Methods
# =============================================================================
        
        

# =============================================================================
# End of Class
# =============================================================================

#testing code
file_name = 'C:/Users/User/Desktop/TelegramBot/ifbot/games/hhgg.z3'

#opens file in binary
file = open(file_name, "rb")

#need to write file in binary as well

#checks attributes of Memory
machine = Interpreter(file)

mem = machine.memory.get_memory()

# =============================================================================
# #tests memory and its segments
# print(mem[6:8])
# print(machine.memory.get_byte_address(mem[6:8]))
# print(machine.memory.get_dynamic(), machine.memory.get_high(), machine.memory.get_static())
# =============================================================================

# =============================================================================
# #tests the get string function
# abbrev_add = machine.help.abbrev_add
# for i in range(1):
#     offset = i*2
#     abbrev_table_add = machine.memory.get_byte_address(mem[abbrev_add:abbrev_add + 2])
#     #print('abbrev_table_add ' + str(abbrev_table_add))
#     abbrev_string_location = machine.memory.get_word_address(mem[abbrev_table_add 
#                                                          + offset:abbrev_table_add
#                                                          + offset + 2])
#     #print('abbrev_string_location ' + str(abbrev_string_location))
#     #print('get_string')
#     abbrev_list = machine.memory.get_string(abbrev_string_location)
#     #print('abbrev_list ' + str(abbrev_list))
#     abbrev_string = ''.join(abbrev_list)
#     print(abbrev_string)
# =============================================================================

#test the instruction encoding (memory.get_instr())
pc_add = machine.program_counter
for i in range(20):
    print('pc_add', pc_add)
    instr = []
    pc_add = machine.memory.get_instr(pc_add, instr)
    print('form, count, num, type, ops', instr)
