import numpy as np
import matplotlib.pyplot as plt
import cv2

class MV:
    def __init__(self,prev_frame, curr_frame, block_size, search_range):
        self.prev_frame=prev_frame
        self.curr_frame=curr_frame
        self.block_size=block_size
        self.search_range=search_range

    def SAD(block1, block2):
    #Calculate the sum of absolute differences (SAD)
        return np.sum(np.abs(block1 - block2))

    def motion_vector_search(current_frame, reference_frame, block_size, search_range): #Motion Estimation
        height, width, _ = current_frame.shape
        num_blocks_h = height // block_size
        num_blocks_w = width // block_size
        motion_vectors = np.zeros((num_blocks_h, num_blocks_w, 2), dtype=np.int32)   #initilize the motion vector 

        #current Frame
        for i in range(num_blocks_h):
            for j in range(num_blocks_w):
                block = current_frame[i * block_size:(i+1) * block_size, j * block_size:(j+1) * block_size] #take a block from current frame
                min_distortion = float('inf') #initalize the the value to get minimum SAD value
                best_vector = np.zeros(2, dtype=np.int32)
                #reference Frame
                for m in range(-search_range, search_range+1):
                    for n in range(-search_range, search_range+1):
                        ref_block_x = j * block_size + m #set the refernece frame rows and col 
                        ref_block_y = i * block_size + n
                        #boundary check
                        if ref_block_x >= 0 and ref_block_x + block_size <= width and ref_block_y >= 0 and ref_block_y + block_size <= height:
                            ref_block = reference_frame[ref_block_y:ref_block_y+block_size, ref_block_x:ref_block_x+block_size] #select a block fom referece frame
                            distortion = MV.SAD(block, ref_block) #calcualte SAD
                            if distortion < min_distortion: #check for the minimum SAD
                                min_distortion = distortion
                                best_vector = np.array([m, n])

                motion_vectors[i, j] = best_vector #assign the best MV
        #print(motion_vectors)
        return motion_vectors

    def motion_compensation(reference_frame, motion_vectors, block_size):
        height, width, _ = reference_frame.shape #get the size of ref. frame
        num_blocks_h, num_blocks_w, _ = motion_vectors.shape
        predicted_frame = np.zeros((height, width, 3), dtype=np.uint8) #initalize the predicted frame

        for i in range(num_blocks_h):
            for j in range(num_blocks_w):
                motion_vector = motion_vectors[i, j]
                ref_block_x = j * block_size + motion_vector[0] #set the refernece frame rows and col with motion vector values
                ref_block_y = i * block_size + motion_vector[1]
                #get the ref block, corresponding to the row and col values in ref. frame
                ref_block = reference_frame[ref_block_y:ref_block_y+block_size, ref_block_x:ref_block_x+block_size, :]
                #Assign ref block to the predicated frame
                predicted_frame[i * block_size:(i+1) * block_size, j * block_size:(j+1) * block_size, :] = ref_block

        return predicted_frame

    
    def MV_main(self):
        
        prev_frame=self.prev_frame
        curr_frame=self.curr_frame
        block_size=self.block_size
        search_range=self.search_range
        frame_height, frame_width,_= curr_frame.shape
        num_blocks_h = frame_height // block_size
        num_blocks_w = frame_width // block_size

        motion_vectors = MV.motion_vector_search(curr_frame, prev_frame, block_size, search_range)
        predicted_frame = MV.motion_compensation(prev_frame, motion_vectors, block_size)
        #residual = curr_frame - predicted_frame
        residual = curr_frame - predicted_frame #calculate the residual

        c_frame=predicted_frame+residual
        return predicted_frame,motion_vectors,residual

