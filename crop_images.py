from PIL import Image
import os

# Define the target aspect ratio
TARGET_ASPECT_RATIO = 4 / 3

# Path to the images directory
images_dir = 'images'

# Function to crop images to the target aspect ratio
def crop_image_to_aspect_ratio(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        current_aspect_ratio = width / height

        if current_aspect_ratio > TARGET_ASPECT_RATIO:
            # Crop width
            new_width = int(height * TARGET_ASPECT_RATIO)
            left = (width - new_width) / 2
            top = 0
            right = left + new_width
            bottom = height
        else:
            # Crop height
            new_height = int(width / TARGET_ASPECT_RATIO)
            left = 0
            top = (height - new_height) / 2
            right = width
            bottom = top + new_height

        # Crop and save the image
        img_cropped = img.crop((left, top, right, bottom))
        img_cropped.save(image_path)

# Iterate through all images in the directory and crop them
for filename in os.listdir(images_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):  # Add other formats if needed
        crop_image_to_aspect_ratio(os.path.join(images_dir, filename))

print("All images have been cropped to the target aspect ratio.")
