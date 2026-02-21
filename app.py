import os
import sqlite3
import torch
from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import json
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Donut Model Loading
processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")
model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def init_db():
    conn = sqlite3.connect('billing_pro.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS scans")
    cursor.execute('''CREATE TABLE IF NOT EXISTS scans 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  filename TEXT, store TEXT, total REAL, 
                  items TEXT, gst REAL, disc REAL, time TEXT)''')
    conn.commit()
    conn.close()

def process_with_donut(img_path):
    image = Image.open(img_path).convert("RGB")
    pixel_values = processor(image, return_tensors="pt").pixel_values
    
    task_prompt = "<s_cord-v2>"
    decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids
    
    outputs = model.generate(
        pixel_values.to(device),
        decoder_input_ids=decoder_input_ids.to(device),
        max_length=model.config.decoder.max_position_embeddings,
        pad_token_id=processor.tokenizer.pad_token_id,
        eos_token_id=processor.tokenizer.eos_token_id,
        use_cache=True,
        return_dict_in_generate=True,
    )

    sequence = processor.batch_decode(outputs.sequences)[0]
    decoded_json = processor.token2json(sequence)
    return decoded_json

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('bill_img')
        if file:
            fname = f"{datetime.now().strftime('%H%M%S')}_{file.filename}"
            path = os.path.join(UPLOAD_FOLDER, fname)
            file.save(path)
            
            raw_data = process_with_donut(path)
            
            # Handling List vs Dict
            if isinstance(raw_data, list) and len(raw_data) > 0:
                data = raw_data[0]
            elif isinstance(raw_data, dict):
                data = raw_data
            else:
                data = {}

            # --- STORE NAME EXTRACTION WITH FALLBACK ---
            store = (data.get("nm") or 
                     data.get("store_nm") or 
                     data.get("brand_nm") or 
                     data.get("header", {}).get("nm") if isinstance(data.get("header"), dict) else None)
            
            raw_str = str(raw_data).lower()
            if not store or store == "None":
                if "walmart" in raw_str:
                    store = "WALMART"
                elif "momi" in raw_str:
                    store = "MOMI & TOY'S"
                else:
                    store = "RETAIL STORE"

            # --- TOTAL EXTRACTION ---
            total_obj = data.get("total", {})
            if isinstance(total_obj, dict):
                total = total_obj.get("total_price") or total_obj.get("cash_total_price") or 0.0
            else:
                total = 0.0
            
            # --- ITEMS PARSING ---
            items_list = []
            menu_items = data.get("menu", [])
            if isinstance(menu_items, list):
                for item in menu_items:
                    if isinstance(item, dict):
                        target = item.get("menu_item", item) if isinstance(item.get("menu_item"), dict) else item
                        name = target.get("nm") or target.get("item_name") or "Item"
                        qty = target.get("cnt") or target.get("quantity") or "1"
                        price = target.get("price") or target.get("item_price") or "0"
                        
                        if isinstance(name, dict): name = "Product"
                        items_list.append(f"{qty}x {name}|{price}")

            items_str = "||".join(items_list) if items_list else "1x No Items Found|0.0"
            
            # Database saving
            conn = sqlite3.connect('billing_pro.db')
            conn.execute("INSERT INTO scans (filename, store, total, items, gst, disc, time) VALUES (?,?,?,?,?,?,?)",
                         (fname, store, total, items_str, 0.0, 0.0, datetime.now().strftime("%H:%M")))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    # Fetch History
    conn = sqlite3.connect('billing_pro.db')
    history = conn.execute("SELECT * FROM scans ORDER BY id DESC").fetchall()
    conn.close()

    chart_labels = [row[7] for row in reversed(history[:10])]
    chart_values = [row[3] for row in reversed(history[:10])]

    return render_template('index.html', history=history, labels=chart_labels, values=chart_values)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)