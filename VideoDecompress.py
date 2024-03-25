import numpy as np
import Inverse_Quantization as InverseQ
import cv2
import unblock
from PIL import Image
import matplotlib.pyplot as plt
import MotionCompensation

def main():
    with open('Video Compress.txt', 'r') as file:
        first_line = file.readline().split() #Read the header file
        first_n=len(first_line)
        info=[]
        for i in range(first_n):
            if(i%2 != 0):
                info.append((first_line[i]))
        #initialize the values
        height,width,level,block_size,frames,frameRate=int(info[0]),int(info[1]),float(info[2]),int(info[3]),int(info[4]),float(info[5])
        macroblocks_height = height // block_size
        macroblocks_width = width // block_size
        matrix = np.zeros((macroblocks_height,macroblocks_width,3,block_size,block_size))
        motionVector = np.zeros((macroblocks_height,macroblocks_width,2))
        matrix_row=0
        matrix_col=0
        channel=0

        output_file = 'reconstructed video 2.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Specify the video codec
        resolution = (height, width)
        video_writer = cv2.VideoWriter(output_file, fourcc, frameRate, resolution)
        
        iterations=0
        lines=1
        for line in file:
            lines=lines+1
            if(iterations<2): #check forr the residuals and initial frame
                values = line.split()
                n=len(values)
                block = np.zeros((8, 8))
                row = 0
                col = 0
                direction = 1
                for i in range(n): #inverse RLC and inverse zig zag
                    if(i%2==0):
                        count=int(values[i+1])
                        value=int(values[i])  
                        while (count > 0):
                            block[row][col] = (value)
                            if direction == 1:  # going Up
                                if col == 7:
                                    row += 1
                                    direction = -1
                                elif row == 0:
                                    col += 1
                                    direction = -1
                                else:
                                    row -= 1
                                    col += 1
                            else:  # Going Down
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
                I_Q=InverseQ.Inverse_Quantization(block,channel,level,iterations)        #inverse quantization,Inverse DCT
                block=I_Q.IQ()
                matrix[matrix_row][matrix_col][channel] = block
                matrix_col=matrix_col+1
                #print(matrix_row,matrix_col)
                if(matrix_col>=macroblocks_width):
                    matrix_row=matrix_row+1
                    matrix_col=0
                if(matrix_row>=macroblocks_height):
                    channel=channel+1
                    matrix_row=0
                    matrix_col=0
                    if(channel>=3):
                        channel=0
                        UnblockMatrix=unblock.Unblock(matrix)
                        YCbCr=UnblockMatrix.unblock()
                        YCbCr = np.clip(YCbCr, 0, 255).astype(np.uint8)
                        rgb = cv2.cvtColor(YCbCr, cv2.COLOR_YCrCb2BGR) #reconstrruct the RGB format of frame(Residual and ref frame)
                        if(iterations==0): #check for reference frame
                            reference_frame=rgb 
                            video_writer.write(reference_frame)
                            file.readline()
                        elif(iterations>0): #check residual
                            residual=rgb
                            #print("########################")
                        iterations=iterations+1
            elif(iterations==2): #check for MV
                #print(lines,channel)
                values = line.split()
                n=len(values)  
                for i in range(n):
                    if(i%2==0):
                        value1=int(values[i])
                        value2=int(values[i+1]) 
                        #print(value1,value2)
                        motionVector[matrix_row][matrix_col] = [value1,value2] #create a motion vector
                        #print(value1,value2)   
                        matrix_col=matrix_col+1
                        if(matrix_col>=macroblocks_width):
                            matrix_row=matrix_row+1
                            matrix_col=0
                        if(matrix_row>=macroblocks_height):
                            #print(motionVector.shape)
                            #print(n)
                            matrix_row=0
                            matrix_col=0 
                            iterations=1
                            height, width, _ = reference_frame.shape
                            num_blocks_h, num_blocks_w, _ = motionVector.shape
                            predicted_frame = np.zeros((height, width, 3)).astype(np.uint8)
                            #motion compensation to reconstruct the predicted frame
                            for i in range(num_blocks_h):
                                for j in range(num_blocks_w):
                                    motion_vector = motionVector[i, j]
                                    #print(motion_vector)
                                    ref_block_x = j * block_size + int(motion_vector[0])
                                    ref_block_y = i * block_size + int(motion_vector[1])
                                    ref_block = reference_frame[ref_block_y:ref_block_y+block_size, ref_block_x:ref_block_x+block_size, :]
                                    predicted_frame[i * block_size:(i+1) * block_size, j * block_size:(j+1) * block_size, :] = ref_block
                            
                            #reconstuct the Curent frame
                            curr_frame=predicted_frame + residual
                            video_writer.write(curr_frame)
                            file.readline()  
                    
    video_writer.release()
    cv2.destroyAllWindows()
    print("Completed")

if __name__ == "__main__":
    main()