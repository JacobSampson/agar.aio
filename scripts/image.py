import cv2
import numpy as np

import os

MAX_IMAGE_WIDTH = 1000

def hough_circles(image):
    height, width = image.shape

    # Convert to high-contrast black and white
    image = cv2.medianBlur(image, 3)

    width_resized = min(MAX_IMAGE_WIDTH, width);
    height_resized = round((width_resized / width) * height)
    image = cv2.resize(image, (width_resized, height_resized), 0, 0, cv2.INTER_AREA)

    image = cv2.convertScaleAbs(image, alpha=0.7, beta=100.)

    image = cv2.threshold(image, 245, 255, cv2.THRESH_BINARY)
    image = image[1]

    high_contrast_image = image.copy()

    # Hough Circles: https://docs.opencv.org/3.4/d3/de5/tutorial_js_houghcircles.html
    # https://answers.opencv.org/question/214448/i-try-to-detect-circle-in-real-time-webcam-using-houghcircles-from-opencv-javascript/
    small_circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 5,
                                    param1=100, param2=5,
                                    minRadius=0, maxRadius=5)

    food = [] if ((small_circles is None) or (len(small_circles) == 0)) else list(small_circles[0])

    # Erase food points from image
    for (x, y, radius) in food:
        cv2.circle(image, (round(x), round(y)), round(radius) + 5, (255,255,255), -1)

    large_circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 2, 15,
                                    param1=100, param2=50,
                                    minRadius=10, maxRadius=0)

    enemies = [] if ((large_circles is None) or (len(large_circles) == 0)) else list(large_circles[0])

    min_dist = float('inf')
    min_index = -1

    # Find and extract player
    MIN_PLAYER_DIST = 250
    for i in range(0, len(enemies)):
        x, y, radius = enemies[i]

        dist = ((width_resized / 2) - x) ** 2 + ((height_resized / 2) - y) ** 2
        if (dist < MIN_PLAYER_DIST) and (dist < min_dist):
            min_dist = dist
            min_index = i

    player = None
    if min_index >= 0:
        player = enemies.pop(min_index)
        # save_parsed_circles(high_contrast_image, player, enemies, food)

    transform_origin = lambda x, y, radius: (x - width_resized, y - height_resized, radius)

    # Transform coordinates to center origin
    map(transform_origin, enemies)
    map(transform_origin, food)

    return player, enemies, food

def save_parsed_circles(image, player, enemies, food):
    cv2.imwrite('images/bw.png', image)
    colored_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    x, y, radius = player
    cv2.circle(colored_image, (round(x), round(y)), round(radius), (0,255,0), thickness=2)

    for circle in enemies:
        x, y, radius = circle
        cv2.circle(colored_image, (round(x), round(y)), round(radius), (0,0,255), thickness=2)

    for circle in food:
        x, y, radius = circle
        cv2.circle(colored_image, (round(x), round(y)), round(radius), (255,0,0), thickness=1)

    cv2.imwrite('images/bw_circles.png', colored_image)
