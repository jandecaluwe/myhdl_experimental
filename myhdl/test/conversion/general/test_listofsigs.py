from __future__ import absolute_import
from __future__ import print_function
from myhdl import *
from myhdl.conversion._toVerilog import ToVerilogError
from myhdl.conversion._toVHDL import ConversionError
from myhdl.conversion._misc import _error
from random import randint

N = 8
M= 2**N


### A first case that already worked with 5.0 list of signal constraints ###

def intbv2list():
    """Conversion between intbv and list of boolean signals."""
    
    a = Signal(intbv(0)[N:])
    b = [Signal(bool(0)) for i in range(len(a))]
    z = Signal(intbv(0)[N:])

    @always(a)
    def extract():
        for i in range(len(a)):
            b[i].next = a[i]

    @always(*b)
    def assemble():
        for i in range(len(b)):
            z.next[i] = b[i]

    @instance
    def stimulus():
        for i in range(M):
            a.next = i
            yield delay(10)
            assert z == a
            print(a)
        raise StopSimulation

    return extract, assemble, stimulus

# test

def test_intbv2list():
    assert conversion.verify(intbv2list) == 0
            
    
### A number of cases with relaxed constraints, for various decorator types ###

def inv1(z, a):
    @always(a)
    def logic():
        z.next = not a
    return logic


def inv2(z, a):
    @always_comb
    def logic():
        z.next = not a
    return logic


def inv3(z, a):
    @instance
    def logic():
        while True:
            yield a
            z.next = not a
    return logic

def inv4(z, a):
    @instance
    def logic():
        while True:
            yield a
            yield delay(1)
            z.next = not a
    return logic


def case1(z, a, inv):
    b = [Signal(bool(1)) for i in range(len(a))]
    c = [Signal(bool(0)) for i in range(len(a))]
    @always(a)
    def extract():
        for i in range(len(a)):
            b[i].next = a[i]

    inst = [None] * len(b)
    for i in range(len(b)):
        inst[i] = inv(c[i], b[i])

    @always(*c)
    def assemble():
        for i in range(len(c)):
            z.next[i] = c[i]

    return extract, inst, assemble


def case2(z, a, inv):
    b = [Signal(bool(1)) for i in range(len(a))]
    c = [Signal(bool(0)) for i in range(len(a))]
    @always_comb
    def extract():
        for i in range(len(a)):
            b[i].next = a[i]

    inst = [None] * len(b)
    for i in range(len(b)):
        inst[i] = inv(c[i], b[i])

    @always_comb
    def assemble():
        for i in range(len(c)):
            z.next[i] = c[i]

    return extract, inst, assemble


def case3(z, a, inv):
    b = [Signal(bool(1)) for i in range(len(a))]
    c = [Signal(bool(0)) for i in range(len(a))]
    @instance
    def extract():
        while True:
            yield a
            for i in range(len(a)):
                b[i].next = a[i]

    inst = [None] * len(b)
    for i in range(len(b)):
        inst[i] = inv(c[i], b[i])

    @instance
    def assemble():
        while True:
            yield c
            for i in range(len(c)):
                z.next[i] = c[i]

    return extract, inst, assemble


def case4(z, a, inv):
    b = [Signal(bool(1)) for i in range(len(a))]
    c = [Signal(bool(0)) for i in range(len(a))]
    @instance
    def extract():
        while True:
            yield a
            yield delay(1)
            for i in range(len(a)):
                b[i].next = a[i]

    inst = [None] * len(b)
    for i in range(len(b)):
        inst[i] = inv(c[i], b[i])

    @instance
    def assemble():
        while True:
            yield c
            yield delay(1)
            for i in range(len(c)):
                z.next[i] = c[i]

    return extract, inst, assemble






def processlist(case, inv):
    """Extract list from intbv, do some processing, reassemble."""
    
    a = Signal(intbv(1)[N:])
    z = Signal(intbv(0)[N:])

    case_inst = case(z, a, inv)

    @instance
    def stimulus():
        for i in range(M):
            yield delay(10)
            a.next = i
            yield delay(10)
            assert z == ~a
            print(z)
        raise StopSimulation

    return case_inst, stimulus


# functional tests
    
def test_processlist11():
    assert conversion.verify(processlist, case1, inv1) == 0
    
def test_processlist12():
    assert conversion.verify(processlist, case1, inv2) == 0
    
def test_processlist22():
    assert conversion.verify(processlist, case2, inv2) == 0
    
def test_processlist33():
    assert conversion.verify(processlist, case3, inv3) == 0

def test_processlist44():
    assert conversion.verify(processlist, case4, inv4) == 0



# signed and unsigned
def unsigned():
    z = Signal(intbv(0)[8:])
    a = [Signal(intbv(0)[8:]) for i in range(3)]

    @always_comb
    def logic():
        z.next = a[1] + a[2]

    @instance
    def stimulus():
        a[0].next = 2
        a[1].next = 5
        yield delay(10)
        print(z)

    return logic, stimulus


