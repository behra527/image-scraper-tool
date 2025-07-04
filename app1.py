from PIL import Image
import os
import glob

# Configuration
input_folder = "combine_dataset"  # Folder containing your combined images
output_makeup = "makeup_img"      # Output folder for makeup images
output_non_makeup = "withoutMakeup_img"  # Output folder for non-makeup images

# Create output directories if they don't exist
os.makedirs(output_makeup, exist_ok=True)
os.makedirs(output_non_makeup, exist_ok=True)

# Process all images in input folder
for img_path in glob.glob(os.path.join(input_folder, "*.*")):
    try:
        # Open the combined image
        with Image.open(img_path) as img:
            width, height = img.size
            
            # Split image into left (non-makeup) and right (makeup) halves
            non_makeup = img.crop((0, 0, width//2, height))
            makeup = img.crop((width//2, 0, width, height))
            
            # Get filename without extension
            filename = os.path.basename(img_path)
            name, ext = os.path.splitext(filename)
            
            # Save images
            non_makeup.save(os.path.join(output_non_makeup, f"{name}_before{ext}"))
            makeup.save(os.path.join(output_makeup, f"{name}_after{ext}"))
            
            print(f"Processed: {filename}")

    except Exception as e:
        print(f"Error processing {img_path}: {str(e)}")

print("\nSeparation complete!")
print(f"Non-makeup images saved to: {output_non_makeup}")
print(f"Makeup images saved to: {output_makeup}")