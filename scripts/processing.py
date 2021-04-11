import numpy as np
import math

def process_inputs(player, enemies, food, m, split):
    features = np.zeros(m)

    slots_available = m - 1
    slots_enemies = round((slots_available * split) / 3)
    slots_food = round((slots_available - (slots_enemies * 3)) / 2)

    # Player
    index = 0
    [_, _, radius] = player if (not player is None) else [0, 0, 0]
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

def reduce_state(state, m, split):
    # Extract player radius
    player_radius = state[0]

    slots_available = m - 1
    slots_enemies = round((slots_available * split) / 3)

    food_index = (slots_enemies * 3)

    enemies = state[1:food_index]
    food = state[food_index:]

    # Extract food and enemies from state array
    parsed_enemies = []
    for i in range(0, len(enemies) - 2, 3):
        parsed_enemies.append([enemies[i], enemies[i + 1], enemies[i + 2]])
    parsed_food = []
    for i in range(0, len(food) - 1, 2):
        parsed_food.append([food[i], food[i + 1]])

    return [player_radius, parsed_enemies, parsed_food]
