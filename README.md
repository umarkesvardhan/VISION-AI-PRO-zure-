
🚀 VISION AI PRO: Intelligent Receipt Processing
VISION AI PRO is an advanced AI-powered web application designed to automate the extraction of financial data from physical receipt images. By leveraging the Donut (Document Understanding Transformer) model, the application transforms unstructured images into a structured dashboard with organized tables and spending visualizations.

✨ Features
AI Data Extraction: Automatically parses Store Names, Itemized Lists (Quantity, Name, Price), and Total Amounts from images.

Multi-Store Compatibility: Features a robust fallback system specifically designed to handle variations in receipt layouts, such as Walmart or Momi & Toy's.

Visual Spending Trends: Integrates Chart.js to provide a chronological line graph of your spending history.

Persistent Archiving: Utilizes an SQLite database to store all historical scans for long-term tracking.

Modern Interface: A responsive, dark-themed UI built with Tailwind CSS for a premium user experience.

🛠️ Tech Stack
Component	Technology
Backend Framework	Python (Flask)
Core AI Model	Donut (naver-clova-ix/donut-base-finetuned-cord-v2)
Database	SQLite3
Frontend Styling	Tailwind CSS
Data Visualization	Chart.js
Processing Engines	PyTorch, Hugging Face Transformers, Pillow (PIL)
⚙️ Installation & Setup
Clone the Repository:

Bash
git clone <your-repository-url>
cd vision-ai-pro
Install Required Libraries:
Ensure you have Python 3.10+ installed.

Bash
pip install flask torch transformers pillow
Initialize and Run:
The database will automatically initialize on the first run.

Bash
python app.py
Access the Application:
Navigate to http://127.0.0.1:5000 in your web browser.

📂 Project Architecture
app.py: The heart of the application handling image processing, AI inference, and database interactions.

templates/index.html: The interactive dashboard displaying scanned history and the spending chart.

static/uploads/: Secure folder for storing uploaded receipt images.

billing_pro.db: Relational database storing structured receipt data (Store Name, Items, Totals, Timestamps).

🧠 Data Processing Workflow
Image Upload: The user submits a bill image through the UI.

AI Inference: The Donut model processes the image to identify document structure and text segments.

Nested JSON Parsing: The system performs a "Multi-Key Search" to find store names and prices within complex nested JSON structures.

Keyword Fallback: If the AI fails to categorize a store, the system scans the raw text for keywords like "Walmart" or "Momi" to manually assign a brand.

Dynamic Rendering: Data is saved to SQLite and rendered onto the dashboard via Jinja2 templates.

📝 Important Performance Notes
Model Size: On the first execution, the application will download approximately 1GB of model weights.

Hardware Acceleration: The app automatically detects and utilizes NVIDIA GPUs (CUDA) for significantly faster processing.

Image Quality: For best results, ensure receipt images are flat, well-lit, and the text is not blurry.