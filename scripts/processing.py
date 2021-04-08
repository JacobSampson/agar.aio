import numpy as np
import math

def process_inputs(player, enemies, food, m):
    SPLIT = 0.33
    features = np.zeros(m)

    slots_available = m - 1
    slots_enemies = round((slots_available * SPLIT) / 3)
    slots_food = round((slots_available - (slots_enemies * 3)) / 2)

    # Player
    index = 0
    [x, y, radius] = player if (not player is None) else [0, 0, 0]
    features[index] = radius

    distance_to_origin = lambda coords: (coords[0] ** 2) + (coords[1] ** 2)

    if (np.amin(np.shape(food)) == 0):
        food = np.array([])
    else:
        food = food[np.argsort(np.apply_along_axis(distance_to_origin, 1, food))]

    if (np.amin(np.shape(enemies)) == 0):
        enemies = np.array([])
    else:
        enemies = enemies[np.argsort(np.apply_along_axis(distance_to_origin, 1, enemies))]

    index = 1
    # Enemies
    for (x, y, radius) in enemies[0:slots_enemies]:
        features[index] = x
        features[index + 1] = y
        features[index + 2] = radius
        index += 3

    index = (slots_enemies * 3)
    # Food
    for (x, y, radius) in food[0:slots_food]:
        features[index] = x
        features[index + 1] = y
        index += 2

    return features
