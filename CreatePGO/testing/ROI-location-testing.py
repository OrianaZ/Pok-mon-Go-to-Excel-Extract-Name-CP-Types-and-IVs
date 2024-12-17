import cv2

# image = cv2.imread('TestingExampleOutputs/pokemon_Binacle.jpg')  #1 row
# image = cv2.imread('CreatePGO/allImages/pokemon_1.jpg')  #2 rows
image = cv2.imread('CreatePGO/allImages/pokemon_3.jpg')  #3 rows

# rois = { #1 row
#     "HP": (477, 847, 75, 30),
#     "name": (260, 735, 400, 65),
#     "cp": (320, 110, 290, 57),
#     "types": (357, 1030, 290, 40),
#     "attack_bar": (110, 1524, 295, 26),
#     "defense_bar": (110, 1609, 295, 26),
#     "hp_bar": (110, 1693, 295, 26),
# }

# rois = { #2 Rows
#     "HP": (477, 847, 75, 30),
#     "name": (260, 735, 400, 65),
#     "cp": (320, 110, 290, 57),
#     "types": (357, 1030, 290, 40),
#     "attack_bar": (110, 1467, 295, 26),
#     "defense_bar": (110, 1552, 295, 26),
#     "hp_bar": (110, 1637, 295, 26),
# }

rois = {  #3 rows
    "HP": (477, 847, 75, 30),
    "name": (260, 735, 400, 65),
    "cp": (320, 110, 290, 57),
    "types": (357, 1030, 290, 40),
    "attack_bar": (110, 1410, 295, 26),
    "defense_bar": (110, 1494, 295, 26),
    "hp_bar": (110, 1579, 295, 26),
}


for key, (x, y, w, h) in rois.items():
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle

cv2.imshow('ROIs', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
