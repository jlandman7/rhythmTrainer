#!/usr/bin/env python3

n = 0
data = []


#sets up matrix with all permutations
def populate():
    matrix = []

    # generate all binary combos up to n digits
    for i in range(int(pow(2, n))):
        binNoZeroes = bin(i)[2:]
        if len(matrix) == binNoZeroes.count('1'):
            matrix.append([])
        matrix[binNoZeroes.count('1')].append(binNoZeroes.zfill(n))
        
    '''
    # pascals triangle reveal
    for i in range(0, len(matrix), 1):
        print(len(matrix[i]))
    '''
    
    permutate(matrix)


def permutate(matrix):
    # init submatrix
    subMatrix = []

    # for all hit #'s
    for i in range(0, n+1):

        # add a subgroup
        subMatrix.append([])
        b = -1

        # for every word
        for j in range(0, len(matrix[i])):

            # if said word is already in matrix, pass over
            a = 1
            for x in range(len(subMatrix[i])):
                if matrix[i][j] in subMatrix[i][x]:
                    a = 0

            # if word is not in matrix
            if a == 1:

                # add new subgroup
                subMatrix[i].append([])
                b += 1

                # add word + permutations into new subgroup
                for k in range(n, 0, -1):
                    while (matrix[i][j][1:]+matrix[i][j][:1]) not in subMatrix[i][b]:
                        subMatrix[i][b].append(matrix[i][j][k:] + matrix[i][j][:k])
                        k-=1
        '''
        def sortKey(e):
            return int((e))
        
        for j in range(len(subMatrix[i])):
            subMatrix[i][j].sort(key = sortKey, reverse=True)
        '''
    data.append(subMatrix)

    '''
    for i in range(len(subMatrix)):
        for j in range(len(subMatrix[i])):
            print(str(i) + " " + str(j) + " " + str(subMatrix[i][j]))
    '''


populate()


for n in range(1, 7):
    print("n: " + str(n))
    populate()

    for j in range(len(data[n])):
        print(data[n][j])


