import numpy as np
import Inverse_Quantization as InverseQ
import cv2
import unblock
from PIL import Image
import matplotlib.pyplot as plt
import MotionCompensation

def main():
    with open('Video Compress.txt', 'r') as file: 
        first_line = file.readline().split() #read the compressed txt header 
        first_n=len(first_line)
        info=[]
        for i in range(first_n):
            if(i%2 != 0):
                info.append((first_line[i]))
        #initalize the values
        width,height,level,block_size,frames,frameRate=int(info[0]),int(info[1]),float(info[2]),int(info[3]),int(info[4]),float(info[5])
        macroblocks_height = height // block_size
        macroblocks_width = width // block_size
        matrix = np.zeros((macroblocks_height,macroblocks_width,3,block_size,block_size))
        motionVector = np.zeros((macroblocks_height,macroblocks_width,2))
        matrix_row=0
        matrix_col=0
        channel=0

        #initalize the reconstruction of video setup
        output_file = 'reconstructed video 2.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Specify the video codec
        resolution = (height, width)
        video_writer = cv2.VideoWriter(output_file, fourcc, frameRate, resolution)
        
        iterations=0
        lines=1
        for line in file: #read line by line
            lines=lines+1
            values = line.split()
            n=len(values)
            block = np.zeros((8, 8))
            row = 0
            col = 0
            direction = 1
            for i in range(n):
                if(i%2==0):
                    #inverse RLC and Zigzag
                    count=int(values[i+1])
                    value=int(values[i])  
                    while (count > 0):
                        #print(row,col)
                        block[row][col] = (value)
                        if direction == 1:  # Moving upwards
                            if col == 7:
                                row += 1
                                direction = -1
                            elif row == 0:
                                col += 1
                                direction = -1
                            else:
                                row -= 1
                                col += 1
                        else:  # Moving downwards
                            if row == 7:
                                col += 1
                                direction = 1
                            elif col == 0:
                                row += 1
                                direction = 1
                            else:
                                row += 1
                                col -= 1
                        count=count-1
            #print(block)
            #Dequantization and inverse DCT of blocks 
            I_Q=InverseQ.Inverse_Quantization(block,channel,level,iterations)       
            block=I_Q.IQ()
            #print(block)
            #set the block to frames specfic location
            matrix[matrix_row][matrix_col][channel] = block
            matrix_col=matrix_col+1
            if(matrix_col>=macroblocks_width):
                matrix_row=matrix_row+1
                matrix_col=0
            if(matrix_row>=macroblocks_height):
                channel=channel+1
                matrix_row=0
                matrix_col=0
                #iterativly go to the Y,Cb,Cr
                if(channel>=3):
                    channel=0
                    UnblockMatrix=unblock.Unblock(matrix) #remove the 8*8 block and reconstruct the original
                    YCbCr=UnblockMatrix.unblock()
                    YCbCr = np.clip(YCbCr, 0, 255).astype(np.uint8)
                    rgb = cv2.cvtColor(YCbCr, cv2.COLOR_YCrCb2BGR) #convert back to RGB
                    reference_frame=rgb
                    video_writer.write(reference_frame)
                    file.readline()
                       
            
                    
    video_writer.release()
    cv2.destroyAllWindows()
    print("Completed")

if __name__ == "__main__":
    main()