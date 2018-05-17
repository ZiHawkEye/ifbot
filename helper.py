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
    def __init__(self, ver_num, kind, op_num):
        # map opcode to function
        #how to look for corresponding op code in dictionary
        #dictionary for each kind
        #list containing all the dictionaries
        #list[kind]['key'] that contains callback function, operand types, is_args (refer to table)
        
        #map opcode to function
        #define operand types and args needed
        #types
        
        


# =============================================================================
# Map instructions to functions
# 
# St	Br	Opcode	Hex 	V 	Inform name and syntax 	Link
# 		------	0 	---	---	
# 	* 	2OP:1 	1 		je a b ?(label)	je
# 	* 	2OP:2 	2 		jl a b ?(label)	jl
# 	* 	2OP:3 	3 		jg a b ?(label) 	jg
# 	* 	2OP:4 	4 		dec_chk (variable) value ?(label) 	dec_chk
# 	* 	2OP:5 	5 		inc_chk (variable) value ?(label) 	inc_chk
# 	* 	2OP:6 	6 		jin obj1 obj2 ?(label) 	jin
# 	* 	2OP:7 	7 		test bitmap flags ?(label) 	test
# * 		2OP:8 	8 		or a b -> (result) 	or
# * 		2OP:9 	9 		and a b -> (result) 	and
# 	* 	2OP:10	A 		test_attr object attribute ?(label) 	test_attr
# 		2OP:11	B 		set_attr object attribute 	set_attr
# 		2OP:12	C 		clear_attr object attribute 	clear_attr
# 		2OP:13	D 		store (variable) value 	store
# 		2OP:14	E 		insert_obj object destination 	insert_obj
# * 		2OP:15	F 		loadw array word-index -> (result) 	loadw
# * 		2OP:16	10 		loadb array byte-index -> (result) 	loadb
# * 		2OP:17	11 		get_prop object property -> (result) 	get_prop
# * 		2OP:18	12 		get_prop_addr object property -> (result) 	get_prop_addr
# * 		2OP:19	13 		get_next_prop object property -> (result) 	get_next_prop
# * 		2OP:20	14 		add a b -> (result) 	add
# * 		2OP:21	15 		sub a b -> (result) 	sub
# * 		2OP:22	16 		mul a b -> (result) 	mul
# * 		2OP:23	17 		div a b -> (result) 	div
# * 		2OP:24	18 		mod a b -> (result) 	mod
# * 		2OP:25	19 	4 	call_2s routine arg1 -> (result) 	call_2s
# 		2OP:26	1A 	5 	call_2n routine arg1 	call_2n
# 		2OP:27	1B 	5 	set_colour foreground background 	set_colour
# 				6 	set_colour foreground background window 	set_colour
# 		2OP:28	1C 	5/6 	throw value stack-frame 	throw
# 		------	1D 	---	---	
# 		------	1E 	---	---	
# 		------	1F 	---	---	
# 
# Opcode numbers 32 to 127: other forms of 2OP with different types.
# One-operand opcodes 1OP St	Br	Opcode	Hex 	V 	Inform name and syntax 	Link
# 	* 	1OP:128	0 		jz a ?(label) 	jz
# * 	* 	1OP:129	1 		get_sibling object -> (result) ?(label) 	get_sibling
# * 	* 	1OP:130	2 		get_child object -> (result) ?(label) 	get_child
# * 		1OP:131	3 		get_parent object -> (result) 	get_parent
# * 		1OP:132	4 		get_prop_len property-address -> (result) 	get_prop_len
# 		1OP:133	5 		inc (variable) 	inc
# 		1OP:134	6 		dec (variable) 	dec
# 		1OP:135	7 		print_addr byte-address-of-string 	print_addr
# * 		1OP:136	8 	4 	call_1s routine -> (result) 	call_1s
# 		1OP:137	9 		remove_obj object 	remove_obj
# 		1OP:138	A 		print_obj object 	print_obj
# 		1OP:139	B 		ret value 	ret
# 		1OP:140	C 		jump ?(label) 	jump
# 		1OP:141	D 		print_paddr packed-address-of-string 	print_paddr
# * 		1OP:142	E 		load (variable) -> (result) 	load
# * 		1OP:143	F 	1/4 	not value -> (result) 	not
# 				5 	call_1n routine 	call_1n
# 
# Opcode numbers 144 to 175: other forms of 1OP with different types.
# Zero-operand opcodes 0OP St	Br	Opcode	Hex 	V 	Inform name and syntax 	Link
# 		0OP:176	0 		rtrue 	rtrue
# 		0OP:177	1 		rfalse 	rfalse
# 		0OP:178	2 		print (literal-string)	print
# 		0OP:179	3 		print_ret (literal-string)	print_ret
# 		0OP:180	4 	1/- 	nop	nop
# 	* 	0OP:181	5 	1 	save ?(label)	save
# 				4 	save -> (result) 	save
# 				5 	[illegal]	
# 	* 	0OP:182	6 	1 	restore ?(label) 	restore
# 				4 	restore -> (result) 	restore
# 				5 	[illegal]	
# 		0OP:183	7 		restart 	restart
# 		0OP:184	8 		ret_popped 	ret_popped
# 		0OP:185	9 	1 	pop 	pop
# * 				5/6 	catch -> (result) 	catch
# 		0OP:186	A 		quit 	quit
# 		0OP:187	B 		new_line 	new_line
# 		0OP:188	C 	3 	show_status 	show_status
# 				4 	[illegal]	
# 	* 	0OP:189	D 	3 	verify ?(label) 	verify
# 		0OP:190	E 	5 	[first byte of extended opcode] 	extended
# 	* 	0OP:191	F 	5/- 	piracy ?(label) 	piracy
# 
# Opcode numbers 192 to 223: VAR forms of 2OP:0 to 2OP:31.
# Variable-operand opcodes VAR St	Br	Opcode	Hex 	V 	Inform name and syntax 	Link
# * 		VAR:224	0 	1 	call routine ...0 to 3 args... -> (result) 	call
# 				4 	call_vs routine ...0 to 3 args... -> (result) 	call_vs
# 		VAR:225	1 		storew array word-index value 	storew
# 		VAR:226	2 		storeb array byte-index value 	storeb
# 		VAR:227	3 		put_prop object property value 	put_prop
# 		VAR:228	4 	1 	sread text parse 	sread
# 				4 	sread text parse time routine 	sread
# * 				5 	aread text parse time routine -> (result) 	aread
# 		VAR:229	5 		print_char output-character-code 	print_char
# 		VAR:230	6 		print_num value 	print_num
# * 		VAR:231	7 		random range -> (result) 	random
# 		VAR:232	8 		push value 	push
# 		VAR:233	9 	1 	pull (variable) 	pull
# * 				6 	pull stack -> (result) 	pull
# 		VAR:234	A 	3 	split_window lines 	split_window
# 		VAR:235	B 	3 	set_window window 	set_window
# * 		VAR:236	C 	4 	call_vs2 routine ...0 to 7 args... -> (result) 	call_vs2
# 		VAR:237	D 	4 	erase_window window 	erase_window
# 		VAR:238	E 	4/- 	erase_line value 	erase_line
# 				6 	erase_line pixels 	erase_line
# 		VAR:239	F 	4 	set_cursor line column 	set_cursor
# 				6 	set_cursor line column window 	set_cursor
# 		VAR:240	10 	4/6 	get_cursor array 	get_cursor
# 		VAR:241	11 	4 	set_text_style style 	set_text_style
# 		VAR:242	12 	4 	buffer_mode flag 	buffer_mode
# 		VAR:243	13 	3 	output_stream number 	output_stream
# 				5 	output_stream number table 	output_stream
# 				6 	output_stream number table width 	output_stream
# 		VAR:244	14 	3 	input_stream number 	input_stream
# 		VAR:245	15 	5/3 	sound_effect number effect volume routine 	sound_effect
# * 		VAR:246	16 	4 	read_char 1 time routine -> (result) 	read_char
# * 	*	VAR:247	17 	4 	scan_table x table len form -> (result) 	scan_table
# * 		VAR:248	18 	5/6 	not value -> (result) 	not
# 		VAR:249	19 	5 	call_vn routine ...up to 3 args... 	call_vn
# 		VAR:250	1A 	5 	call_vn2 routine ...up to 7 args... 	call_vn2
# 		VAR:251	1B 	5 	tokenise text parse dictionary flag 	tokenise
# 		VAR:252	1C 	5 	encode_text zscii-text length from coded-text 	encode_text
# 		VAR:253	1D 	5 	copy_table first second size 	copy_table
# 		VAR:254	1E 	5 	print_table zscii-text width height skip 	print_table
# 	*	VAR:255	1F 	5 	check_arg_count argument-number 	check_arg_count
# 
# Extended opcodes EXT St	Br	Opcode	Hex 	V 	Inform name and syntax 	Link
# * 		EXT:0 	0 	5 	save table bytes name prompt -> (result) 	save
# * 		EXT:1 	1 	5 	restore table bytes name prompt -> (result) 	restore
# * 		EXT:2 	2 	5 	log_shift number places -> (result) 	log_shift
# * 		EXT:3 	3 	5/- 	art_shift number places -> (result) 	art_shift
# * 		EXT:4 	4 	5 	set_font font -> (result) 	set_font
# * 				6/- 	set_font font window -> (result) 	set_font
# 		EXT:5 	5 	6 	draw_picture picture-number y x 	draw_picture
# 	*	EXT:6 	6 	6 	picture_data picture-number array ?(label) 	picture_data
# 		EXT:7 	7 	6 	erase_picture picture-number y x 	erase_picture
# 		EXT:8 	8 	6 	set_margins left right window 	set_margins
# * 		EXT:9 	9 	5 	save_undo -> (result) 	save_undo
# * 		EXT:10	A 	5 	restore_undo -> (result) 	restore_undo
# 		EXT:11	B 	5/* 	print_unicode char-number 	print_unicode
# 		EXT:12	C 	5/* 	check_unicode char-number -> (result) 	check_unicode
# 		EXT:13	D 	5/* 	set_true_colour foreground background 	set_true_colour
# 				6/* 	set_true_colour foreground background window 	set_true_colour
# 		-------	E 	---	---	
# 		-------	F 	---	---	
# 		EXT:16	10 	6 	move_window window y x 	move_window
# 		EXT:17	11 	6 	window_size window y x 	window_size
# 		EXT:18	12 	6 	window_style window flags operation 	window_style
# * 		EXT:19	13 	6 	get_wind_prop window property-number -> (result) 	get_wind_prop
# 		EXT:20	14 	6 	scroll_window window pixels 	scroll_window
# 		EXT:21	15 	6 	pop_stack items stack 	pop_stack
# 		EXT:22	16 	6 	read_mouse array 	read_mouse
# 		EXT:23	17 	6 	mouse_window window 	mouse_window
# 	*	EXT:24	18 	6 	push_stack value stack ?(label) 	push_stack
# 		EXT:25	19 	6 	put_wind_prop window property-number value 	put_wind_prop
# 		EXT:26	1A 	6 	print_form formatted-table 	print_form
# 	*	EXT:27	1B 	6 	make_menu number table ?(label) 	make_menu
# 		EXT:28	1C 	6 	picture_table table 	picture_table
# * 		EXT:29	1D 	6/*	buffer_screen mode -> (result) 	buffer_screen 
# =============================================================================

    #checks for string, branch, return arguments
    def check_add(self):
    # OP
        
    
    # 1OP 
    
    # 2OP 

    # VAR 

# EXT