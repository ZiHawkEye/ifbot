# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:30:51 2018

@author: User
"""
from helper import *

class Memory():
    def __init__(self, file):        
        # determines endianness of bits - big
        # bits are numbered from right to left, counting from zero
        # bit with lowest number is least significant
        self.endian = 'big'

        # loads the entirety of the story file
        self.memory = self.load_memory(file)
        
        # sets version number of z machine
        self.ver_num = self.get_ver()
        
        # instantiates object containing predetermined values
        self.help = Helper(self.ver_num)

        # variables containing memory indexes of 'memory' denoting the start and end of each 
        # memory segment
        # dynamic memory starts at 0x00 to BYTE address stored at 0x0e 
        # in the header(defined as first 64 bytes in the story file)        
        self.dynamic = []
        
        # static follows immediately after dynamic,
        # must end by address 0xffff or end of file, whichever is lower
        self.static = []
        
        # high memory begins at the BYTE address stored at 0x04 and 
        # continues to the end of the file
        # may overlap with static memory
        self.high = []
        
        # segments memory into dynamic, static and high
        self.segment_mem()
        
        # addresses of subcategories of header
        # byte address to initialize program counter
        # index of 'memory' where first routine instruction is stored
        self.pc = self.get_pc_start()
        
        # index of 'memory' where abbreviation table is stored
        self.abbrev_start = self.get_abbrev_start()

        # index of 'memory' where global variables are stored
        self.gvars_start = self.get_gvars_start()
        
        # dictionary
        dict_header = self.get_dict_start()
        n = self.memory[dict_header]
        self.sep_start = dict_header + 1
        # converts each byte to ascii code
        self.separators = self.memory[self.sep_start:self.sep_start + n]
        self.entry_length = self.memory[self.sep_start + n]
        num_start = self.sep_start + n + 1
        self.num_of_entries = self.get_num(self.memory[num_start:num_start + 2], signed=True)
        self.dict = self.sep_start + n + 3
        
        # property defaults table before object table
        self.prop_defaults = self.get_property_defaults_start()

        # object table
        self.obj_tb = self.prop_defaults + (31*2) if self.ver_num in [1, 2, 3] else self.prop_defaults + (63*2)        
        
# =============================================================================
# Set Methods for Attributes       
# =============================================================================
    # segments memory
    def segment_mem(self):
        # sorts 'memory' into dynamic, static and high
        # start and end of dynamic
        dstart = 0
        
        # converts 0x0e to index and gets byte address(2 bytes)
        address = self.help.dyn_end_add
        dend = self.get_byte_address(self.memory[address:address + 2])

                
        # start and end of static
        sstart = dend
        
        if len(self.memory) - 1 < 65535:
            send = len(self.memory) - 1
        else:
            send = 65535

        
        # start and end of high
        # converts 0x04 to index and gets byte address(2 bytes) 
        address = self.help.hi_start_add
        hstart = self.get_byte_address(self.memory[address: address + 2])        
        
        hend = len(self.memory) - 1

        
        # marks the start and end of each segment of memory
        self.dynamic = [dstart, dend]
        self.static = [sstart, send]
        self.high = [hstart, hend]

        
    def load_memory(self, file):
        # reads the file in 1 byte elements into 'memory' list and closes the file
        # converts each byte into 8 bit integers
        memory = []
        try:
            while True:
                byte = file.read(1)
                int_8 = self.get_int(byte)
                memory.append(int_8)
                if not byte:
                    break
                
        finally:
            file.close()
        
        return memory

    def set_gvar(self, var, value):
        self.storew(baddr=self.gvars_start, n=var, a=value)

    def storew(self, baddr, n, a):
        # a is always 2 bytes
        a = self.get_num(a)
        a = [a >> 8] + [0xff & a]
        assert(len(a) == 2 and type(a[0]) == int), "Incorrect format for a " + str(a) + " in storew"
        index = baddr + 2*n
        self.memory[index:index + 2] = a

    def storeb(self, baddr, n, byte):
        assert(type(byte) == int), "Incorrect format for byte " + str(byte) + " in storeb"
        index = baddr + n
        self.memory[index] = byte

    def copy_table(self, baddr1, baddr2, s):
        if baddr2 == 0:
            for i in range(s):
                self.memory[baddr1 + i] = 0
        else:
            if s < 0:
                s *= -1 
                # if s is negative, copy forwards table at add1 to add2 even if it corrupts add1 table
                # assume that add1 table entries wont be corrupted before they are read?
                for i in range(s):
                    self.memory[baddr2 + i] = self.memory[baddr1 + i]
            
            elif s > 0:
                # if tables overlap then copy backwards to avoid corruption
                # otherwise copy forwards by default
                if baddr1 < baddr2 and baddr1 + s > baddr2:
                    # copies table backwards
                    for i in range(s - 1, -1, -1):
                        self.memory[baddr2 + i] = self.memory[baddr1 + i]
                else:
                    for i in range(s):
                        self.memory[baddr2 + i] = self.memory[baddr1 + i]

# =============================================================================
# Get Methods for Attributes
# =============================================================================
    def get_ver(self):
        return self.memory[0]
    
    def get_memory(self):
        #can't just return must make a copy otherwise you're just aliasing
        return self.memory[:]
    
    def get_dynamic(self):
        return self.dynamic[:]
    
    def get_static(self):
        return self.static[:]
        
    def get_high(self):
        return self.high[:]
        
    def get_pc(self):
        return self.pc

    def get_pc_start(self):
        address = self.help.pc_add
        if self.ver_num != 6:
            return self.get_byte_address(self.memory[address:address + 2])
        else:
            return self.get_packed_address(self.memory[address:address + 2])
    
    def get_abbrev_start(self):
        address = self.help.abbrev_add
        return self.get_byte_address(self.memory[address:address + 2])
    
    def get_gvars_start(self):
        address = self.help.gvar_add
        return self.get_byte_address(self.memory[address:address + 2])

    def get_gvar(self, var):
        address = self.gvars_start + var*2
        return self.memory[address:address+2]

    def get_property_defaults_start(self):
        address = self.help.obj_add
        byte_address = self.get_byte_address(self.memory[address:address + 2])
        assert(byte_address != 0), "No objects detected"
        return byte_address

    def get_dict_start(self):
        address = self.help.dict_add
        return self.get_byte_address(self.memory[address:address + 2])

# =============================================================================
# Operations
# =============================================================================
    def loadw(self, baddr, n):
        address = baddr + 2*n
        return self.memory[address:address + 2]

    def loadb(self, baddr, n):
        address = baddr + n
        return self.memory[address]
    
    def scan_table(self, a, baddr, n, byte):
        index = baddr
        
        # top bit of byte is 0 to search for a byte, 1 to search for a word, remaining 7 bits 
        # give the unsigned length of an entry in bytes
        # default format is \x82, looking for a word in a table of words
        
        # convert byte to int
        int_byte = byte
        one = int_byte >> 7
        seven = int_byte - one << 7
        format_word = self.get_int(b'\x82')
        if one == 0:
            assert (len(a) == 1), "Variable a should not be a word in scan_table"  
            assert (seven != format_word), "Wrong format code to search for byte in scan_table"
            for i in range(0, n, 1):
                if self.memory[index + i] == a:
                    return index + i
            return 0
            
        elif one == 1:
            assert (len(a) == 2), "Variable a should not be a byte in scan_table"
            assert (seven == format_word), "Wrong format code to search for word in scan_table"
            for i in range(0, n, 2):
                address = index + i
                if self.memory[address:address + 2] == a:
                    return address
            return 0

    def read(self, baddr1, baddr2, stream):
        # stream is a lowercase string
        stream = [ord(char) for char in stream]
        # ensures stream does not exceed max buffer length
        max_buffer_len = self.memory[baddr1]
        size = len(stream)
        assert (max_buffer_len >= size), "Buffer length exceeded"
        if self.ver_num in [1, 2, 3]:
            stream.append(0) # appends terminating char
            address = baddr1 + 1
            self.memory[address:address + size + 1] = stream
        elif self.ver_num in [4, 5, 6]:
            # writes size of stream inside buffer
            self.memory[baddr1 + 1] = size
            address = baddr1 + 2
            self.memory[address:address + size] = stream

    def tokenise(self, baddr1, baddr2, baddr3=None, bit=None):
        # tokenises input ascii chars and looks them up in the dictionary
        # gets size of input string, excluding terminating char
        if self.ver_num in [1, 2, 3, 4]:
            # should have a 0 terminating char at the end
            start = baddr1 + 1
            end = start
            while self.memory[end] != 0:
                end += 1
            size = end - start
        elif self.ver_num in [5, 6]:
            size = self.memory[baddr1 + 1]
            start = baddr1 + 2
        # look for tokens
        lens = []
        positions = [start - baddr1]
        for i in range(size):
            position = start + i
            ascii_code = self.memory[position]
            if ascii_code in self.separators:
                # tokenise separator chars individually
                positions.append(position - baddr1)
                token_len = positions[-1] - positions[-2] 
                lens.append(token_len)
                positions.append(position + 1 - baddr1)
                lens.append(1)
            elif ascii_code == 32:
                # ignore spaces
                token_len = position - baddr1 - positions[-1]
                lens.append(token_len)
                positions.append(position + 1 - baddr1)
        # for last token
        end = size + start
        token_len = end - baddr1 - positions[-1]
        lens.append(token_len)
 
        tokens = []
        # encodes tokens
        for i in range(len(positions)):
            token = self.encode_text(baddr1, lens[i], positions[i])
            tokens.append(token)
        dict_adds = []
        for token in tokens:
            # looks up token in separators
            for i in range(len(self.separators)):
                if token == self.separators[i]:
                    address = self.sep_start + i
                    dict_adds.append(address)

            # looks up token in dictionary
            # use main dict if baddr3 is not specified
            dict_start = self.dict if baddr3 == None else baddr3
            is_found = False
            token_len = 4 if self.ver_num in [1, 2, 3] else 6
            for i in range(0, self.num_of_entries):
                entry_start = dict_start + i*self.entry_length
                entry = self.memory[entry_start:entry_start + token_len]
                if entry == token:
                    dict_adds.append(entry_start)
                    is_found = True
                    break
            if not is_found:
                dict_adds.append(0)

        # creates parse buffer
        # first byte of buffer stores the max amount of tokens
        token_max = self.memory[baddr2]
        assert (token_max >= len(tokens)), "Text buffer contains too many tokens"
        # actual number of tokens is stored in the next byte
        self.memory[baddr2 + 1] = len(tokens)
        # creates block for each token
        for i in range(len(tokens)):
            if dict_adds[i] == 0 and bit != 0:
                pass
            else:
                dict_byte_add = self.get_bytes(dict_adds[i], 2)
                block = dict_byte_add + [lens[i]] + [positions[i]]
                # write block to parse buffer after first 2 bytes
                address = baddr2 + 2 + (i * 4)
                self.memory[address:address + 4] = block
        
    def encode_text(self, baddr1, n, p, baddr2=None):
        zchars = []
        start = baddr1 + p
        charlist = self.memory[start:start + n]
        # maps each char to a zscii code
        for char in charlist:
            if char in self.separators:
                return char
            else:
                for shift in range(0, 3):
                    for zcode in range(6, 32):
                        if char == ord(self.help.char_map[shift][zcode]):
                            if shift == 0:
                                zchars.append(zcode)
                            else:
                                zchars.append(shift)
                                zchars.append(zcode)
        
        # convert every 3 zchars into a word
        zstring = []
        position = [10, 5, 0]
        # defines max number of zchars (4/6 bytes)
        if self.ver_num in [1, 2, 3]:
            max_len = 6 
        elif self.ver_num in [4, 5, 6]:
            max_len = 9
        for i in range(0, max_len, 3):
            # each zword has a bit, followed by 3 5 bit sequences
            zword = 0
            for j in range(3):
                try:
                    zword += (zchars[i + j] << position[j])
                except IndexError:
                    # add padding
                    zword += (5 << position[j])
            zstring.append(zword >> 8)
            zstring.append(zword & 0xff)
        # insert terminating character
        zstring[-2] += 1 << 7
        if self.ver_num in [1, 2, 3]:
            assert (len(zstring) == 4), "Error encoding zstring " + str(zstring)
            if baddr2 != None:
                self.memory[baddr2:baddr2 + 4] = zstring
            else:
                return zstring
        elif self.ver_num in [4, 5, 6]:
            assert (len(zstring) == 6), "Error encoding zstring " + str(zstring) 
            if baddr2 != None:
                self.memory[baddr2:baddr2 + 6] = zstring
            else:
                return zstring
    
    def verify(self):
        n = self.get_num(self.memory[26:28])
        a = self.get_num(self.memory[28:30])
        if self.ver_num == 3:
            factor = 2
        elif self.ver_num in [4, 5]:
            factor = 4
        elif self.ver_num in [6, 7, 8]:
            factor = 8
        sum = 0
        if n*f - 1 > 64:
            for i in range(n*f - 1):
                sum += self.memory[64 + i]
        if sum == a:
            return True
        else:
            return False
        
# =============================================================================
# Helper Functions
# # =============================================================================
# =============================================================================
# Data Structures
# =============================================================================
    # arithmetic
    # converts a hexadecimal number to base 10
    # may not be necessary
    def get_int(self, hexa, endian='default'):
        assert (type(hexa) == bytes), "hexa " + str(hexa) + " should be of type bytes"
        if endian == 'default':
            num = int.from_bytes(hexa, byteorder=self.endian)
        elif endian == 'big' or endian == 'little':
            num = int.from_bytes(hexa, byteorder=order)
        return num
    
    # joins multiple int elements
    def get_num(self, int_list, signed=False):
        num = 0
        if type(int_list) == int:
            num = int_list
        else:
            for int_8 in int_list:
                num = (num << 8) + int_8
        assert (num <= 0xffff or not signed), "Encountered signed num greater than 16 bits in get_num()"
        # all signed nums are 16 bit
        if signed == True:
            if num >> 15 == 0: #if the top bit is 0, num is unsigned            
                return num 
            else:
                return num - (1 << 16) 
        else:
            # UNDO
            assert(num >= 0), "Encountered negative unsigned num" + str(num)
            return num

    # convert integers greater than 1 byte into a list of 8 bit integers
    def get_bytes(self, num, bytes_num):
        assert (num < 2 ** (bytes_num*8)), "num " + str(num) + " should be less than " + str(2 ** (bytes_num*8))
        byte_list = []
        for i in range(bytes_num - 1, -1, -1):
            temp = num >> (i*8)
            num -= temp << (i*8)
            byte_list.append(temp)
        return byte_list
# =============================================================================
# Text
# =============================================================================
    # converts 2 byte list of hexa char into 1x 1 bit int and 3 5 bit ints
    def get_zscii(self, word):
        assert (len(word) == 2), "zscii characters should be of 2 bytes"
        # merges word
        int_16 = self.get_num(word)
        
        # splits byte into 1 bit followed by 3x 5 bit ints
        zscii = []
        shifts = [15, 10, 5, 0]
        for shift in shifts:    
            # extracts the desired bit substring by shifting the whole string
            # right and autotruncating
            temp = (int_16 >> shift) 
            zscii.append(temp)
            int_16 -= (temp << shift)
        
        # zscii list now consists of a 2 byte 'word' broken up into
        # 1x 1 bit int followed by 3x 5 bit ints(aka z chars)
        return zscii
    
    
    # takes in a 5 bit int 'zchar' and maps zscii to characters
    # depending on zmachine version
    def map_zscii(self, zchar, shift=0):
        # special chars
        is_space = (zchar == 0)
        is_newline = ((self.ver_num in [1] and
                        zchar == 1) or
                        (self.ver_num in [2, 3, 4, 5, 6, 7, 8] and
                        (zchar == 7 and shift == 2)))
        if is_space:
            return ' '
        elif is_newline:
            return '\n'
        
        # ascii chars
        else:
            try:
                return self.help.char_map[shift][zchar]
            except KeyError:
                print("Invalid zscii code")
                raise
        
    # takes in memory address('memory' index) as argument since the length of a char
    # is not defined apriori
    def get_string(self, address):
        zlist = []
        
        while True:
            # convert 2 byte hexa to list containing 3 zchars and 1 bit (of type int)
            word = self.memory[address:address + 2]
            zword = self.get_zscii(word)
            address += 2
            
            # appends all zchars to zlist
            for i in range(1, 4):
                zlist.append(zword[i])
              
            # terminating condition
            if zword[0] == 1 or (address + 2) > len(self.memory):
                break
                
        charlist = []
        # converts zlist ints to chars
        shift = 0
        # Cannot change loop index inside for loop for python, must use while loop instead
        i = 0
        while i < len(zlist):
            zchar = zlist[i]
            # if special chars are inside act accordingly
            is_upper = ((self.ver_num in [1, 2] and
                            zchar in [2, 3, 4, 5]) or
                            (self.ver_num in [3, 4, 5, 6, 7, 8] and
                            zchar == 4))
            is_punct = ((self.ver_num in [1, 2] and
                            zchar in [2, 3, 4, 5]) or
                            (self.ver_num in [3, 4, 5, 6, 7, 8] and
                            zchar == 5))
            is_abbrev = ((self.ver_num in [2] and
                            zchar == 1) or 
                            (self.ver_num in [3, 4, 5, 6, 7, 8] and
                            zchar in [1, 2, 3]))
            is_output = (zchar == 6 and shift == 2)
            if is_upper:
                # shifts to uppercase
                shift = 1
            
            elif is_punct:
                # shifts to punctuation
                shift = 2
                
            elif is_output:
                # literal output character
                a = zlist[i + 1]
                b = zlist[i + 2]
                long_zchar = (a << 5) + b
                # convert to little endian?
                i += 2
                # CHECK
                charlist.append(chr(long_zchar))
                
# =============================================================================
# When we encounter A2-06, we read two more Z-characters,
# join the two pentets, interpret the resulting dectet 
# as a little-endian 10-bit integer, 
# and that's the ZSCII character being represented. 
# =============================================================================         
            
            elif is_abbrev:
                # gets abbreviated string
                a = zchar# this works cus zchar is int
                b = zlist[i + 1]
                i += 1 
                                
                entry = (a - 1) * 32 + b # this is the nth entry in the abbrev table, starting from 0
                # gets the index where word address to abbreviation is stored
                wa_index = self.abbrev_start + entry * 2
                
                # gets the word address where abbreviation is stored
                # and converts it to index in 'memory'
                word_address = self.get_word_address(self.memory[wa_index:wa_index + 2])
                
                # finds the z string and appends it to charlist
                temp = self.get_string(word_address)
                charlist.append(temp)
            
            else:
                # does not use the algorithm involving shift and lock keys
                # maps zscii to characters(depends on the zmachine version)
                ascii_char = self.map_zscii(zchar, shift=shift)
                charlist.append(ascii_char)
                
                # CHECK not sure if this step is correct (only for ver 3+)
                shift = 0
            # increments the while loop
            i += 1
        
        # Updates program counter
        self.pc = address
        zstr = ''.join(charlist)
        return zstr

# =============================================================================
# Objects
# =============================================================================
    def get_obj(self, obj):
        # obj is a legal obj number (obj is numbered from 1)
        assert(obj > 0), "Object 0 does not exist"
        address = self.obj_tb + (self.help.obj_size * (obj - 1))
        
        # predefined addresses
        adds = [0, 4, 5, 6, 7, 9] if self.ver_num in [1, 2, 3] else [0, 6, 8, 10, 12, 14]
        adds = [address + add for add in adds]
        flag_len = 32 if self.ver_num in [1, 2, 3] else 48

        flags_int = self.get_num(self.memory[adds[0]:adds[1]])
        flags = []
        for i in range(flag_len - 1, -1, -1):
            bit = flags_int >> i
            flags.append(bit)
            flags_int -= bit << i
        parent = self.get_num(self.memory[adds[1]:adds[2]])
        sibling = self.get_num(self.memory[adds[2]:adds[3]])
        child = self.get_num(self.memory[adds[3]:adds[4]])
        properties_add = self.get_byte_address(self.memory[adds[4]:adds[5]])
        return Object(flags, parent, sibling, child, properties_add)
    
    def get_obj_name(self, pc):
        text_len = self.memory[pc]
        pc += 1
        name = ""
        if text_len != 0:
            name = self.get_string(pc)
            assert (self.pc - pc == text_len*2), "Property name length does not equal to stated text_length; properties table may not exist"
        else:
            self.pc = pc
        return name
    
    def get_prop_blk(self, pc):
        if self.ver_num in [1, 2, 3]:
            size_byte = self.memory[pc]
            data_add = pc + 1
            if size_byte == 0:
                return 0
            prop_len = (size_byte >> 5) + 1
            prop_num = size_byte & 31
        elif self.ver_num >= 4:
            size_byte = self.memory[pc]
            if size_byte == 0:
                return 0
            prop_num = size_byte & 63    
            if (size_byte >> 7) == 1:
                second_byte = self.memory[pc + 1]
                data_add = pc + 2
                prop_len = (second_byte & 63) if (second_byte & 63) != 0 else 64
            else:
                data_add = pc + 1
                prop_len = (size_byte >> 6) & 1
        return {'prop_num': prop_num, 'prop_len': prop_len, 'data_add': data_add}
                
    def get_prop_addr(self, pc, prop):
        # returns the byte address of the property data (after size byte)
        # properties are numbered from 1 onwards
        self.get_obj_name(pc)
        # updates pc to end of name string
        pc = self.pc
        max_prop = 31 if self.ver_num in [1, 2, 3] else 63
        for i in range(max_prop):
            result = self.get_prop_blk(pc)
            if result == 0:
                return 0
            else:
                if result['prop_num'] == prop:
                    return result
                pc = result['data_add'] + result['prop_len']
        return 0

    def set_obj(self, obj, obj_var):
        # takes an object of type Object and encodes it into the object table
        assert(obj > 0), "Object 0 does not exist"
        address = self.obj_tb + (self.help.obj_size * (obj - 1))
        obj_bytes = []
        # predefined values
        vals = ({"flags_size": 4, "psc_size": 1, "prop_size": 2, "obj_size": 9} if self.ver_num in [1, 2, 3] else 
                {"flags_size": 6, "psc_size": 2, "prop_size": 2, "obj_size": 14})
        flags_len = 32 if self.ver_num in [1, 2, 3] else 48
        
        # get flags
        flags_int = 0
        for i in range(flags_len):
            flags_int = (flags_int << 1) + obj_var.flags[i]
        flags_byte = self.get_bytes(flags_int, vals['flags_size'])
        # get parent, sib, child (get_bytes() returns a list even if converting 1 byte)
        parent_byte = self.get_bytes(obj_var.parent, vals['psc_size'])
        sibling_byte = self.get_bytes(obj_var.sibling, vals['psc_size'])
        child_byte = self.get_bytes(obj_var.child, vals['psc_size'])
        # gets properties
        properties_byte = self.get_bytes(obj_var.properties_add, vals['prop_size'])
        obj_bytes = (flags_byte +
                     parent_byte +
                     sibling_byte +
                     child_byte +
                     properties_byte)
        assert(len(obj_bytes) == vals['obj_size']), "Error encoding object"
        self.memory[address:address + len(obj_bytes)] = obj_bytes

    def put_prop(self, obj, prop, a):
        # Set prop on obj to a. The propperty must be present on the object(prop is in prop list? or flag == 1?)
        # Conversion from unsigned to signed num?
        obj_var = self.get_obj(obj)
        result = self.get_prop_addr(obj_var.properties_add, prop)
        if result == 0:
            raise Exception("Property not found")
        elif result['prop_len'] > 2:
            # do nothing
            pass
        else:
            # if prop len is 1, then a should store only the least significant byte of the value
            a = [a >> 8] + [0xff & a]
            data_add = result['data_add']
            if result['prop_len'] == 1:
                self.memory[data_add] = a[1]
            else:
                self.memory[data_add:data_add + 2] = a 

    def get_next_prop(self, obj, prop):
        obj_var = self.get_obj(obj)
        if prop == 0:
            self.get_obj_name(obj_var.properties_add)
            pc = self.pc
            result = self.get_prop_blk(pc)
            return result['prop_num']
        else:
            result = self.get_prop_addr(obj_var.properties_add, prop)
            if result == 0:
                raise Exception("Property was not found")
            pc = result['data_add'] + result['prop_len']
            result = self.get_prop_blk(pc)
            if result == 0:
                return 0
            else:
                return result['prop_num']

# =============================================================================
# Routines and Instructions
# =============================================================================
    # start of a routine: function, interrupt or procedure
    # end of routine: return
    def get_routine(self, pc):
        self.pc = pc
        localvars_num = self.memory[pc]
        self.pc += 1
        localvars = []

        if self.ver_num in [1, 2, 3, 4]:
            for i in range(localvars_num):
                localvars.append(self.memory[self.pc:self.pc + 2])
                self.pc += 2
        elif self.ver_num in [5, 6]:
            for i in range(localvars_num):
                localvars.append(0)

        return localvars
    
    # takes in 'memory' index as argument since the length of an instruction
    # is not defined apriori
    # note: python passes args by assignment so mutable variables can be changed
    # inside the function
    def get_instr(self, pc):
        self.pc = pc
        byte = self.memory[self.pc]
        self.pc += 1

        # op_types
        LARGE = 0
        SMALL = 1
        VAR = 2

        # gets kind, op num, types
        # KIND(0:0OP, 1:1OP, 2:2OP, 3:VAR, 4:EXT)
        if byte >= 0x00 and byte <= 0x7f:
            kind = 2
            if byte <= 0x1f:
                op_num = byte - 0x00
                types = [SMALL, SMALL]
            elif byte <= 0x3f:
                op_num = byte - 0x20
                types = [SMALL, VAR] 
            elif byte <= 0x5f:
                op_num = byte - 0x40
                types = [VAR, SMALL]
            elif byte <= 0x7f:
                op_num = byte - 0x60
                types = [VAR, VAR]
        elif byte <= 0xaf:
            kind = 1
            if byte <= 0x8f:
                op_num = byte - 0x80
                types = [LARGE]
            elif byte <= 0x9f:
                op_num = byte - 0x90
                types = [SMALL]
            elif byte <= 0xaf:
                op_num = byte - 0xa0
                types = [VAR]
        elif byte <= 0xbf and byte != 0xbe:
            kind = 0
            op_num = byte - 0xb0
            types = []
        elif byte <= 0xff:
            if byte == 0xbe:
                kind = 4
                # op code given in next byte
                byte = self.memory[self.pc]
                self.pc += 1
                op_num = byte
            elif byte <= 0xdf:
                kind = 2
                op_num = byte - 0xc0
            elif byte <= 0xff:
                kind = 3
                op_num = byte - 0xe0
            # gets operand types for 0xb0 to 0xff
            types = []
            if byte in [0xec, 0xfa]:
                type_bytes = self.memory[self.pc:self.pc + 2]
                self.pc += 2
                n = 16
            else:
                type_bytes = self.memory[self.pc]
                self.pc += 1
                n = 8
            # splits byte seq into 2 bit sequences
            for i in range(n - 2, -2, -2):
                temp = type_bytes >> i
                if temp == 3:
                    break
                types.append(temp)
                type_bytes -= temp << i
            
        instr_details = self.help.op_table[kind][op_num] # instr_details is of type dict
        assert (instr_details != {}), "Kind: {}, OP: {} ".format(str(kind), str(op_num)) + "is not a valid instruction at " + '{0:02x}'.format(pc)
        
        # gets operands
        operands = self.get_operands(self.pc, types)

        # it is an error for a variable instr with 2op code to not have 2 operands
        # unless it is op_code: 2op:1
        # if op_count is 0 - 2, number of elems in types and operands == op_count
        if kind in range(0, 3) and instr_details['name'] != "je":
            assert (kind == len(types)), 'Number of types does not equal op count (0OP, 1OP, 2OP) for ' + instr_details['name']
            assert (kind == len(operands)), 'Number of operands does not equal op count (0OP, 1OP, 2OP) for ' + instr_details['name']

        str_arg = None
        res_arg = None
        is_reversed = None
        offset = None
        if instr_details["is_str"] == True:
            str_arg = self.get_string(self.pc)
        if instr_details["is_res"] == True:
            res_arg = self.memory[self.pc]
            self.pc += 1
        if instr_details["is_br"] == True:
            # the branch argument is always the last of the sequence of arguments
            # get bit 2 to see if branch arg is 1 or 2 bytes
            int_byte = self.memory[self.pc]
            # gets bit 2
            one = (int_byte >> 7)
            two = (int_byte >> 6) & 1
            # bit 1 determines if logic is reversed
            is_reversed = True if one == 0 else False
            is_one = True if (two == 1) else False
            br_arg_byte = self.memory[self.pc] if is_one else self.memory[self.pc: self.pc + 2]
            br_arg = self.get_num(br_arg_byte)
            # gets offset
            # unsigned if 1 byte and signed if 2
            if is_one:
                offset = (br_arg - (br_arg >> 6 << 6))
            else:
                signed_bits = (br_arg - (br_arg >> 14 << 14))
                offset = signed_bits if (signed_bits < 1 << 13) else (signed_bits - 2 ** 14)

            self.pc = self.pc + 1 if is_one else self.pc + 2

        name = instr_details['name']
        op_types = instr_details["types"]
        instr = Instruction(name, types, op_types, operands, str_arg, res_arg, is_reversed, offset)
        return instr
        
    # gets operands by returning a list
    def get_operands(self, op_start, types):
        self.pc = op_start
        operands = []
        byte_operand = []
        
        for args in types:
            if args == 0:
                # large - 2 bytes
                byte_operand = self.memory[self.pc:self.pc + 2]
                self.pc += 2
                
            elif args == 1 or args == 2:
                # small and variable - 1 byte
                byte_operand = self.memory[self.pc]
                self.pc += 1           
                
            # operand is a byte list
            # operands should be a nested list
            operands.append(byte_operand)

        return operands

# =============================================================================
# Memory Addresses    
# =============================================================================
    # converts byte address list(2 bytes/elems long) to index in 'memory'
    def get_byte_address(self, byte_list):
        index = self.get_num(byte_list)
        return index
    
    # converts word address list(2 bytes/elems long) to index in 'memory'
    def get_word_address(self, word_list):
        index = self.get_byte_address(word_list) * 2
        return index
    
    # converts packed address list(2 bytes/elems long) to index in 'memory'
    def get_packed_address(self, packed_list, is_routine_call = False, 
                           is_print_paddr = False):
        pindex = self.get_byte_address(packed_list)
        
        if self.ver_num in [1, 2, 3]:
            index = 2 * pindex
        elif self.ver_num in [4, 5]:
            index = 4 * pindex
        elif self.ver_num in [6, 7]: 
            if is_routine_call:
                # gets the routine offset in hexadecimal
                # gets int memory address
                address = self.help.ro_add
                ro = self.memory[address]
                index = 4 * pindex + ro
                
            elif is_print_paddr:
                # gets the string offset in hexadecimal
                # gets int memory address
                address = self.help.so_add
                so = self.memory[address]
                index = 4 * pindex + so
        elif self.ver_num == 8:
            index = 8 * pindex
            
        return index

# =============================================================================
# End of Class
# =============================================================================



    

