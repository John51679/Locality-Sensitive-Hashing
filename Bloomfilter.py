from bitarray import bitarray
import mmh3
import numpy as np


def ArrayInit(Input_num,False_Positive_Posibility): #Initialization of the bit array with known number of inputs and probability of false positive
    m = int(- np.log(False_Positive_Posibility) * Input_num  / (np.log(2)) ** 2) #calculation of the optimal size of the bit array
    ba = bitarray(m) #initialization of the size of the bit array of size m
    ba.setall(False) #Initialize the bit_array values with zeros
    return ba

def Hash(Input_num,BitArraySize):
    k = int(np.log(2) * BitArraySize / Input_num) #Finding optimal number of hash functions
    return k

def Add(Bit_Array,NumOfHashes,item): #Adding an item to the filter
    #kati = [] #Temporary list containing the results of the hash functions
    for i in range(NumOfHashes):
        katis = mmh3.hash(item, i) % len(Bit_Array) #Use mmh3 library for hashing the element i in the bit array
        #kati.append(katis)
        Bit_Array[katis] = True #Wherever the result of the hash function lands change the value in that position to '1'
    return Bit_Array

def Check(Bit_Array,NumOfHashes,item): #Check for the presence of an element inside the filter
    for i in range(NumOfHashes):
        katis = mmh3.hash(item, i) % len(Bit_Array) #Use mmh3 library for hashing the element i in the bit array
        if (not Bit_Array[katis]): #If all bit array elements with the hash function results as indexes are 1 then return TRUE otherwise FALSE
            return False
    return True #True here is not absolute. It indicates that the element may be in the filter.