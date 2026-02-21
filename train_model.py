import os
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image

# 1. Dataset Path Setup
DATASET_PATH = r"C:\Users\kandr\OneDrive\Desktop\Azure\images"
LABELS_FILE = os.path.join(DATASET_PATH, "labels.csv")

class BillDataset(Dataset):
    def __init__(self, csv_file, img_dir, transform=None):
        # Dataset ni load chestunnam
        self.annotations = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, index):
        img_id = self.annotations.iloc[index, 0]
        img_path = os.path.join(self.img_dir, img_id)
        image = Image.open(img_path).convert("RGB")
        
        # Price ni target label ga tiskuntunnam (Example)
        price_label = torch.tensor(float(self.annotations.iloc[index, 2]))

        if self.transform:
            image = self.transform(image)

        return image, price_label

# 2. Transformations (Image size ni fix chestundi)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# 3. Model Training Logic
def train():
    if not os.path.exists(LABELS_FILE):
        print(f"Error: {LABELS_FILE} kanipinchadam ledhu. Please create it first.")
        return

    dataset = BillDataset(csv_file=LABELS_FILE, img_dir=DATASET_PATH, transform=transform)
    loader = DataLoader(dataset, batch_size=4, shuffle=True)

    # Pre-trained ResNet model ni vadutunnam (Transfer Learning)
    model = models.resnet18(pretrained=True)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 1) # Price prediction kosam output 1

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    print("Training Start avthundi...")
    model.train()
    for epoch in range(10): # 10 sarlu data ni loop chestundi
        total_loss = 0
        for batch_idx, (data, targets) in enumerate(loader):
            optimizer.zero_grad()
            outputs = model(data)
            loss = criterion(outputs, targets.view(-1, 1).float())
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        print(f"Epoch [{epoch+1}/10], Loss: {total_loss/len(loader):.4f}")

    # Model save cheyadam
    torch.save(model.state_dict(), "bill_model.pth")
    print("Training Complete! Model saved as bill_model.pth")

if __name__ == "__main__":
    train()