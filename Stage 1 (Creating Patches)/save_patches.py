import numpy as np
import os
import time
from PIL import Image
from datetime import timedelta
from openslide import open_slide
from openslide.deepzoom import DeepZoomGenerator



class Patch:
    progressBar = ""
    def __init__(self, file_path, db_location):

        # Path to storage directories
        self.file_path = file_path
        self.db_location = db_location
        self.file_dir = os.path.dirname(file_path)
        self.file_name = os.path.basename(file_path)

        print("======================================================")
        print("Image directory:           ", self.file_dir)
        print("Image name:                ", self.file_name)
        print("Data store directory:      ", self.db_location)
        print("======================================================")

    def print_tile_dimensions(self, patch_size=0):
        patch_dim = patch_size
        level_count = 0
        level_tiles = []
        level_dimensions = []

        # Check that either tile or patch size is set correctly.
        if patch_size == 0:
            print("[error]: set patch size.")
        else:
            print("Setting patch size ", patch_dim)

            # Open image and return variables.
            slide = open_slide(self.file_path)
            tiles = DeepZoomGenerator(slide, tile_size=patch_size, overlap=0)

            level_count = tiles.level_count
            level_tiles = tiles.level_tiles
            level_dimensions = tiles.level_dimensions

        print("============Tile Dimensions==========")
        print("Level count:         " + str(level_count))
        print("Level tiles:         " + str(level_tiles))
        print("Level dimensions:    " + str(level_dimensions))
        print("=====================================")

    def sample_and_store_patches(self, patch_size, level, progressBar):
        start_time = start_timer() # Timer Start

        rows_per_txn = 20
        tile_size = patch_size
        slide = open_slide(self.file_path)
        tiles = DeepZoomGenerator(slide, tile_size=tile_size, overlap=0, limit_bounds=True)

        if level >= tiles.level_count:
            print("[error]: requested level does not exist. Number of slide levels: " + str(tiles.level_count))
            return 0
        x_tiles, y_tiles = tiles.level_tiles[level]

        x, y = 0, 0
        count, batch_count = 0, 0
        patches, coords, labels = [], [], []
        while y < y_tiles:
            while x < x_tiles:
                new_tile = np.array(tiles.get_tile(level, (x, y)), dtype=np.uint8)
                # OpenSlide calculates overlap in such a way that sometimes depending on the dimensions, edge
                # patches are smaller than the others. We will ignore such patches.
                if np.shape(new_tile) == (patch_size, patch_size, 3):
                    patches.append(new_tile)
                    coords.append(np.array([x, y]))
                    count += 1
                progressBar.setValue(int((y * x_tiles + x) * 100 / (x_tiles * y_tiles)))
                x += 1

            # To save memory, we will save data into the dbs every rows_per_txn rows. i.e., each transaction will commit
            # rows_per_txn rows of patches. Write after last row regardless. HDF5 does NOT follow
            # this convention due to efficiency.
            if (y % rows_per_txn == 0 and y != 0) or y == y_tiles - 1:
                self.save_to_disk(patches, coords, labels)
            y += 1
            x = 0

        print("============ Patches Dataset Stats ===========")
        print("Total patches sampled:   ", count)
        print("Patches saved to:        ", self.db_location)
        print("==============================================")

        end_timer(start_time) # Timer Ends

    def save_to_disk(self, patches, coords, labels):

        save_labels = len(labels)
        for i, patch in enumerate(patches):
            # Construct the new PNG filename
            patch_file_name = self.file_name[:-4] + "_" + str(coords[i][0]) + "_" + str(coords[i][1]) + "_"

            if save_labels:
                patch_file_name += str(labels[i])

            # Save the image
            Image.fromarray(patch).save(self.db_location + patch_file_name + ".png")

# Timer
def start_timer():
    return time.time()


def end_timer(start_time):
    end_time = time.time()
    print("Time usage: " + str(timedelta(seconds=int(round(end_time - start_time)))))






