import numpy as np
from scipy.fftpack import idct

class Inverse_Quantization:
    def __init__(self,matrix,channel,level,iterations):
        self.matrix=matrix
        self.channel=channel
        self.level=level
        self.iterations=iterations
    
    def IQ(self):
        matrix=self.matrix
        quantization_matrix_Y = np.array([
                [16, 11, 10, 16, 24, 40, 51, 61],
                [12, 12, 14, 19, 26, 58, 60, 55],
                [14, 13, 16, 24, 40, 57, 69, 56],
                [14, 17, 22, 29, 51, 87, 80, 62],
                [18, 22, 37, 56, 68, 109, 103, 77],
                [24, 35, 55, 64, 81, 104, 113, 92],
                [49, 64, 78, 87, 103, 121, 120, 101],
                [72, 92, 95, 98, 112, 100, 103, 99]
            ])
        if(self.iterations == 0): #for Independent frame
            quantization_matrix_CbCr = np.array([
                    [17, 18, 24, 47, 99, 99, 99, 99],
                    [18, 21, 26, 66, 99, 99, 99, 99],
                    [24, 26, 56, 99, 99, 99, 99, 99],
                    [47, 66, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99],
                    [99, 99, 99, 99, 99, 99, 99, 99]
                ])
        else: #for Predictive frame
            quantization_matrix_CbCr=5

        if(self.channel== 0 ):
            quantization_matrix_Y = np.around((quantization_matrix_Y*self.level))
            unquantized_blocks = np.around(matrix*quantization_matrix_Y) 
            #print(unquantized_blocks)
        
        else:
            quantization_matrix_CbCr = np.around((quantization_matrix_CbCr*self.level))
            unquantized_blocks = np.around(matrix*quantization_matrix_CbCr)
        
        #inverse DCT
        idct_img=idct(idct(unquantized_blocks.T,norm='ortho').T,norm='ortho')
        #print("idct")
        #print(idct_img)
        return idct_img