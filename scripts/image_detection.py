import cv2
import numpy as np

# Load the heatmap image
image = cv2.imread('scripts/event-oct-nov.png')

# Convert the image to HSV color space
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the color range for detection (e.g., red)
lower_red = (0, 255, 0)
upper_red = (250, 255, 250)

# Create a binary mask for the specified color range
mask = cv2.inRange(hsv_image, lower_red, upper_red)

# Find contours
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Sort contours by area
sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

# Work with the largest contours as needed

# Visualize the largest contour (for example, drawing a bounding box)
if sorted_contours:
    largest_contour = sorted_contours[0]
    x, y, w, h = cv2.boundingRect(largest_contour)
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Display the result (or save it)
cv2.imshow('Result', image)
cv2.waitKey(0)
cv2.destroyAllWindows()