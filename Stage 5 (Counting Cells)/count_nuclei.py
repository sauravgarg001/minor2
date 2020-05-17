import cv2
import numpy as np
import math
import os
import csv

data_folder = 'data'
dir_path = os.path.join(os.getcwd(), data_folder)
file_dir_path_list = os.listdir(dir_path)

# field names
fields = ['Image', 'Number of cells']

# data rows of csv file
rows = []

# name of csv file
filename = "records.csv"


for index, file_name in enumerate(file_dir_path_list):
    print(str(index + 1), ' File: ', file_name, 'processing...')
    file_dir_path = os.path.join(dir_path, file_name)

    image = cv2.imread(file_dir_path+"/mask.png")
    original = image.copy()
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


    hsv_lower = np.array([0,0,0])
    hsv_upper = np.array([255,255,255])
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    close = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)

    cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    minimum_area = 100
    average_cell_area = 650
    connected_cell_area = 1000
    cells = 0
    for c in cnts:
        area = cv2.contourArea(c)
        if area > minimum_area:
            cv2.drawContours(original, [c], -1, (36,255,12), 2)
            if area > connected_cell_area:
                cells += math.ceil(area / average_cell_area)
            else:
                cells += 1
    print('Cells: {}'.format(cells))

    row = [file_name, cells]
    rows.append(row)


# writing to csv file
with open(filename, 'w') as csvfile:
    # creating a csv writer object
    csvwriter = csv.writer(csvfile)

    # writing the fields
    csvwriter.writerow(fields)

    # writing the data rows
    csvwriter.writerows(rows)