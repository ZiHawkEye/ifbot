# -*- coding: utf-8 -*-
"""
Created on Wed May 16 23:34:51 2018

@author: User
"""
from operations import *

def ops(op_table, 
        kind, op_num, 
        name='', is_str=False, is_br=False, is_res=False, types=[],
        is_null=False):
    
    if is_null:
        op_table[kind].insert(op_num, {}) #should mutate the table passed in
    else:
        instr_details = {"name": name, 
                        "types": types, 
                        "is_str": is_str, 
                        "is_br": is_br, 
                        "is_res": is_res}

        op_table[kind].insert(op_num, instr_details)

#TODO
#add arg types
def make_table(ver_num):
    op_table = [[], [], [], [], []]

    #0OP
    ops(op_table,     0, 0,  'rtrue')
    ops(op_table,     0, 1,  'rfalse')
    ops(op_table,     0, 2,  'print_', is_str=True)
    ops(op_table,     0, 3,  'print_rtrue', is_str=True)
    ops(op_table,     0, 4,  'nop')
    
    if ver_num in [1, 2, 3]:
        ops(op_table, 0, 5,  'save_b',                      is_br=True)
        ops(op_table, 0, 6,  'restore_b',                   is_br=True)
    elif ver_num == 4:
        ops(op_table, 0, 5,  'save_r',         is_res=True)
        ops(op_table, 0, 6,  'restore_r',      is_res=True)
    else:
        ops(op_table, 0, 5, is_null=True)
        ops(op_table, 0, 6, is_null=True)
        
    ops(op_table,     0, 7,  'restart')
    ops(op_table,     0, 8,  'retpulled')
    
    if ver_num in [1, 2, 3, 4]:
        ops(op_table, 0, 9,  'pop')
    elif ver_num >= 5:
        ops(op_table, 0, 9,  'catch',          is_res=True)
        
    ops(op_table,     0, 10, 'quit_')
    ops(op_table,     0, 11, 'new_line')
    
    if ver_num == 3:
        ops(op_table, 0, 12, 'show_status')
    else:
        ops(op_table, 0, 12, is_null=True)
    
    if ver_num >= 3:
        ops(op_table, 0, 13, 'verify',                      is_br=True)
    else:
        ops(op_table, 0, 13, is_null=True)
        
    #first byte of an extended instruction in v5+
    ops(op_table,     0, 14, is_null=True)
    
    if ver_num >= 5:
        ops(op_table, 0, 15, 'piracy',                      is_br=True)
    else:
        ops(op_table, 0, 15, is_null=True)
        
        
    #1OP
    ops(op_table,     1, 0,  'jz',                          is_br=True, types=["u"])
    ops(op_table,     1, 1,  'get_sibling',    is_res=True, is_br=True, types=["obj"])
    ops(op_table,     1, 2,  'get_child',      is_res=True, is_br=True, types=["obj"])
    ops(op_table,     1, 3,  'get_parent',     is_res=True,             types=["obj"])
    ops(op_table,     1, 4,  'get_prop_len',   is_res=True,             types=["baddr"])
    ops(op_table,     1, 5,  'inc',                                     types=["var"])
    ops(op_table,     1, 6,  'dec',                                     types=["var"])
    ops(op_table,     1, 7,  'print_addr',                              types=["baddr"])
    
    if ver_num == 4:
        ops(op_table, 1, 8,  'call_f0',        is_res=True,             types=["raddr"])
    else:
        ops(op_table, 1, 8,  is_null=True)
        
    ops(op_table,     1, 9,  'remove_obj',                              types=["obj"])
    ops(op_table,     1, 10, 'print_obj',                               types=["obj"])
    ops(op_table,     1, 11, 'ret',                                     types=["u"])
    ops(op_table,     1, 12, 'jump',                                    types=["s"])
    ops(op_table,     1, 13, 'print_paddr',                             types=["saddr"])
    ops(op_table,     1, 14, 'load',           is_res=True,             types=["var"])
    
    if ver_num in [1, 2, 3, 4]:
        ops(op_table, 1, 15, 'not_',           is_res=True,             types=["u"])
    elif ver_num >= 5:
        ops(op_table, 1, 15, 'call_p0',                                 types=["raddr"])
    
    
    #2OP
    ops(op_table,     2, 0,  is_null=True)
    ops(op_table,     2, 1,  'je',                          is_br=True, types=["u", "u", "u", "u"])
    ops(op_table,     2, 2,  'jl',                          is_br=True, types=["s", "t"])
    ops(op_table,     2, 3,  'jg',                          is_br=True, types=["s", "t"])
    ops(op_table,     2, 4,  'dec_jl',                      is_br=True, types=["var", "s"])
    ops(op_table,     2, 5,  'inc_jg',                      is_br=True, types=["var", "t"])
    ops(op_table,     2, 6,  'jin',                         is_br=True, types=["obj", "u"])
    ops(op_table,     2, 7,  'test',                        is_br=True, types=["u", "u"])
    ops(op_table,     2, 8,  'or_',            is_res=True,             types=["u", "u"])
    ops(op_table,     2, 9,  'and_',           is_res=True,             types=["u", "u"])
    ops(op_table,     2, 10, 'test_attr',                   is_br=True, types=["obj", "attr"])
    ops(op_table,     2, 11, 'set_attr',                                types=["obj", "attr"])
    ops(op_table,     2, 12, 'clear_attr',                              types=["obj", "attr"])
    ops(op_table,     2, 13, 'store',                                   types=["var", "u"])
    ops(op_table,     2, 14, 'insert_obj',                              types=["obj", "obj"])
    ops(op_table,     2, 15, 'loadw',          is_res=True,             types=["baddr", "u"])
    ops(op_table,     2, 16, 'loadb',          is_res=True,             types=["obj", "u"])
    ops(op_table,     2, 17, 'get_prop',       is_res=True,             types=["obj", "prop"])
    ops(op_table,     2, 18, 'get_prop_addr',  is_res=True,             types=["obj", "prop"])
    ops(op_table,     2, 19, 'get_next_prop',  is_res=True,             types=["obj", "prop"])
    ops(op_table,     2, 20, 'add',            is_res=True,             types=["u", "u"])
    ops(op_table,     2, 21, 'sub',            is_res=True,             types=["u", "u"])
    ops(op_table,     2, 22, 'mul',            is_res=True,             types=["u", "u"])
    ops(op_table,     2, 23, 'div',            is_res=True,             types=["u", "u"])
    ops(op_table,     2, 24, 'mod',            is_res=True,             types=["u", "u"])
    
    if ver_num >= 4:
        ops(op_table, 2, 25, 'call_f1',        is_res=True,             types=["raddr", "u"])
    else:
        ops(op_table, 2, 25, is_null=True)
    
    if ver_num >= 5:    
        ops(op_table, 2, 26, 'call_p1',                                 types=["raddr", "u"])
        ops(op_table, 2, 27, 'set_colour',                              types=["u", "u"])
        ops(op_table, 2, 28, 'throw',                                   types=["u", "u"])
    else:
        ops(op_table, 2, 26, is_null=True)
        ops(op_table, 2, 27, is_null=True)
        ops(op_table, 2, 28, is_null=True)
        
    ops(op_table,     2, 29, is_null=True)
    ops(op_table,     2, 30, is_null=True)
    ops(op_table,     2, 31, is_null=True)
    
    
    #VAR
    ops(op_table,     3, 0,  'call_fv',        is_res=True,             types=["raddr", "u", "u", "u"])    
    ops(op_table,     3, 1,  'store_w',                                 types=["baddr", "u", "u"])    
    ops(op_table,     3, 2,  'store_b',                                 types=["baddr", "u", "byte"])    
    ops(op_table,     3, 3,  'put_prop',                                types=["obj", "prop", "u"])    
    
    if ver_num in [1, 2, 3]:
        ops(op_table, 3, 4,  'read',                                    types=["baddr", "baddr"])
    elif ver_num == 4:
        ops(op_table, 3, 4,  'read_t',                                  types=["baddr", "baddr", "time"])    
    elif ver_num >= 5:
        ops(op_table, 3, 4,  'read_r',         is_res=True,             types=["baddr", "baddr", "time"])    
        
    ops(op_table,     3, 5,  'print_char',                              types=["u"])    
    ops(op_table,     3, 6,  'print_num',                               types=["s"])    
    ops(op_table,     3, 7,  'random',         is_res=True,             types=["s"])    
    ops(op_table,     3, 8,  'push',                                    types=["u"])    
    
    if ver_num in [1, 2, 3, 4, 5]:
        ops(op_table, 3, 9,  'pull',                                    types=["var"])
    elif ver_num >= 6:
        ops(op_table, 3, 9,  'pull_b',                                  types=["baddr", "var"])#baddr is optional but this is also unused    
    
    if ver_num >= 3:
        ops(op_table, 3, 10, 'split_screen',                            types=["u"])    
        ops(op_table, 3, 11, 'set_window',                              types=["window"])    
    else:
        ops(op_table, 3, 10, is_null=True)    
        ops(op_table, 3, 11, is_null=True)    
    
    if ver_num >= 4:
        ops(op_table, 3, 12, 'call_fd',        is_res=True,             types=["raddr", "u", "u", "u", "u", "u", "u", "u"])    
        ops(op_table, 3, 13, 'erase_window',                            types=["window"])
    else:
        ops(op_table, 3, 12, is_null=True)    
        ops(op_table, 3, 13, is_null=True)
    
    if ver_num in [4, 5]:
        ops(op_table, 3, 14, 'erase_line')    
    elif ver_num == 6:
        ops(op_table, 3, 14, 'erase_line_n',                            types=["u"])    
    else: 
        ops(op_table, 3, 14, is_null=True)
    
    if ver_num in [4, 5]:
        ops(op_table, 3, 15, 'set_cursor',                              types=["s", "u"])    
    elif ver_num == 6:
        ops(op_table, 3, 15, 'set_cursor_w',                            types=["s", "u", "window"])    
    else: 
        ops(op_table, 3, 15, is_null=True)    
    
    if ver_num >= 4:
        ops(op_table, 3, 16, 'get_cursor',                              types=["baddr"])    
        ops(op_table, 3, 17, 'set_text_style',                          types=["u"])    
        ops(op_table, 3, 18, 'buffer_mode',                             types=["bit"])    
    else:
        ops(op_table, 3, 16, is_null=True)    
        ops(op_table, 3, 17, is_null=True)    
        ops(op_table, 3, 18, is_null=True)    
        
    if ver_num in [3, 4]:
        ops(op_table, 3, 19, 'output_streams',                          types=["s"])    
    elif ver_num == 5:
        ops(op_table, 3, 19, 'output_streams_b',                        types=["s", "baddr"])    
    elif ver_num == 6:
        ops(op_table, 3, 19, 'output_streams_bw',                       types=["s", "baddr", "u"])
    else:
        ops(op_table, 3, 19, is_null=True)        
    
    if ver_num >= 3:
        ops(op_table, 3, 20, 'input_stream',                            types=["u"])    
        ops(op_table, 3, 21, 'sound',                                   types=["u", "u", "time", "raddr"])    
    else:
        ops(op_table, 3, 20, is_null=True)    
        ops(op_table, 3, 21, is_null=True)            
    
    if ver_num >= 4:
        ops(op_table, 3, 22, 'read_char',      is_res=True,             types=["u", "time", "raddr"])
        ops(op_table, 3, 23, 'scan_table',     is_res=True, is_br=True, types=["u", "baddr", "u", "byte"])
    else:
        ops(op_table, 3, 22, is_null=True)
        ops(op_table, 3, 23, is_null=True)
        
    if ver_num >= 5:
        ops(op_table, 3, 24, 'not_',           is_res=True,             types=["u"]) #same as 1OP:15
        ops(op_table, 3, 25, 'call_pv',                                 types=["raddr", "u", "u", "u"])
        ops(op_table, 3, 26, 'call_pd',                                 types=["raddr", "u", "u", "u", "u", "u", "u"])
        ops(op_table, 3, 27, 'tokenise',                                types=["baddr", "baddr", "baddr", "bit"])
        ops(op_table, 3, 28, 'encode_text',                             types=["baddr", "u", "u", "baddr"])
        ops(op_table, 3, 29, 'copy_table',                              types=["baddr", "baddr", "u"])
        ops(op_table, 3, 30, 'print_table',                             types=["baddr", "u", "u", "u"])
        ops(op_table, 3, 31, 'check_arg_count',             is_br=True, types=["u"])
    else:
        ops(op_table, 3, 24, is_null=True) #same as 1OP:15
        ops(op_table, 3, 25, is_null=True)
        ops(op_table, 3, 26, is_null=True)
        ops(op_table, 3, 27, is_null=True)
        ops(op_table, 3, 28, is_null=True)
        ops(op_table, 3, 29, is_null=True)
        ops(op_table, 3, 30, is_null=True)
        ops(op_table, 3, 31, is_null=True)
    
    
    #EXT - only for v5+
    if ver_num >= 5:
        ops(op_table,     4, 0,  'save',       is_res=True,             types=["baddr", "u", "baddr"])
        ops(op_table,     4, 1,  'restore',    is_res=True,             types=["baddr", "u", "baddr"])
        ops(op_table,     4, 2,  'log_shift',  is_res=True,             types=["u", "s"])
        ops(op_table,     4, 3,  'art_shift',  is_res=True,             types=["u", "s"])
    
    if ver_num == 5:
        ops(op_table,     4, 4,  'set_font',   is_res=True,             types=["u"])
    elif ver_num == 6:    
        ops(op_table,     4, 4,  'set_font_w', is_res=True,             types=["u", "window"])  
    else:
        ops(op_table,     4, 4,  is_null=True)        
    
    if ver_num == 6:
        ops(op_table, 4, 5,  'draw_picture',                            types=["pic", "u", "u"])
        ops(op_table, 4, 6,  'picture_data',                is_br=True, types=["pic", "baddr"])  
        ops(op_table, 4, 7,  'erase_picture',                           types=["pic", "u", "u"])
        ops(op_table, 4, 8,  'set_margins',                             types=["u", "u", "window"])
    else:
        ops(op_table, 4, 5,  is_null=True)
        ops(op_table, 4, 6,  is_null=True)
        ops(op_table, 4, 7,  is_null=True)
        ops(op_table, 4, 8,  is_null=True)
    
    if ver_num >= 5:
        ops(op_table, 4, 9,  'save_undo',      is_res=True)
        ops(op_table, 4, 10, 'restore_undo',   is_res=True)
    
    ops(op_table,     4, 11, is_null=True)
    ops(op_table,     4, 12, is_null=True)
    ops(op_table,     4, 13, is_null=True)
    ops(op_table,     4, 14, is_null=True)
    ops(op_table,     4, 15, is_null=True)
    
    if ver_num == 6:
        ops(op_table, 4, 16, 'move_window',                             types=["window", "u", "u"])
        ops(op_table, 4, 17, 'window_size',                             types=["window", "u", "u"])
        ops(op_table, 4, 18, 'window_style',                            types=["window", "u", "u"])
        ops(op_table, 4, 19, 'get_wind_prop',  is_res=True,             types=["window", "u"])
        ops(op_table, 4, 20, 'scroll_window',                           types=["window", "s"])
        ops(op_table, 4, 21, 'pop_stack',                               types=["u", "baddr"])
        ops(op_table, 4, 22, 'read_mouse',                              types=["baddr"])
        ops(op_table, 4, 23, 'mouse_window',                            types=["window"])
        ops(op_table, 4, 24, 'push_stack',                 is_br=True,  types=["u", "baddr"])
        ops(op_table, 4, 25, 'put_wind_prop',                           types=["window", "u", "u"])
        ops(op_table, 4, 26, 'print_form',                              types=["baddr"])
        ops(op_table, 4, 27, 'make_menu',                  is_br=True,  types=["u", "baddr"])
        ops(op_table, 4, 28, 'picture_table',                           types=["baddr"])

    return op_table