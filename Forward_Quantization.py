#code is similar to the image compression and there are few changes only in here
from scipy.fft import dct
import numpy as np
import RLC as rlc
import Inverse_Quantization

class Forward_Quantization:
    def __init__(self,Y,Cb,Cr,level,type,frames,fps):
        self.Y=Y
        self.Cb=Cb
        self.Cr=Cr
        self.level=level
        self.type=type
        self.frames=frames
        self.fps=fps
        
    def macroBlock(image): #convert to 8*8 blocks
        height, width = image.shape
        macroblocks_height = height // 8
        macroblocks_width = width // 8
        macroblocks = np.zeros((macroblocks_height, macroblocks_width, 8, 8))
        for y in range(macroblocks_height):
            for x in range(macroblocks_width):
                macroblocks[y, x] = image[y*8:(y+1)*8, x*8:(x+1)*8]
        return macroblocks
    
    def DCT(macro_image,flag,level,f,matrix,types): #get DCT transform
        #print(matrix)
        macroblocks_height,macroblocks_width,_,_=macro_image.shape
        if(flag=="Y"):
            channel=0
        elif(flag=="Cb"):
            channel=1
        else:
            channel=2
        for i in range(macroblocks_height):
            for j in range(macroblocks_width):
                
                #print(macro_image[i][j])
                dct_img=dct(dct(macro_image[i][j].T,norm='ortho').T,norm='ortho')
                #print(dct_img)
                dct_img_Q=Forward_Quantization.qunatize(dct_img,level,flag,types)
                #print(dct_img_Q)
                iterations=0
                '''if(types=="V"):
                    dct_img_Q=Forward_Quantization.qunatize(dct_img,level,flag)
                    iterations=0
                else:
                    dct_img_Q=dct_img
                    iterations=1
                    pass'''
                #print(dct_img_Q)
                #Inverse Qunatice and apply IDCT to save image in buffer for motion compensatition
                
                Inverse_Q=Inverse_Quantization.Inverse_Quantization(dct_img_Q,channel,level,iterations)
                idct_img=Inverse_Q.IQ()
                matrix[int(i)][int(j)][channel]=idct_img
                #print("************************************")
                #print(idct_img)
                #I_matrix=Forward_Quantization.I_qunatize(dct_img_Q,flag,level,matrix,i,j)
                
                RunLength=rlc.RLC_ZigZag(dct_img_Q,f)
                RunLength.zigzag()
        return matrix

    def qunatize(macroblocks_dct,level,flag,types): #Quantization procerss
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
        if(types=="V"): #used for independent frames
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
        else: #used for Predictive frames
            quantization_matrix_CbCr=5
        #quantization
        if(flag=="Y"):
            
            quantization_matrix_Y = np.around((quantization_matrix_Y*level))
            quantized_blocks = np.around(macroblocks_dct/(quantization_matrix_Y))
          
            
        elif(flag=="Cb" or flag=="Cr"):
            quantization_matrix_CbCr = np.around((quantization_matrix_CbCr*level))
            quantized_blocks = np.around(macroblocks_dct/(quantization_matrix_CbCr))
        
        return quantized_blocks

    def Forward_Quantization(self):
        '''image = np.zeros((height, width,3))
        for j in range(3):
            for y in range(height):
                for x in range(width):
                    block = self.matrix[y, x, j]
                    image[y*8:(y+1)*8, x*8:(x+1)*8,j] = block'''
        level=self.level
        height,width=self.Y.shape
        frames=self.frames
        #set the header of the txt file
        info="height: "+str(height)+" Width: "+str(width)+" Levels: "+str(level)+" Block: "+str(8)+" Frames: "+str(frames)+" FPS: "+str(self.fps)
        
        
        f = open("Video Compress.txt", "a")
        f.write(info)
        f.write('\n')
        
        Y_macro_image=Forward_Quantization.macroBlock(self.Y)
        Cb_macro_image=Forward_Quantization.macroBlock(self.Cb)
        Cr_macro_image=Forward_Quantization.macroBlock(self.Cr)
        macroblocks_height,macroblocks_width,_,_=Y_macro_image.shape
        matrix = np.zeros((macroblocks_height,macroblocks_width,3,8,8))
        #print(matrix)
        Y_DCT_image=Forward_Quantization.DCT(Y_macro_image,"Y",level,f,matrix,self.type)
        #print(Y_DCT_image)
        Cb_DCT_image=Forward_Quantization.DCT(Cb_macro_image,"Cb",level,f,Y_DCT_image,self.type)
        Cr_DCT_image=Forward_Quantization.DCT(Cr_macro_image,"Cr",level,f,Cb_DCT_image,self.type)

        
        f.close()
        #print(Cr_DCT_image)
        return Cr_DCT_image
    