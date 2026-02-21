import os
import csv

# Mee path
image_folder = r"C:\Users\kandr\OneDrive\Desktop\Azure\images"
output_csv = os.path.join(image_folder, "labels.csv")

# Folder lo unna images list tiskuntunnam
images = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]

with open(output_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    # Header
    writer.writerow(['file_name', 'item_name', 'price', 'gst', 'discount'])
    
    for img in images:
        # Initial ga dummy data pedutunnam, meeru Excel lo change cheskovachu
        writer.writerow([img, 'Ice Java Tea', '16000', '1600', '0'])

print(f"Success! {output_csv} create ayyindi. Ippudu training script run cheyandi.")