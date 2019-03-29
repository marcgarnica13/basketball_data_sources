# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 13:12:51 2018

@author: SESA474580
"""

import numpy as np # '1.12.1'
import matplotlib.pyplot as plt # '2.0.1'
import matplotlib.gridspec as gridspec
import random
from copy import deepcopy


class GenImage():
    def __init__(self, x_px=48, y_px=48, line_wd=2.0):
        self.x_px = x_px
        self.y_px = y_px
        self.line_wd = line_wd

    ### Generate dynacard image based on stroke position and load
    def print_card(self, stroke_position, stroke_load, Print=True, save_in=None, PPI=72):
        '''
        stroke_position: numpy array of 128 values
        stroke_load: numpy array of 128 values
        Print: boolean, print image in console
        save_in: if path is given image is saved in that directory
        x_px: image width in pixels
        y_px: image length in pixels
        my_dpi: monitor resolution (used to transform inches into pixels, plt default 72)
        line_wd: dyna card line width
        '''
        # Copy the first data at the end just to have matplotlib closing the curve
        position = np.append(stroke_position, stroke_position[0])
        load = np.append(stroke_load, stroke_load[0])     
        # create plot
        plt.ioff()
        fig, ax = plt.subplots(figsize=((self.x_px/PPI), (self.y_px/PPI)), dpi=PPI)    
        ax.plot(position, load, '-', color='white', linewidth=self.line_wd)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.patch.set_facecolor('black')
        fig.patch.set_facecolor('black')
        # Print image if needed (default = False)
        if Print:
            plt.show()
        # save if path is given    
        if save_in is not None:
            plt.savefig(save_in, bbox_inches='tight', facecolor='black')        
        # plot to array
        fig.canvas.draw()
        img = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        plt.close()
        # gray scale
        r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]
        gray_img = (0.2989 * r + 0.5870 * g + 0.1140 * b)/255
        return(gray_img) 
            
  
    # given a card dict, return the generated image in a pixel numpy matrix structure
    def gen_image(self, cards):
        cards_images = deepcopy(cards)
        for i in range(len(cards_images)):
            cards_images[i]['plot'] = self.print_card(stroke_position = cards_images[i]['data']['position'],
                                               stroke_load = cards_images[i]['data']['force'],
                                               Print=False)
        print(len(cards_images) ,"images generated and save in card['plot']")
        return(cards_images)
        
    # given a card dict, train data and labels for image recognition training    
    def training_data(self, cards):
        X_data = np.array([card['plot'] for card in cards])
        Y_data = np.array([card['label'][0] for card in cards])
        id_data = np.array([''.join(e) for e in [card['source'] for card in cards]])
        return(X_data, Y_data, id_data,)
    
    
    # print random images from a cards list
    def print_random_images(self, cards, sample_size = 20, print_file=True):
        count=0
        fig = plt.figure(figsize=(7, 6))
        grid = gridspec.GridSpec(int(sample_size/5), 5, wspace=0.0, hspace=0)
        # for i in range(int(sample_size/5)):    
        for x in range(sample_size):
            idx = random.randint(0, (len(cards)-1))
            img = cards[idx]['plot']
            ax = plt.Subplot(fig, grid[count])
            ax.set_xticks([])
            ax.set_yticks([])
            ax.imshow(img, cmap='gray')
            fig.add_subplot(ax)
            if (print_file):
                print(x+1, cards[idx]['source'])
            count += 1
        plt.show()
        
    # print images from a cards list
    def print_images(self, cards, images_per_line=5):
        
        # should be +1....
        max_rows = int(len(cards)/images_per_line) + 2
        max_cols = images_per_line
        
        fig, axes = plt.subplots(nrows=max_rows, ncols=max_cols, figsize=(7,6))
        
        # remove axis from each subplot
        for i in range(0, max_cols*max_rows):
            row = i // max_cols
            col = i % max_cols
            axes[row, col].axis("off")
            axes[row, col].get_xaxis().set_ticks([])  
            axes[row, col].get_xaxis().set_visible(False)
        plt.axis('off')
        
        # iterate on each card
        for idx, card in enumerate(cards):
            row = idx // max_cols
            col = idx % max_cols    
            img = axes[row, col].imshow(card['plot'], cmap="gray", aspect="auto")
            img.set_cmap('hot')
        plt.subplots_adjust(wspace=0.0, hspace=0.0)
        
        # display
        plt.show()

    