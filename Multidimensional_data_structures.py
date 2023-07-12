import Shingles as sh
import time
import math


filesNo = int(input("Provide the directory with the documents: ")) #Set the document directory

DocTest = [] #List containing the files we will check
DocNames = [] #A list containing the names of the files we imported
parsed_texts = [] #List containing the pre-processed version of the files
shingles = [] #List containing the shingles vector for each file

for c in range(filesNo): #Check for correctness of file import and record the correct ones in the corresponding lists.

    DocTest.append('NULL')
    end = False

    while (not end): #As long as the user gives incorrect input, request input again.
        try:
            checked = True
            kati = input("Give me the name of the text file or its directory path\n")
            text1 = open(kati)
            testing = [text1.read()]

            DocTest[c] = kati

            for k in range(len(DocTest) - 1):
                if (DocTest[k] == kati): checked = False
            if (checked == True):
                DocNames.append(DocTest[c])
                end = True

            else:
                print('A Document with that name was already given. Please try again!\n')

        except OSError as error:
            print('Error: File does not exist. Please try again!\n')
    parsed_texts.append(sh.Parse(DocNames[c])) #Placing in the list of pre-processed files
    shingles.append(sh.Shingles(parsed_texts[c],3)) #Place in the list the resulting shingles for each file.



start = time.time() #Start timer
candidates = [] #Initialize a candidates list that will store candidate files for comparison.
#Compare all possible file combinations without repetition
for i in range(len(DocNames)):
    for j in range(i+1,len(DocNames)):
        #if (i == j): continue
        #print("We are talking about files: {0} and {1}".format(DocNames[i],DocNames[j]))
        matrix = sh.SMatrix(shingles[i],shingles[j]) #Save the generated matrix for a pair
        #jac = sh.JaccardSim(matrix)
        #l = sh.Permutations(matrix,100)
        #l = sh.Signature(l,matrix)
        #l = sh.PermutationSim(l)
        #print(jac)

        n = len(matrix[:]) #Storage of the number of lines in the matrix

        #Using the maximum common divisor method to compute a good combination of bands and rows for the LSH implementation.
        GCD = math.gcd(n, 2)
        bands = int(n / GCD)
        rows = int(n / bands)
        for prime_check in range(4):
            for g in range(2, 11):
                if (rows > 10): break
                if (GCD == 1):
                    GCD = math.gcd(bands, g)
                    #print("For i {0} we have GCD = {1}".format(g, GCD))

                else:
                    while (GCD != 1 and rows < 10):
                        #print("mpainw edw gia to i {}".format(g - 1))
                        GCD = math.gcd(bands, g - 1)
                        temp = bands
                        bands = int(temp / GCD)
                        rows = int(n / bands)
                        if (rows > 30):
                            bands = temp
                            rows = int(n / bands)
                            break
            #print("bands = {0}, rows = {1}, n = {2}, bands * rows = {3}".format(bands, rows, n, bands*rows))
            if (bands * rows != n):
                n += 1
                band = n
            if (rows < 10 and prime_check > 1 and prime_check < 3):
                bands += 1
                n += rows
            elif(rows < 10 and prime_check == 3): break
                #rows = int(n/bands)
            if (rows > 10): break

        #In case n is a prime number we handle it by predicting that an error will occur which we correct along the way to avoid an out of bounds exception or loss of information.
        #There is no chance of false positive occurring with this correction because of the way the matrix is created which makes sure that we don't have identical elements in the last positions of the matrix.
        error = 0
        for k in range(bands):
            same = 0
            if (k == (bands - 1)):
                error = bands*rows - len(matrix)
                rows = rows - error
            for p in range(rows):
                if (matrix[k*(rows + error) + p,0] == matrix[k*rows + p,1]):
                    same += 1
            if(same == rows):
                candidates.append([i,j]) #If all elements in a band are identical place the pair in the candidates list.
                #print(candidates)
                break

print(candidates) #Display on the candidates list screen



for i in range(len(candidates)): #Now we find the similarity of the pairs we considered as candidates from the above procedure.
    m = sh.SMatrix(shingles[candidates[i][0]], shingles[candidates[i][1]])
    jac = sh.JaccardSim(m) #Finding Jaccard Similarity of the pair for comparison with the approximate minhash method.
    print("We are talking about files {0} and {1}".format(DocNames[candidates[i][0]],DocNames[candidates[i][1]]))
    print(jac)
    sim = sh.Permutations(m,10) #Create 10 permutation vectors for the m matrix
    sim = sh.Signature(sim,m) #Creation of the Signature matrix
    sim = sh.PermutationSim(sim) #Calculation of the approximate similarity with the minhash method
    print(sim)

end = time.time() #End of timer
print("Time elapsed is {} seconds!".format(end - start)) #Display on the screen the total running time of the whole process.
