# -*- coding: utf-8 -*-

def setBit(int_type, offset):
    mask = 1 << offset
    return(int_type | mask)

def clearBit(int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)

def testBit(int_type, offset):
    mask = 1 << offset
    return(int_type & mask)