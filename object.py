import easyocr
import re
import sqlite3


reader = easyocr.Reader(['en'])

IMAGE_PATH = 'menu3.jpg' 
result = reader.readtext(IMAGE_PATH)


conn = sqlite3.connect('menu.db')
c = conn.cursor()


c.execute('''CREATE TABLE IF NOT EXISTS menu_items
             (item_name TEXT, price TEXT)''')

c.execute("DELETE FROM menu_items")


unique_items = set()
current_item_name = None

for item in result:
    text = item[1].strip()

    rs_price_match = re.search(r'Rs\.\s*(\d+)', text)
    slash_price_match = re.search(r'(\d+)\/\-', text)
    
    if rs_price_match:
        price = rs_price_match.group(1)
        if current_item_name:
            unique_items.add((current_item_name, price))
            c.execute("INSERT INTO menu_items (item_name, price) VALUES (?, ?)", (current_item_name, price))
        current_item_name = None
    elif slash_price_match:
        price = slash_price_match.group(1)
        if current_item_name:
            unique_items.add((current_item_name, price))
            c.execute("INSERT INTO menu_items (item_name, price) VALUES (?, ?)", (current_item_name, price))
        current_item_name = None
    else:
        if not re.match(r'^\(.*\)$', text): 
            current_item_name = text

conn.commit()

c.execute("SELECT * FROM menu_items")
rows = c.fetchall()


for row in rows:
    print(f"Item: {row[0]}, Price: {row[1]}")


conn.close()
