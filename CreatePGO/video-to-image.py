import cv2
import pytesseract
import os
import re
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_hp(image, roi):
    x, y, w, h = roi
    cropped = image[y:y+h, x:x+w]
    hp_text = pytesseract.image_to_string(cropped, config="--psm 7").strip()

    hp_text = re.sub(r'[^HP]', '', hp_text)

    return hp_text

# Function to process the video and save distinct Pokémon frames
def process_video_and_capture_frames(video_path, output_folder, start_frame=30, skip_frames_initial=1, check_frames_interval=1, roi_hp= (477, 847, 75, 30)):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    
    frame_count = start_frame
    saved_frame_count = 0
    skip_next = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1

        if frame_count % check_frames_interval == 0:
            hp_value = extract_hp(frame, roi_hp)
            
            if hp_value == "HP" or hp_value == "H" or hp_value == "P":
                timestamp = int(time.time() * 1000)
                image_filename = os.path.join(output_folder, f"pokemon_{saved_frame_count+1}.jpg")
                cv2.imwrite(image_filename, frame)
                saved_frame_count += 1
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count + skip_frames_initial)
                frame_count += skip_frames_initial 

    cap.release()
    print(f"Finished processing. Total saved frames: {saved_frame_count}")

if __name__ == "__main__":
    video_path = "CreatePGO/PokemonExampleRecording.mp4"
    output_folder = "CreatePGO/allImages"
    process_video_and_capture_frames(video_path, output_folder, start_frame=30, skip_frames_initial=1, check_frames_interval=1, roi_hp= (477, 847, 75, 30))
