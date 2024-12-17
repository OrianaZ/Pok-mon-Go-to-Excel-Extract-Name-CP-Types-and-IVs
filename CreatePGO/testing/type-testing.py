import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text(image, roi):
    x, y, w, h = roi
    cropped = image[y:y+h, x:x+w]
    text = pytesseract.image_to_string(cropped, config="--psm 7").strip()
    text = re.sub(r'[^A-Za-z/]', '', text)
    return text
  
  
def extract_types(types):
    if "/" in types:
        main_type, secondary_type = types.split("/")
        return main_type.strip(), secondary_type.strip()
    else:
        return types.strip(), ""

# image = cv2.imread('TestingExampleOutputs/pokemon_Binacle.jpg')
image = cv2.imread('TestingExampleOutputs/pokemon_Grimer.jpg')

rois = {
    "types": (357, 1030, 290, 40),
}

types = extract_text(image, rois["types"])

print(types)
