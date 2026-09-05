import csv, pickle
import numpy as np
from scipy.spatial import cKDTree

city_data = []
coordinate_data = []

with open('backend/scripts/cities500.txt', 'rt', encoding='utf-8') as f:

    reader = csv.reader(f, delimiter='\t')

    for line in reader:
        current_city = {'name': line[1], 'country_code': line[8]}
        current_coords = (float(line[4]), float(line[5]))

        city_data.append(current_city)
        coordinate_data.append(current_coords)

coord_array = np.array(coordinate_data)
kd_tree = cKDTree(coord_array)

with open('backend/db/world_data.pkl', 'wb') as bin_file:
    pickle.dump((kd_tree, city_data), bin_file)