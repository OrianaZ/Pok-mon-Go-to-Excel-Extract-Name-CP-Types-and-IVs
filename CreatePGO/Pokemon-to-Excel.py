import cv2
import pytesseract
import pandas as pd
import numpy as np
import os
import re
import math
import difflib
from fuzzywuzzy import process

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image, roi):
    x, y, w, h = roi
    cropped = image[y:y+h, x:x+w]
    text = pytesseract.image_to_string(cropped, config="--psm 7").strip()
    text = re.sub(r'[^A-Za-z/]', '', text)
    return text

def get_valid_roi_set(image, roi_sets):
    for roi_set in roi_sets:
        if not is_bar_white(image, roi_set["attack_bar"]):
            return roi_set
    
    print("Defaulting to the third ROI set.")
    return roi_sets[2]

def load_pokemon_names_from_csv(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')  # Try default encoding
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')  # Fallback encoding
    pokemon_names = set()
    
    for _, row in df.iterrows():
        pokemon_names.add(row['Name'].strip())
        
    return list(pokemon_names)

def get_closest_pokemon_name(extracted_text, pokemon_names):
    result = process.extractOne(extracted_text, pokemon_names, score_cutoff=80)
    
    if result:
        closest_match = result[0]
    else:
        closest_match = extracted_text
    
    return closest_match


def extract_pokemon_name(image, roi, pokemon_names):
    x, y, w, h = roi
    cropped = image[y:y+h, x:x+w]
    
    extracted_text = pytesseract.image_to_string(cropped, config="--psm 7").strip()
    cleaned_text = re.sub(r'[^A-Za-z/]', '', extracted_text)
    closest_match = get_closest_pokemon_name(cleaned_text, pokemon_names)
    
    return closest_match
  
MIN_CP = 11
MAX_CP = 3826

def preprocess_image(image, roi, padding=5):
    x, y, w, h = roi
    padded_roi = image[max(0, y-padding):y+h+padding, max(0, x-padding):x+w+padding]

    gray = cv2.cvtColor(padded_roi, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    blurred = cv2.GaussianBlur(resized, (3, 3), 0)

    return blurred

def validate_and_correct_cp(cp_text):
    cleaned_text = re.sub(r'[^0-9]', '', cp_text)

    if cleaned_text.isdigit():
        cp_value = int(cleaned_text)
        if MIN_CP <= cp_value <= MAX_CP:
            return cp_value

    if len(cleaned_text) in {1, 2}:
        for i in range(1, 10):
            potential_cp = int(f"{i}{cleaned_text}")
            if MIN_CP <= potential_cp <= MAX_CP:
                return potential_cp

    return 0

def segment_and_ocr(image):
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    digit_images = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if 10 < h < 50 and 5 < w < 40:
            digit_images.append((x, binary[y:y+h, x:x+w]))

    digit_images = sorted(digit_images, key=lambda d: d[0])

    digits = []
    for _, digit_roi in digit_images:
        digit_text = pytesseract.image_to_string(
            digit_roi,
            config="--psm 10 -c tessedit_char_whitelist=0123456789"
        ).strip()

        if digit_text.isdigit():
            digits.append(digit_text)

    if digits:
        combined_cp = int("".join(digits))
        if MIN_CP <= combined_cp <= MAX_CP:
            return combined_cp

    return 0

def try_multiple_ocr_configs(image):
    configs = [
        "--psm 6 -c tessedit_char_whitelist=0123456789",
        "--psm 7 -c tessedit_char_whitelist=0123456789"
    ]
    results = []

    for config in configs:
        cp_text = pytesseract.image_to_string(image, config=config).strip()
        cp_value = validate_and_correct_cp(cp_text)
        if cp_value > 0:
            results.append(cp_value)

    return max(results, default=0)

def extract_cp(image, roi):
    processed_image = preprocess_image(image, roi)
    cp_value = try_multiple_ocr_configs(processed_image)

    if cp_value == 0:
        cp_value = segment_and_ocr(processed_image)

    if cp_value == 0:
        thresholded = cv2.adaptiveThreshold(
            processed_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        cp_value = try_multiple_ocr_configs(thresholded)

    return cp_value


def is_bar_white(image, roi, target_color=(255, 253, 255), color_tolerance=2, white_percentage_threshold=0.75):
    x, y, w, h = roi
    cropped_bar = image[y:y+h, x:x+w]
    cropped_bar_rgb = cv2.cvtColor(cropped_bar, cv2.COLOR_BGR2RGB)
    
    target_color = np.array(target_color)
    color_diff = np.abs(cropped_bar_rgb - target_color)
    color_mask = np.all(color_diff <= color_tolerance, axis=-1)
    
    matching_pixels = np.sum(color_mask)
    total_pixels = w * h
    white_percentage = matching_pixels / total_pixels
    
    return white_percentage >= white_percentage_threshold


def calculate_iv(image, bar_roi, rounded_edge_pixels=52, color_tolerance=45):
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
  
  
TYPE_NAMES = [
    "Bug", "Dark", "Dragon", "Electric", "Fairy", "Fighting", "Fire", "Flying", 
    "Ghost", "Grass", "Ground", "Ice", "Normal", "Poison", "Psychic", "Rock", 
    "Steel", "Water"
]

def closest_match(input_type):
    matches = difflib.get_close_matches(input_type, TYPE_NAMES, n=1, cutoff=0.8)
    return matches[0] if matches else input_type

def extract_types(types):
    if not types:
        return "", ""

    if "/" in types:
        main_type, secondary_type = types.split("/")
        main_type = main_type.strip()
        secondary_type = secondary_type.strip()

        main_type = closest_match(main_type)
        secondary_type = closest_match(secondary_type)
        
        return main_type, secondary_type
    else:
        main_type = types.strip()

        main_type = closest_match(main_type)
        return main_type, ""

def process_pokemon_image(image_path):
    image = cv2.imread(image_path)

    roi_sets = [
        {
            "name": (260, 735, 400, 65),
            "cp": (320, 110, 290, 57),
            "types": (357, 1030, 290, 40),
            "attack_bar": (110, 1524, 295, 26),
            "defense_bar": (110, 1609, 295, 26),
            "hp_bar": (110, 1693, 295, 26),
        },
        {
            "name": (260, 735, 400, 65),
            "cp": (320, 110, 290, 57),
            "types": (357, 1030, 290, 40),
            "attack_bar": (110, 1467, 295, 26),
            "defense_bar": (110, 1552, 295, 26),
            "hp_bar": (110, 1637, 295, 26),
        },
        {
            "name": (260, 735, 400, 65),
            "cp": (320, 110, 290, 57),
            "types": (357, 1030, 290, 40),
            "attack_bar": (110, 1410, 295, 26),
            "defense_bar": (110, 1494, 295, 26),
            "hp_bar": (110, 1579, 295, 26),
        },
    ]
    
    valid_rois = get_valid_roi_set(image, roi_sets)
    if not valid_rois:
        print("No valid ROI set found.")
        return None

    name = extract_pokemon_name(image, valid_rois["name"], pokemon_names)
    cp = extract_cp(image, valid_rois["cp"])
    types = extract_text(image, valid_rois["types"])

    main_type, secondary_type = extract_types(types)

    iv_values = {
        "Attack": calculate_iv(image, valid_rois["attack_bar"], rounded_edge_pixels=52, color_tolerance=45),
        "Defense": calculate_iv(image, valid_rois["defense_bar"], rounded_edge_pixels=52, color_tolerance=45),
        "HP": calculate_iv(image, valid_rois["hp_bar"], rounded_edge_pixels=52, color_tolerance=45)
    }

    return {
        "Name": name,
        "CP": cp,
        "Main Type": main_type,
        "Secondary Type": secondary_type,
        "Attack": iv_values["Attack"],  
        "Defense": iv_values["Defense"],
        "HP": iv_values["HP"]
    }

def process_images_to_excel(image_paths, output_file):
    data = []
    for image_path in image_paths:
        print(f"Processing {image_path}...")
        data.append(process_pokemon_image(image_path))
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")


def process_images_in_folder(folder_path, output_file):
    image_paths = [
        os.path.join(folder_path, f) 
        for f in os.listdir(folder_path) 
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    
    data = []
    for image_path in image_paths:
        print(f"Processing {image_path}...")
        data.append(process_pokemon_image(image_path))
        
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    pokemon_names = load_pokemon_names_from_csv("CreatePGO/pokemon_names.csv")
    folder_path = "CreatePGO/allImages"
    output_file = "CreatePGO/pokemon_data.xlsx"
    process_images_in_folder(folder_path, output_file)
