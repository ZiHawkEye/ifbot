class Frame(): 
    def __init__(self, pc, localvars, result=None):
        self.pc = pc
        # creates a copy of localvars not merely an assignment
        self.localvars = localvars[:]
        self.routine_stack = []
        self.result = result

    def get_pc(self):
        return self.pc
    
    def get_localvar(self, var):
        assert (var <= 1 and var >= 15), "There are only up to 15 local variables per frame"
        return self.localvars[var - 1]

    def pop_routine_stack(self):
        return self.routine_stack.pop()

    def get_result(self):
        return self.result

    def set_pc(self, pc):
        self.pc = pc

    def set_localvar(self, value, var):
        assert (var <= 1 and var >= 15), "There are only up to 15 local variables per frame"
        self.localvars[var - 1] = value

    def push_routine_stack(self, value):
        self.routine_stack.append(value)

    def set_result(self, result):
        self.result = result
    

class Frame3(Frame): 
    def __init__(self, pc, localvars, ret, result=None):
        Frame.__init__(self, pc, localvars, result)
        self.ret = ret

    def get_ret(self):
        return self.ret

    def set_ret(self, ret):
        self.ret = ret

class Frame5(Frame3): 
    def __init__(self, pc, localvars, ret, n, result=None, framep=None):
        Frame3.init(self, pc, localvars, ret, result)
        self.n = n
        self.framep = framep

    def get_framep(self):
        return self.framep

    def get_n(self):
        return self.n

    def set_framep(self, framep):
        self.framep = framep

    def set_n(self, n):
        self.n = n