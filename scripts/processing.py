import numpy as np

def process_inputs(player, enemies, food, m):
    SPLIT = 0.25

    slots_available = m - 1
    slots_enemies = round(slots_available * SPLIT)
    slots_food = slots_available - slots_enemies

    features = []

    # Player
    x, y, radius = player if len(player) == 3 else 0, 0, 0
    features.append([1, 0, 0, x, y, radius])

    distance_to_player = lambda item: (x - item[0]) ** 2 + (y - item[1]) ** 2

    food = food[np.argsort(distance_to_player(food))]
    enemies = enemies[np.argsort(distance_to_player(enemies))]

    # Enemies
    for (x, y, radius) in enemies[0:slots_enemies]:
        features.append([0, 1, 0, x, y, radius])
    for _ in range(slots_enemies - len(enemies)):
        features.append([0, 1, 0, 0, 0, 0])

    # Food
    for (x, y, radius) in food[0:slots_food]:
        features.append([0, 0, 1, x, y, radius])
    for _ in range(slots_food - len(food)):
        features.append([0, 0, 1, 0, 0, 0])

    return features
