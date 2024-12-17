# Pokémon Go to Excel: Name, CP, Types, IV's

## Summary
This project automates the extraction and validation of Pokémon details from video footage of scrolling through Pokémon storage. It includes Python scripts to convert MP4 video files into individual image frames, extract key details such as Pokémon name, CP (Combat Power), types, and IV stats using OCR and image processing, and validate the accuracy of extracted data. Testing utilities are provided to verify IV calculations, ROIs, and type recognition. A final validation script ensures that the extracted Pokémon types align with the corresponding Pokémon names, so that the user can manually ensure correctness. The processed data is then compiled into an Excel file for easy analysis.  

## BEFORE USING
### Known Bugs:
This code seems to have some trouble analyzing the specific text, I have done my best to ensure it works well, and checks it against accurate data. However it has most trouble with the CP,
SO please know not all CP's will be accurate.  
Additionally depending on how fast you scroll, iv's could take 'too long' to move up or down so screenshots are not accurate. However if you have mostly 2-3 stars then this is not an issue.  
  
If you know of a way to fix the CP I am all ears, as I tried for a long time to try and perfect but could not.  

### Requirements
#### Python Version
I used `python 3.13.1`, but version `Python 3.10+` should work.  
  
#### Packages
`pip install opencv-python pytesseract pandas numpy fuzzywuzzy`  
  
## How to Use
### Step 1
Take a screen recording of your Pokémon with the IV's up on the screen. Scroll pretty fast.  
Example of what this should look like is under `CreatePGO`  

### Step 2
Look at what the dimensions of your screen recoding are. The ROI locations are dependent on pixels. The examples in this project are `884 x 1920`  
If your dimensions are different resize the example images: at least 1 of each of the versions to be what your dimensions are.  

** *Notice* **   
*There are 3 different 'versions' of images that you get. The description of where the Pokémon were caught ranges from 1-3 lines. this will move the IV location up or down, and therefore the ROI will be different. the other locations will remain the same.*

### Step 3
Under `CreatePGO > testing` run the `ROI-location-testing.py` file on the newly resized images.  
Ensure that the regions are highlighting the exact areas of interest. So name is surrounding name... and so on.  
  
ROI sizing is pixels (starting x, starting y, width, height)  
Please look at the screenshots under `TestingExampleOutputs` for what this should look like.  
Run this on all 3 versions to ensure that the locations are good for all iv's  

** *Note* **  
*There should only be different ROIs on the IV bars, all else should be the same across the three.*

### Step 4  
Paste the ROI regions into there corresponding location in the other files starting with the test files  

Under `CreatePGO > testing`  
`Iv-testing-accuracy.py`  
paste in the three different versions of attack, defense, and HP bars in `lines 37-53`  
  
`type-testing.py`  
paste in the types roi into `line 27`  

### Step 5
Under `CreatePGO > testing` run the `Iv-testing-accuracy.py` file and `type-testing.py` files with the updated ROI locations, and images  

Ensure that the outputs in the console are what you want to see.  
`TestingExampleOutputs` has what an example output should look like for the example images in that folder.  

** *Troubleshooting tips* **  
*Ensure that you have ample room on either side of the types as while it is in the same height it can vary where it is across the screen depending on the frame.*  
  
*the IVs have rounded sides, and use pixel percentage to figure out the number it correlates to. Adjusting the rounded_edge_pixels and color_tolerance on both lines 57 and 5 (ensuring both lines have the same number) will help get this accurate.*
 
### Step 6
Continue making minor adjustments to ROI until desired output is correct.

### Step 7
update ROI location in main python files  
  
Under `CreatePGO`  
`video-to-image.py`  
`lines 19 & 61` roi_hp=*place HP roi here*  
  
`Pokemon-to-Excel.py`  
paste in the three different versions all ROI besides the HP into `lines 229-250`  
on `Lines 61-62` update the Min and Max CP to what your Pokémon CP range is.  

** *Note* **  
*If you changed anything else i.e the color tolerance, or rounded edge pixels update those accordingly in all areas on this file.*

### Step 8
There are example outputs in the allImages folder for what outputs after running the example mp4. if you are done with these remove them from the folder.  
Ensure that the locations of the video, as well as name of the video and the output folder are correctly specified in the last lines of the  `video-to-image.py`  
Do the same with `Pokemon-to-Excel.py` file.  

### Step 9
Run `video-to-image.py`  
Ensure that images are outputting to file  
  
** *Troubleshooting tips* **  
*if no images are outputting try adjusting the HP location, as this is what is validating before an image is saved.*  
  
*if it is skipping first images adjust `start_frame=30` on lines 61 & 19 to be a lower number, ensure both numbers are the same.*  
  - *if it is outputting the first Pokémon too many times increase this number*  

  
*if Pokémon are constantly being saved multiple times throughout adjust either or both of `skip_frames_initial=1`, `check_frames_interval=1`, on lines 61 & 19 ensure both numbers are the same.*  
  - *skip_frames_initial will skip that number of frames after an image is saved, so it will not output the same Pokémon if you are scrolling slow.*  
  - *`check_frames_interval designates what frames are checked so 1 checks every frame, 2 skips a frame etc..*  
  
### Step 10
 Run `Pokemon-to-Excel.py`
    this will overwrite the current example file, but the example file could be deleted first as well.

### Step 11
Copy outputted data file to the ValidatePGO folder.  
Make sure to not manually change any headings or other  
run `Validate-types.py`  
  
This basically just ensures that it correctly pulled the Pokémon name and types. If anything is marked as invalid it is up to you to manually correct.  

### Step 12
Manually adjust file as need with missing data (CPs)  

### Step 13
Enjoy your Pokémon in an excel file.  

## Authors Note:
I have 2550 Pokémon, It took me about 10 minutes of continuous fast scrolling to get through all of my Pokémon. Mine outputted about 100 or so CP 0 Pokémon, and a few duplicates most notable on the first and last Pokémon, initially deleting the extra images and using excel built in feature to remove duplicates after getting the excel document, I got this pretty accurate to what I have. I do note it is not 100% but provides me a good starting point for all my Pokémon instead of manually entering all of them  
  
If you see any errors, or improvements let me know.
