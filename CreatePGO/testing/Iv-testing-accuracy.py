import cv2
import numpy as np
import math

def calculate_iv(bar_roi, rounded_edge_pixels=52, color_tolerance=45):
    x, y, w, h = bar_roi
    cropped_bar = image[y:y+h, x:x+w]

    orange_rgb = np.array([231, 145, 32])
    pink_rgb = np.array([218, 117, 123])

    cropped_bar_rgb = cv2.cvtColor(cropped_bar, cv2.COLOR_BGR2RGB)

    orange_mask = np.all(np.abs(cropped_bar_rgb - orange_rgb) < color_tolerance, axis=-1)
    pink_mask = np.all(np.abs(cropped_bar_rgb - pink_rgb) < color_tolerance, axis=-1)
    
    orange_pixels = np.sum(orange_mask)
    pink_pixels = np.sum(pink_mask)

    effective_width = w - 2 * rounded_edge_pixels

    if orange_pixels == 0 and pink_pixels>1:
        iv = 15
    else:
        total_pixels = effective_width * h
        orange_percentage = orange_pixels / total_pixels
        rounded_percentage = math.ceil(orange_percentage * 15) / 15
        iv = int(rounded_percentage * 15)
        
    return iv

# image = cv2.imread('TestingExampleOutputs/pokemon_Binacle.jpg')  #1 row
# image = cv2.imread('CreatePGO/allImages/pokemon_1.jpg')  #2 rows
image = cv2.imread('CreatePGO/allImages/pokemon_3.jpg')  #3 rows


# rois = { #1 rows
#     "attack_bar": (110, 1524, 295, 26),
#     "defense_bar": (110, 1609, 295, 26),
#     "hp_bar": (110, 1693, 295, 26),
# }

# rois = { #2 rows
#     "attack_bar": (110, 1467, 295, 26),
#     "defense_bar": (110, 1552, 295, 26),
#     "hp_bar": (110, 1637, 295, 26),
# }

rois = { #3 rows
    "attack_bar": (110, 1410, 295, 26),
    "defense_bar": (110, 1494, 295, 26),
    "hp_bar": (110, 1579, 295, 26),
}

iv_values = {}
for bar_name, bar_roi in rois.items():
    iv = calculate_iv(bar_roi, rounded_edge_pixels=52, color_tolerance=45)
    iv_values[bar_name] = iv

print(iv_values)