def test_unsigned():
    conversion.verify(unsigned)
        

def signed():
    z = Signal(intbv(0, min=-10, max=34))
    a = [Signal(intbv(0, min=-5, max=17)) for i in range(3)]

    @always_comb
    def logic():
        z.next = a[1] + a[2]

    @instance
    def stimulus():
        a[0].next = 2
        a[1].next = -5
        yield delay(10)
        print(z)

    return logic, stimulus


def test_signed():
    conversion.verify(signed)
        

def mixed():
    z = Signal(intbv(0, min=0, max=34))
    a = [Signal(intbv(0, min=-11, max=17)) for i in range(3)]
    b = [Signal(intbv(0)[5:]) for i in range(3)]

    @always_comb
    def logic():
        z.next = a[1] + b[2]

    @instance
    def stimulus():
        a[0].next = -6
        b[2].next = 15
        yield delay(10)
        print(z)

    return logic, stimulus


def test_mixed():
    conversion.verify(mixed)
        

### error tests

# port in list

def portInList(z, a, b):

    m = [a, b]

    @always_comb
    def logic():
        z.next = m[0] + m[1]

    return logic


def test_portInList():
    z, a, b = [Signal(intbv(0)[8:]) for i in range(3)]

    try:
        inst = conversion.analyze(portInList, z, a, b)
    except ConversionError as e:
        assert e.kind == _error.PortInList
    else:
        assert False
       
    
# signal in multiple lists

def sigInMultipleLists():

    z, a, b = [Signal(intbv(0)[8:]) for i in range(3)]

    m1 = [a, b]
    m2 = [a, b]

    @always_comb
    def logic():
        z.next = m1[0] + m2[1]

    return logic

def test_sigInMultipleLists():

    try:
        inst = conversion.analyze(sigInMultipleLists)
    except ConversionError as e:
        assert e.kind == _error.SignalInMultipleLists
    else:
        assert False

# list of signals as port
       
def my_register(clk, inp, outp):
    @always(clk.posedge)
    def my_register_impl():
        for index in range(len(inp)):
            outp[index].next = inp[index]
    return my_register_impl

def test_listAsPort():
    count = 3
    clk = Signal(False)
    inp = [Signal(intbv(0)[8:0]) for index in range(count)]
    outp = [Signal(intbv(0)[8:0]) for index in range(count)]
    try:
        inst = conversion.analyze(my_register, clk, inp, outp)
    except ConversionError as e:
        assert e.kind == _error.ListAsPort
    else:
        assert False


# signals in 2D lists

def sigIn2DLists(clk, reset, x, y, Nrows=4, Mcols=8):
    
    mem2d = [[Signal(intbv(randint(1, 7689), min=0, max=7690)) 
              for col in range(Mcols)] 
             for row in range(Nrows)]
    rcnt = Signal(intbv(0, min=0, max=Nrows))
    ccnt = Signal(intbv(0, min=0, max=Mcols))
    
    @always_seq(clk.posedge, reset=reset)
    def rtl():
        if ccnt == Mcols-1:
            if rcnt == Nrows - 1:
                rcnt.next = 0
            else :
                rcnt.next = rcnt + 1
            ccnt.next = 0
        else :
            ccnt.next = ccnt + 1
        
        mem2d[rcnt][ccnt].next = x
        y.next = mem2d[rcnt][ccnt]
 
    return rtl
    
def verify_sigIn2DLists():
    clk = Signal(bool(0))
    reset = ResetSignal(0, active=0, async=True)
    x = Signal(intbv(0, min=0, max=7690))
    y = Signal(intbv(1, min=0, max=7690))

    N,M = 4,8
    tbdut = sigIn2DLists(clk, reset, x, y, Nrows=N, Mcols=M)

    @always(delay(3))
    def tbclk():
        clk.next = not clk

    @instance
    def tbstim():
        x.next = 0
        reset.next = reset.active
        yield delay(33)
        reset.next = not reset.active
        yield clk.posedge
        yield clk.posedge

        # the default values are not 0
        for ii in range(N*M):
            assert y != 0
            yield clk.posedge
 
        for ii in range(N*M):
            assert y == 0
            yield clk.posedge

        raise StopSimulation

    return tbdut, tbclk, tbstim


def test_sigIn2DLists():
    Simulation(verify_sigIn2DLists()).run()

    clk = Signal(bool(0))
    reset = ResetSignal(0, active=0, async=True)
    x = Signal(intbv(0, min=0, max=7690))
    y = Signal(intbv(1, min=0, max=7690))
  
    try:
        inst = conversion.verify(sigIn2DLists, clk, reset, x, y)
    except ConversionError as e:
        print("Failed to convert to VHDL")
    except ToVerilogError as e:
        print("Failed to convert to Verilog")
    else:
        assert False
   
