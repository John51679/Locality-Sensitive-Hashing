import Bloomfilter as bf
import numpy as np
import random as r
import re
import string

#The Parse function preprocesses the input file
def Parse(input_text):
    X = open(input_text, "r+") #The file is stored in variable X with read+ permissions
    y = X.read() #Read the contents of the file
    y = re.sub('[' + string.punctuation + ']', '', y) #Remove the column points and '[','']' and replace them with the space.
    y = y.lower() #We convert every capital character to lowercase
    for i in range(len(y)):
        try:
            if (y[i] == '\n' or y[i] == ' ' or y[i] == '\t' or y[i] == '\\'): #extra check to replace both line changes and tabs with the blank.
                y = y.replace(y[i], '')
        except IndexError as IE: #Dynamic handling of memory as we release the data we "throw away"
            break

    return y

#Shingles Syntax takes the parsed file and the size of the shingles and splits the currently one whole word that makes up the entirety of the file into shingles of size k
def Shingles(parsed_text, k):
    shingle = [] #Initializing the shingles list
    for i in range(len(parsed_text) - k + 1):
        shingle.append('')
        for j in range(k):
            shingle[i] += parsed_text[j + i] #For every k characters in our file append the shingle list and place the word.

    """Filtering redundant shingles"""
    unique = [] #Initialize the unique list in order to remove duplicates.

    test = bf.ArrayInit(len(shingle), 0.05) #Application of bloom filters to find duplicates

    N = bf.Hash(len(shingle), len(test)) #Finding the optimal number of hash functions

    for i in shingle: #Removal of duplicates using the filter.
        not_found = True
        not_found = bf.Check(test, N, i)
        test = bf.Add(test, N, i)
        if not not_found: unique.append(i)

    return unique

"""The SMatrix function takes as arguments the parsed shingles and builds a Matrix containing the number of times that
a shingle appears per file."""
def SMatrix(Shingle_type_1, Shingle_type_2):  
    Merged = Shingle_type_1.copy() #We create a Merged variable that will contain the unions of the shingles of the files we are comparing.
    BloomArr = bf.ArrayInit(len(Shingle_type_1), 0.05) #We use the bloom filter to get a more efficient searching for the data.

    k = bf.Hash(len(Shingle_type_1), len(BloomArr)) #We calculate the k of the bloom filters.
    for i in Merged:
        BloomArr = bf.Add(BloomArr, k, i) #We add the matrix data to the filter.
    for i in Shingle_type_2: #With this for we avoid the possibility of having duplicates in the merged list.
        Not_Found = True
        Not_Found = bf.Check(BloomArr, k, i)
        if not Not_Found: Merged.append(i)

    Matrix = np.zeros([len(Merged),2]) #We pre-allocate the Matrix matrix.

    for i in range(len(Matrix)):
        Matrix[i, 0] = Shingle_type_1.count(Merged[i])
        Matrix[i, 1] = Shingle_type_2.count(Merged[i])

    return Matrix

"""This function will be used to construct the permutations to be used later."""
def Permutations(Input_Matrix, Number_Of_Permutations):
    lines = len(Input_Matrix[:]) #size of the matrix as much as the shingles are.
    init = []
    #We construct a one-dimensional list from 1 to our lines and give them values in order starting from 1.
    for i in range(1,lines):
        init.append(i)

    p = []
    #We take the Init list we constructed above and shuffle its contents.
    for i in range(Number_Of_Permutations):
        temp = init.copy()
        r.shuffle(temp)
        p.append(temp)
    p = np.transpose(p)
    return p

"""This function will be used to create the signature"""
def Signature(Permutations, Input_Matrix):
    #pre-allocation of the Sign matrix which will end up being containing the signatures.
    Sign = np.zeros([len(Permutations[0, :]), len(Input_Matrix[0, :])])
    
    #This for generates the line-by-line signature for each file.
    for i in range(len(Input_Matrix[0, :])):
        t = []
        for j in range(len(Permutations[0, :])):
            temp = Permutations[:, j].copy()
            flag = False
            while (not flag):
                minimum = np.argmin(temp)
                if (int(Input_Matrix[minimum, i]) == 1):
                    flag = True
                else:
                    temp[minimum] = 99999

            t.append(temp[minimum])
        Sign[0:len(t), i] = t

    return Sign

"""This function will be used optionally to verify the signature similarity result and if necessary, measure the resulting error."""
def JaccardSim(smatrix):
    Jac = []
    #The similarity jaccard takes the matrix union and intersection and performs the intersection/union operation to compute the similarity.
    for k in range(len(smatrix[0, :])):
        for i in range(k + 1, len(smatrix[0, :])):
            intersection = 0
            union = 0
            for j in range(len(smatrix[:])):
                if (smatrix[j, k] == 1.0 or smatrix[j, i] == 1.0):
                    union += 1
                if (smatrix[j, k] == 1.0 and smatrix[j, i] == 1.0):
                    intersection += 1

            Jac.append(intersection / union)
    return Jac

"""The approximate Similarity calculation function."""
def PermutationSim(signature):
    #Signature similarity takes the union and intersection of the Signature matrix and performs the intersection/union operation.
    Sim = []
    union = len(signature[:])
    for i in range(len(signature[0, :])):
        for j in range(i + 1, len(signature[0, :])):
            same = 0
            for k in range(len(signature[:])):
                # print('i,j,k = ', i, ' ', j, ' ', k)
                if (signature[k, i] == signature[k, j]):
                    same += 1
            Sim.append(same / union)

    return Sim