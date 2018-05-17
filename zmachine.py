# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 14:23:58 2018

@author: User
"""

# =============================================================================
# PLEASE REFER TO INTERPRETER.PY FOR A MORE MODULARISED VERSION
# I STOPPED AFTER IMPLEMENTING GET_STRING
# =============================================================================

# =============================================================================
# THINGS ACCOMPLISHED
# LOAD MEMORY
# SEGMENT MEMORY
# GET NUM
# GET STRING WITHOUT ENCODING 10BIT LITTLE ENDIAN LITERAL OUTPUT CHARS
# GET BYTE ADDRESS
# GET WORD ADDRESS
# GET PACKED ADDRESS
# OTHER GET METHODS
# =============================================================================

# =============================================================================
# how to read the file: map the file's data and notation to the corresponding data
# structures and operations
# zmachine does not include parser
# 
#  zcode documentation
#  http://inform-fiction.org/zmachine/standards/z1point1/index.html
# save standard quetzal
# 
# Z machine is a design for an imaginary computer
# 
# all data(memory addresses, arithmetic, words) is stored 
# in chunks of 2 bytes (2 ** 16 permutations, 16 bits)
# 
# the story file is effectively the memory of the z machine, storing variables and 
# instructions to be executed by the z machine
# 
# z machine consists of a program counter, stack and routine call state
# 
# programs are divided into routines - the pc will point to the current routine
# some instructions require the z machine to call a new routine, after which it will return
# to the previous routine - this requires a stack to keep track of its previous position
# 
# stack(RAM) is a second bank of memory separate from the main one, is initially empty
# values are added to or taken from the top of the stack, also stores local variables
# 
# z machine maintains special structures inside memory
# header at the bottom of memory, has details on program and the rest of memory
# dictionary, list of English words program expects that it might want to read from keyboard
# object tree, arrangement of chunks of memory called objects
# 
# in adventure games
# dictionary: holds names of items and verbs 
# objects: places and artifacts of the game, each object has a parent, sibling and child
# 
# Example object tree:
#      West of House
# 
#     You are standing in an open field west of a white house, with a boarded front door. There is a small mailbox here.
# 
#     >open mailbox
# 
#     Opening the small mailbox reveals a leaflet.
# 
# [ 41] ""
# . [ 68] "West of House"
# .  . [ 21] "you"
# .  . [239] "small mailbox"
# .  .  . [ 80] "leaflet"
# .  . [127] "door"
# 
# object 41 is a dummy obj to contain all rooms or locations
# object 41 is parent to [you, small mailbox, door]. items in the list are siblings
# small mailbox is parent to leaflet
# 
# objects have variables (attributes and properties) 
# mailbox object:
# 239. Attributes: 30, 34
#      Parent object:  68  Sibling object: 127  Child object:  80
#      Property address: 2b53
#          Description: "small mailbox"
#           Properties:
#               [49] 00 0a 
#               [46] 54 bf 4a c3 
#               [45] 3e c1 
#               [44] 5b 1c 
# 
# 
# Story files consists of a snapshot of main memory. processors run story file
# with an empty stack and a pc value set according to info in story's header
# many structures in memory(dictionary and object tree) have to already be setup
# first byte of story file at memory address 0 contains the version number of Z
# machine to be used
# 
# =============================================================================
from values import Values

#TODO
#INCLUDE CHARS FOR 10 BIT LITERAL OUTPUT CHARS
#START OPCODES AND ROUTINES ENCODING

#class zmachine refers to the CPU
#make memory, call stack, io card, rand num, sound card, video card
#timer, save memory, mouse all classes

#in memory, convert raw data (bytes) into data structures to be returned to the PC
#how to pass opcodes and arguments?

class ZMachine():
    def __init__(self, file):
        #initialization
        #memory initialized
        #number of bits and bytes in the header are written, depending on z machine
        #includes most of teh bits marked IROM in table 3 in the appendix
        #all components are initialized
        
        #call stack is made to contain a single frame, containing in v1-5
        #a pc set to the byte address in the header word at index 6
        #no local variables
        #empty routine stack
        
        #in v6 execution begins at a routine of which the packed routine address
        #is stored at index 6
        #pc set to that address + 1
        #number of local variables found in the byte at that address, all 
        #initialized to 0
        #empty routine stack
        
        
        #determines endianness of bits - big
        #bits are numbered from right to left, counting from zero
        #bit with lowest number is least significant
        self.order = 'big'        
        
        #parts of the z machine not included in the story file
        self.stack = []
        self.program_counter = 0
        self.routine_call_state = 0

        
        #data from the story file will be read into memory
        self.memory = self.load_memory(file)
        
        #version number of z machine to be used: always the first BYTE of the story file
        self.ver_num = self.get_ver()
       
        #initiates object containing predetermined values
        self.val = Values(self.ver_num)

        #variables containing memory indexes of 'memory' denoting the start and end of each 
        #memory segment
        #dynamic memory starts at 0x00 to BYTE address stored at 0x0e 
        #in the header(defined as first 64 bytes in the story file)
        self.dynamic = []
        
        #static follows immediately after dynamic,
        #must end by address 0xffff or end of file, whichever is lower
        self.static = []
        
        #high memory begins at the BYTE address stored at 0x04 and 
        #continues to the end of the file
        #may overlap with static memory
        self.high = []

        self.segment_mem()

        
        
# =============================================================================
# Set Methods
# =============================================================================
    #loads the story file into 'memory'
    def load_memory(self, file):
        #reads the file in 1 byte elements into 'memory' list and closes the file
        memory = []
        
        try:
            while True:
                byte = file.read(1)
                memory.append(byte)
                if not byte:
                    break
                
        finally:
            file.close()
        
        return memory



    def segment_mem(self):
        #sorts 'memory' into dynamic, static and high
        #start and end of dynamic
        dstart = 0
        
        #converts 0x0e to index and gets byte address(2 bytes)
        address = self.val.dyn_end_add
        dend = self.get_byte_address(self.memory[address:address + 2])

                
        #start and end of static
        sstart = dend
        
        if len(self.memory) - 1 < 65535:
            send = len(memory) - 1
        else:
            send = 65535

        
        #start and end of high
        #converts 0x04 to index and gets byte address(2 bytes) 
        address = self.val.hi_start_add
        hstart = self.get_byte_address(self.memory[address: address + 2])        
        
        hend = len(self.memory) - 1

        
        #marks the start and end of each segment of memory
        self.dynamic = [dstart, dend]
        self.static = [sstart, send]
        self.high = [hstart, hend]

 
# =============================================================================
# Get Methods
# =============================================================================
    def get_memory(self):
        return self.memory
    
    def get_dynamic(self):
        return self.dynamic
    
    def get_static(self):
        return self.static
    
    def get_high(self):
        return self.high
    
    def get_ver(self):
        return self.get_int(self.memory[0])
        
# =============================================================================
# Helper Functions
# =============================================================================
# =============================================================================
# Data Structures
# =============================================================================
    #arithmetic
    #converts a hexadecimal number to base 10
    def get_int(self, hexa, order=''):
        if order == '':
            num = int.from_bytes(hexa, byteorder=self.order)
        elif order == 'big' or order == 'little':
            num = int.from_bytes(hexa, byteorder=order)
        return num
    
    
    #converts list of hexadecimal numbers(2 bytes/elems long) to base- 10 integer
    def get_num(self, hexa, signed=False):
        #converts hexa list to int
        hexanum = b''.join(hexa)
        num = self.get_int(hexanum)

        #checks if num is signed 
        if signed == True:
            if num >> 15 == 0:#if the top bit is 0, num is unsigned            
                return num 
            else:
                return num - 2 ** 16 
        else:
            return num
    
    
    #text
    #converts 2 byte list of hexa char into 1x 1 bit int and 3 5 bit ints
    def get_zscii(self, hexa):
        #probably a more efficient way to do this
        #converts hexa to int
        intchar = self.get_num(hexa)
        
        #splits bit into 1 bit followed by 3x 5 bit ints
        zscii = []
        shift = [15, 10, 5, 0]
        for i in range(4):    
            n = shift[i]
            #extracts the desired bit substring by shifting the whole string
            #right and autotruncating
            temp = (intchar >> n) 
            
            #appends substring into zscii list
            zscii.append(temp)
            
            #removes the extracted substring from the overall bit string
            intchar -= (temp << n)
        
        #zscii list now consists of a 2 byte 'word' broken up into
        #1x 1 bit int followed by 3x 5 bit ints(aka z chars)
        return zscii
    
    
    #takes in a 5 bit int 'zchar' and maps zscii to characters
    #depending on zmachine version (need to add vernum argument)
    def map_zscii(self, zchar, shift=0):
        #special chars
        if self.val.check_space(zchar, shift):
            return ' '
        elif self.val.check_newline(zchar, shift):
            return '\n'
        
        #ascii chars
        else:
            if shift == 0:
                #lowercase
                return self.val.lower[zchar]
            elif shift == 1:
                #uppercase
                return self.val.upper[zchar]
            elif shift == 2:
                #punctuation
                return self.val.punct[zchar]
    
    
    #takes in memory address('memory' index) as argument since the length of a char
    #is not defined apriori
    def get_string(self, address):
        zlist = []
        memadd = address
        
        while True:
            #convert 2 byte hexa to list containing 3 zchars and 1 bit (of type int)
            hexa = self.memory[memadd:memadd + 2]
            zword = self.get_zscii(hexa)
            
            #appends all zchars to zlist
            for i in range(1, 4):
                zlist.append(zword[i])
              
            #checks for terminating condition
            if zword[0] == 1 or (memadd + 2) > len(self.memory):
                break
            
            #increments memory address
            memadd += 2
        
        
        charlist = []
        #converts zlist ints to chars
        shift = 0
        for i in range(len(zlist)):
            zchar = zlist[i]
            #check if special chars are inside and act accordingly
            if self.val.check_upper(zchar, shift):
                #shifts to uppercase
                shift = 1
            
            elif self.val.check_punct(zchar, shift):
                #shifts to punctuation
                shift = 2
                
            elif self.val.check_output(zchar, shift):
                #literal output character
                a = zlist[i + 1]
                b = zlist[i + 2]
                long_zchar = (a << 5) + b
                #convert to little endian?
                i += 2#will increment one more after the loop ends
                charlist.append(long_zchar)
                
# =============================================================================
# When we encounter A2-06, we read two more Z-characters,
# join the two pentets, interpret the resulting dectet 
# as a little-endian 10-bit integer, 
# and that's the ZSCII character being represented. 
# =============================================================================         
            
            elif self.val.check_abbrev(zchar, shift):
                #gets abbreviated string
                a = zchar#this works cus zchar is int
                b = zlist[i + 1]
                i += 1#will increment one more after the loop ends                
                
                #gets the index in 'memory' where abbrev table is stored
                abbrev_table = self.get_byte_address(self.memory[self.val.abbrev_add])
                
                #gets the index where word address to abbreviation is stored
                word_address_index = abbrev_table + (a - 1) * 32 + b
                
                #gets the word address where abbreviation is stored
                #and converts it to index in 'memory'
                word_address = self.get_word_address(self.memory[word_address_index])
                
                #finds the z string and appends it to charlist
                temp = self.get_string(word_address)#CHECK IM NOT SURE
                for word in temp:
                    charlist.append(word)
            
            else:
                #maps zscii to characters(depends on the zmachine version)
                ascii_char = self.map_zscii(zchar, shift=shift)
                charlist.append(ascii_char)
                
                #CHECK not sure if this step is correct
                shift = 0
        
        return charlist
    
    
    
# =============================================================================
# Memory Addresses
# =============================================================================
# =============================================================================
# 3 kinds of memory addresses ALL 2 BYTES long:
# byte addresses, word addresses, packed addresses
# byte address specifies A BYTE(not 2) in memory from 0 to the last byte
# in static memory
# 
# word address specifies an even address in the bottom 128K of memory 
# (by giving the address divided by 2)
# word addresses are only used in the abbreviations table
# 
# packed address specifies where a routine or string begins in high memory
# given a packed address P, the formula to obtain the corresponding byte address B
# 2P - versions 1, 2, 3
# 4P - 4, 5
# 4P + 8R_O - 6, 7 for routine calls
# 4P + 8S_O - 6, 7 for print_paddr
# 8P - 8        
# 
# R_O and S_O are string offsets specified in header as words at $28 and $2a respectively      
#   
# must convert memory address in story file into index in 'memory'
# 
# =============================================================================

    #converts byte address list(2 bytes/elems long) to index in 'memory'
    def get_byte_address(self, byte_list): 
        index = self.get_num(byte_list)
        return index
    
    #converts word address list(2 bytes/elems long) to index in 'memory'
    def get_word_address(self, word_list):
        index = self.get_byte_address(word_list) * 2
        return index
    
    #converts packed address list(2 bytes/elems long) to index in 'memory'
    def get_packed_address(self, packed_list, is_routine_call = False, 
                           is_print_paddr = False):
        pindex = self.get_byte_address(packed_list)
        
        
        vn = self.ver_num
        if vn == 1 or vn == 2 or vn == 3:
            index = 2 * pindex
        
        elif vn == 4 or vn == 5:
            index = 4 * pindex
        
        elif vn  == 6 or vn == 7: 
            if is_routine_call:
                #gets the routine offset in hexadecimal
                #gets int memory address
                address = self.val.ro_add
                rohexa = self.memory[address]
                
                #converts hexadecimal to int offset
                ro = self.get_int(rohexa)
                index = 4 * pindex + ro
                
            elif is_print_paddr:
                #gets the string offset in hexadecimal
                #gets int memory address
                address = self.val.so_add
                sohexa = self.memory[address]
                
                #converts hexadecimal to int offset
                so = self.get_int(sohexa)
                index = 4 * pindex + so
                
        elif vn == 8:
            index = 8 * pindex
        
        
        return index

    
    def generator(self, n, random=True):
        if random == True:
            pass
            #generates random number using time as seed
        
        else:
            pass
            #generates random number using custom seed
            
    
    
    
# =============================================================================
# end of class
# =============================================================================

#testing code


file_name = 'C:/Users/User/Desktop/TelegramBot/ifbot/games/hhgg.z3'

#opens file in binary
file = open(file_name, "rb")

#need to write file in binary as well

machine = ZMachine(file)

memory = machine.get_memory()#this should not be allowed

#python prints out 2 bytes in hexadecimal like so: '\x<hexa>' 
#hexadecimal is expressed in the documentation as '$0<hexa><hexa>' and also as '0x<hexa>'
#memory address is implicit not stated in the story file like
#\x00\x00: data, \x00\x01: data


#zlist = machine.get_zscii([b'\x3e', b'\xf2'])
#print(zlist)

#print(memory[0], memory[4:6], memory[14:16])
#print(machine.get_dynamic(), machine.get_high(), machine.get_static())

#tests the get string function
abbrev_add = machine.val.abbrev_add
for i in range(1):
    offset = i*2
    abbrev_table_add = machine.get_byte_address(memory[abbrev_add:abbrev_add + 2])
    #print('abbrev_table_add ' + str(abbrev_table_add))
    abbrev_string_location = machine.get_word_address(memory[abbrev_table_add + offset:abbrev_table_add + offset + 2])
    #print('abbrev_string_location ' + str(abbrev_string_location))
    #print('get_string')
    abbrev_list = machine.get_string(abbrev_string_location)
    #print('abbrev_list ' + str(abbrev_list))
    abbrev_string = ''.join(abbrev_list)
    print(abbrev_string)
    
