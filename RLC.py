class RLC_ZigZag:
    def __init__(self,matrix,f):
        self.matrix=matrix
        self.f=f

    def zigzag(self):
        matrix=self.matrix
        rows=matrix.shape[0]
        columns=matrix.shape[0]
        solution=[[] for i in range(rows+columns-1)]
        for i in range(rows):
            for j in range(columns):
                sum=i+j
                if(sum%2 ==0):
                    solution[sum].insert(0,matrix[i][j])
                else:
                    solution[sum].append(matrix[i][j])    
        zigzag_list=[]
        for i in solution:
            for j in i:
                zigzag_list.append(int(j))
        #print(zigzag_list)
        RLC_ZigZag.RunlengthCode(zigzag_list,self.f)
        return
        
    def RunlengthCode(matrix,f):
        n=len(matrix)
        #print(n)
        count=1
        RLC=''
        #f = open("Compress.txt", "a")
        for i in range(n-1):
            if matrix[i]==matrix[i+1]:
                count += 1
            else:
                #RLC.append(matrix[i])
                #RLC.append(count)
                RLC=RLC+' '+ str(matrix[i])+' ' +str(count)
                count=1
        #RLC.append(matrix[i])
        #RLC.append(count)
        #f.write(str(matrix[i]))
        #f.write(str(count))
        RLC=RLC+' '+ str(matrix[i])+' ' +str(count)
        f.write(RLC)
        #print(RLC)
        
        #f.write(str(RLC))
        f.write('\n')
        #f.close()
        return 

