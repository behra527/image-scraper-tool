from PIL import Image
import os

# Configuration
dataset_folder = "dataset"
makeup_folder = os.path.join(dataset_folder, "makeup_img")
non_makeup_folder = os.path.join(dataset_folder, "withoutMakeup_img")
target_size = (256, 256)
dpi = (96, 96)

def process_images(folder_path, folder_type):
    # Create output subfolder if it doesn't exist
    output_folder = os.path.join(folder_path, "processed")
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all image files
    image_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.jfif', '.bmp')
    files = [f for f in os.listdir(folder_path) 
             if f.lower().endswith(image_extensions)]
    
    # Process images with sequential numbering
    for idx, filename in enumerate(files, start=1):
        input_path = os.path.join(folder_path, filename)
        output_filename = f"img_{idx}.jpg"  # Save all as JPG
        output_path = os.path.join(output_folder, output_filename)
        
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize image
                resized_img = img.resize(target_size, Image.LANCZOS)
                
                # Save as JPEG with sequential name
                resized_img.save(
                    output_path,
                    format='JPEG',
                    dpi=dpi,
                    quality=95
                )
            print(f"Processed: {filename} -> {output_filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
    
    return output_folder

# Process both folders
print("Processing makeup images...")
processed_makeup = process_images(makeup_folder, "makeup")

print("\nProcessing non-makeup images...")
processed_non_makeup = process_images(non_makeup_folder, "non-makeup")

print("\nAll images processed successfully!")
print(f"Makeup images saved in: {processed_makeup}")
print(f"Non-makeup images saved in: {processed_non_makeup}")