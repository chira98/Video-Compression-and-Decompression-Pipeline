'''
1.In the "main.py" file, it contains both Stage 2 and Stage 3 functionalities.
2.To use Stage 2, ensure that you select only the intra coding option when Command prompt message dispalys, and for the decompression of intra coding, use the "VideoDecompress - Intra.py" file.
3.When using Stage 3, use the "VideoDecompress.py" file for the decompression of inter and intra coding compression.
4.Also, make sure that the "MotionCompensation.py" file is present in the folder before running the inter coding work.
'''

import numpy as np
import Ycbcr as conv
import Forward_Quantization as FQ
import cv2
import unblock
import MotionCompensation
import matplotlib.pyplot as plt
import sys
import VideoDecompress
import os

#np.set_printoptions(threshold=sys.maxsize)
def main():
    video = cv2.VideoCapture('Video1.mp4')  #read the video
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) #take the number of Frames
    fps = video.get(cv2.CAP_PROP_FPS) #Take FPS
    #print(total_frames,fps)
    open('Video Compress.txt', 'w').close() #clear a file if there is a alredy written text file

    #Ask whether user need to compress the video for desired bit rate(using users enumber)
    Y_N = (input("Would you like to determine the compression ratio corresponding to your E number[Y/N]? "))
    if(Y_N=='Y'):
        #get the e number
        e_no = int(input("Please enter your E-Number: "))
        #bitrate=e_no+30000
        #bitrate=e_no+6000
        bitrate=e_no+3000
        min_qp,max_qp=1,30 #add a range of 1 to 30 since over 30 is poor quality
        stepSize=1 #this is the step size which used for optimization
        print("1.Inter Coding \n2.Intra Coding ")  #ask whether need to do the compression using Intra or inter
        Intae = int(input("Enter a value: "))
        #initalize the Quantization parameter and Bitrate
        optimal_qp=None
        optimal_bitrate=None
        while min_qp <= max_qp:
            video = cv2.VideoCapture('Video1.mp4')
            open('Video Compress.txt', 'w').close()
            current_qp = (min_qp + max_qp) // 2 #Calculate the current QP by getting the center value
            #print(current_qp)
            count=0
            
            #inter COding
            if(Intae==1): 
                #while True:
                for i in range(10): #since computation take more time use number of iterartion=10
                    ret, frame = video.read()
                    
                    #check are there are any more frames to go
                    if not ret:
                        break

                    levels=current_qp

                    if(count==0): #count=0 means initial frame(frame number 1)
                        #start the compression Methods
                        ycbcr=conv.YCbCr(frame)
                        Y,Cb,Cr=ycbcr.convert() #convert to Y,Cb,Cr 
                        fq = FQ.Forward_Quantization(Y,Cb,Cr,levels,'V',total_frames,fps) #Quantization/DCT transform/RLC applied here 'V'-Qunatization matrix
                        #take the reconstruction of initial frame to use it as fedback to use in Motion compensation
                        IDCT_Frame=fq.Forward_Quantization() 
                        UnblockMatrix=unblock.Unblock(IDCT_Frame)
                        YCbCr=UnblockMatrix.unblock()

                        YCbCr = np.clip(YCbCr, 0, 255).astype(np.uint8)
                        rgb = cv2.cvtColor(YCbCr, cv2.COLOR_YCrCb2BGR) #convert backt RGB Frame
                        Pevious_Frame=rgb #set the reconstructed frame
                        
                    
                    else:
                        #apply this to all the other frames 
                        MV=MotionCompensation.MV(Pevious_Frame,frame,8,16) #Calculate the motion estimation and residuals 8=block size, 16=search area size
                        predicted_frame,motion_vectors,residual=MV.MV_main()
                        #apply compression to residual
                        ycbcr=conv.YCbCr(residual)
                        Y,Cb,Cr=ycbcr.convert()
                        fq = FQ.Forward_Quantization(Y,Cb,Cr,levels,'Y',total_frames,fps) #Y-use pre defined Qunatization value
                        IDCT_Frame=fq.Forward_Quantization()
                        height,width,no=motion_vectors.shape
                        #Write the Motion vector on the Text file
                        f = open("Video Compress.txt", "a")
                        motion=''
                        c=0
                        for i in range(height):
                            for j in range(width):
                                for k in range(no):
                                    motion=motion+str(motion_vectors[i][j][k])+" "
                            f.write(motion)
                            c=c+1
                            
                            motion=''
                            f.write('\n')
                        f.close()
                    count=count+1
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            else: #Intra coding
                levels = current_qp
                count=0
                #while True:
                for i in range(10): #since computation take more time use number of iterartion=10
                    #print(count)
                    ret, frame = video.read()
                    
                    if not ret:
                        break
                    #Do the compression
                    ycbcr=conv.YCbCr(frame)
                    Y,Cb,Cr=ycbcr.convert()
                    fq = FQ.Forward_Quantization(Y,Cb,Cr,levels,'V',total_frames,fps)
                    IDCT_Frame=fq.Forward_Quantization()

            video.release()
            cv2.destroyAllWindows()
            #Optimization method used to calulate best bit rate
            file_size = os.path.getsize('Video Compress.txt') #get the file size
            average_bitrate=file_size/1024
            print(current_qp,average_bitrate)
            #Optimization Concept
            if average_bitrate <= bitrate:
                optimal_qp = current_qp
                optimal_bitrate = average_bitrate
                max_qp = current_qp - stepSize
                
            else:
                min_qp = current_qp + stepSize
                

        print("Optimal QP:", optimal_qp)
        print("Achieved Bitrate:", optimal_bitrate)
        print("Compression Completed!")
    #basic Compression of Intra & Inter
    else:
        print("1.Inter Coding \n2.Intra Coding ") 
        Intae = int(input("Enter a value: ")) #check for Inter/Intra
        if(Intae==1): #inter
            #apply qunatization based on HIGH/MEDIUM/LOW (take the direct input here)
            print("Please enter the desired compression Quality,")
            print("1.High \n2.Medium \n3.Low ") 
            levels = int(input("Enter a value: "))

            ############################################
            output_file = 'reconstructed video in compress.mp4'
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Specify the video codec
            resolution = (720, 1080)
            video_writer = cv2.VideoWriter(output_file, fourcc, fps, resolution)
            ##############################################

            count=0
            #while True:
            for i in range(10):
                ret, frame = video.read()

                if not ret:
                    break
                
                if(count==0): #initial Frame
                    #do the compression
                    ycbcr=conv.YCbCr(frame)
                    Y,Cb,Cr=ycbcr.convert()
                    fq = FQ.Forward_Quantization(Y,Cb,Cr,levels,'V',total_frames,fps)
                    IDCT_Frame=fq.Forward_Quantization() #reconstruct the 1 frame to use as feedback

                    UnblockMatrix=unblock.Unblock(IDCT_Frame)
                    YCbCr=UnblockMatrix.unblock()

                    YCbCr = np.clip(YCbCr, 0, 255).astype(np.uint8)
                    rgb = cv2.cvtColor(YCbCr, cv2.COLOR_YCrCb2BGR)
                    Pevious_Frame=rgb
                    cv2.imwrite("Reconstructed 1 Frame.jpg", rgb)
                    video_writer.write(rgb)

                else: #all other frames
                    #do the compression and use reconstructed 1st frame
                    MV=MotionCompensation.MV(Pevious_Frame,frame,8,16)
                    predicted_frame,motion_vectors,residual=MV.MV_main()
                    video_writer.write(predicted_frame+residual)

                    ycbcr=conv.YCbCr(residual)
                    Y,Cb,Cr=ycbcr.convert()
                    fq = FQ.Forward_Quantization(Y,Cb,Cr,levels,'Y',total_frames,fps) #'Y' use quantization value
                    IDCT_Frame=fq.Forward_Quantization()
                    height,width,no=motion_vectors.shape
                    f = open("Video Compress.txt", "a")
                    motion=''
                    c=0
                    for i in range(height):
                        for j in range(width):
                            for k in range(no):
                                motion=motion+str(motion_vectors[i][j][k])+" "
                        f.write(motion)
                        c=c+1
                        
                        motion=''
                        f.write('\n')
                    f.close()
                count=count+1
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
            print("Compression Completed!")
            video.release()
            video_writer.release()
            cv2.destroyAllWindows()
        
        else: #intra coding
            print("Please enter the desired compression Quality,")
            print("1.High \n2.Medium \n3.Low ") 
            levels = int(input("Enter a value: "))
            count=0
            while True:
            #for i in range(10):
                ret, frame = video.read()
                
                if not ret:
                    break
                
                #compression
                ycbcr=conv.YCbCr(frame)
                Y,Cb,Cr=ycbcr.convert()
                fq = FQ.Forward_Quantization(Y,Cb,Cr,levels,'V',total_frames,fps)
                IDCT_Frame=fq.Forward_Quantization()
            print("Compression Completed!")

if __name__ == "__main__":
    main()