from myhdl import *

def bench_SliceSignal():
    
    s = Signal(intbv(0)[8:])
    a, b, c = s(7), s(5), s(0)
    d, e, f, g = s(8,5), s(6,3), s(8,0), s(4,3)
    N = len(s) 

    @instance
    def check():
        for i in range(N):
            s.next = i
            yield delay(10)
            print int(a)
            print int(b)
            print int(c)
            print d
            print e
            print f
            print g

    return check


def test_SliceSignal():
    assert conversion.verify(bench_SliceSignal) == 0


def bench_ConcatSignal():
    
    a = Signal(intbv(0)[5:])
    b = Signal(bool(0))
    c = Signal(intbv(0)[3:])
    d = Signal(intbv(0)[4:])
    
    s = ConcatSignal(a, b, c, d)

    I = 2**len(a)
    J = 2**len(b)
    K = 2**len(c)
    M = 2**len(d)
    @instance
    def check():
        for i in range(I):
            for j in range(J):
                for k in range(K):
                    for m in range(M):
                        a.next = i
                        b.next = j
                        c.next = k
                        d.next = m
                        yield delay(10)
                        print s

    return check


def test_ConcatSignal():
    assert conversion.verify(bench_ConcatSignal) == 0




def bench_TristateSignal():
    s = TristateSignal(intbv(0)[8:])
    a = s.driver()
    b = s.driver()
    c = s.driver()

    @instance
    def check():
        a.next = None
        b.next = None
        c.next = None
        yield delay(10)
        print s
        a.next = 1
        yield delay(10)
        print s
        a.next = None
        b.next = 122
        yield delay(10)
        print s
        b.next = None
        c.next = 233
        yield delay(10)
        print s
        c.next = None
        yield delay(10)
        print s
    
    return check


def test_TristateSignal():
    assert conversion.verify(bench_TristateSignal) == 0