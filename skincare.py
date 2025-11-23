import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------- Database Setup ---------------- #
# This version avoids pandas to reduce dependency issues.
DB_FILE = 'skincare.db'

try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
except Exception as e:
    tk.messagebox.showerror("Database Error", f"Could not connect to database: {e}")
    raise

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    skin_type TEXT,
    concern TEXT,
    price INTEGER,
    ingredients TEXT
)
''')
conn.commit()

# Sample data insertion using INSERT OR IGNORE to avoid primary key conflicts
sample = [
    (1, 'Niacinamide Serum', 'Serum', 'Oily, Combination', 'Acne, Pores', 450, 'Niacinamide, Zinc'),
    (2, 'Hyaluronic Acid Serum', 'Serum', 'Dry, Sensitive', 'Dryness', 550, 'Hyaluronic Acid'),
    (3, 'AHA BHA Cleanser', 'Cleanser', 'Oily', 'Acne', 399, 'Salicylic Acid'),
    (4, 'Ceramide Moisturizer', 'Moisturizer', 'Dry, Sensitive', 'Barrier Repair', 649, 'Ceramides'),
    (5, 'Vitamin C Serum', 'Serum', 'All', 'Pigmentation', 700, 'Vitamin C'),
    (6, 'Watermelon Gel Moisturizer', 'Moisturizer', 'Oily, Combination', 'Hydration', 599, 'Watermelon Extract')
]

for row in sample:
    try:
        cursor.execute("INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?, ?, ?, ?)", row)
    except Exception:
        pass
conn.commit()

# ---------------- Product dictionary (advanced) ---------------- #
products = {
    "cleansers": [
        {"name": "Cetaphil Gentle Skin Cleanser", "skin": ["dry", "sensitive"]},
        {"name": "CeraVe Hydrating Cleanser", "skin": ["dry", "normal"]},
        {"name": "Neutrogena Hydro Boost Cleanser", "skin": ["oily", "normal"]},
        {"name": "Simple Refreshing Face Wash", "skin": ["oily", "sensitive"]},
        {"name": "The Face Shop Rice Water Bright Cleanser", "skin": ["normal", "dry"]}
    ],
    "serums": [
        {"name": "The Ordinary Niacinamide 10% + Zinc 1%", "skin": ["oily", "acne"]},
        {"name": "Minimalist Vitamin C 10%", "skin": ["dull", "pigmentation"]},
        {"name": "Deconstruct Brightening Serum", "skin": ["pigmentation"]},
        {"name": "Plum 2% Alpha Arbutin Serum", "skin": ["pigmentation"]},
        {"name": "L’Oreal Revitalift Hyaluronic Acid Serum", "skin": ["dry", "normal"]}
    ],
    "moisturizers": [
        {"name": "CeraVe Moisturizing Cream", "skin": ["dry", "sensitive"]},
        {"name": "Neutrogena Hydro Boost Water Gel", "skin": ["oily", "normal"]},
        {"name": "Ponds Super Light Gel", "skin": ["oily", "normal"]},
        {"name": "Cetaphil Moisturizing Lotion", "skin": ["dry"]},
        {"name": "Minimalist Sepicalm 03% Moisturizer", "skin": ["sensitive", "acne"]}
    ],
    "sunscreens": [
        {"name": "La Shield SPF 50", "skin": ["oily", "normal"]},
        {"name": "Re’equil Oxybenzone & OMC Free Sunscreen", "skin": ["sensitive", "normal"]},
        {"name": "Dermaco Ultra Matte Sunscreen", "skin": ["oily"]},
        {"name": "Aqualogica Radiance+ Dewy Sunscreen", "skin": ["dry"]},
        {"name": "Dr. Sheth’s Ceramide & Vitamin C Sunscreen", "skin": ["sensitive", "dry"]}
    ],
    "acne_treatments": [
        {"name": "Benzoyl Peroxide 2.5% Gel", "skin": ["acne"]},
        {"name": "Salicylic Acid 2% Solution", "skin": ["acne", "oily"]},
        {"name": "Cosrx Pimple Patches", "skin": ["acne"]},
        {"name": "Adapalene Gel (Differin)", "skin": ["acne"]},
        {"name": "Deconstruct Breakout Control Serum", "skin": ["acne"]}
    ],
    "exfoliants": [
        {"name": "The Ordinary AHA + BHA Peeling Solution", "skin": ["dull", "textured"]},
        {"name": "Minimalist Lactic Acid 10%", "skin": ["dry", "dull"]},
        {"name": "Cosrx BHA Blackhead Power Liquid", "skin": ["oily", "acne"]},
        {"name": "Paula’s Choice 2% BHA Liquid", "skin": ["oily", "blackheads"]}
    ],
    "toners": [
        {"name": "Klairs Supple Preparation Toner", "skin": ["dry", "sensitive"]},
        {"name": "Cosrx Snail Mucin Power Essence", "skin": ["dry", "damaged"]},
        {"name": "Plum Green Tea Toner", "skin": ["oily", "acne"]},
        {"name": "I’m From Rice Toner", "skin": ["dull", "dry"]}
    ]
}

# ---------------- Recommendation Logic (no pandas) ---------------- #
def get_recommendations(skin_type, concern, budget, category):
    # Build SQL query with basic LIKE matching and budget filter
    sql = "SELECT name, category, price, ingredients FROM products WHERE price <= ?"
    params = [budget]

    if skin_type.lower() != 'all':
        sql += " AND skin_type LIKE ?"
        params.append(f"%{skin_type}%")
    if concern.lower() != 'all':
        sql += " AND concern LIKE ?"
        params.append(f"%{concern}%")
    if category.lower() != 'all':
        sql += " AND category LIKE ?"
        params.append(f"%{category}%")

    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
    except Exception as e:
        return [], f"Database query failed: {e}"

    # If no results from DB, try fallback to product dictionary (in-memory)
    if not rows:
        matches = []
        cat_key = category.lower()
        if cat_key == 'all':
            keys = products.keys()
        else:
            # map category selections to our keys
            mapping = {
                'cleanser': 'cleansers', 'cleanser(s)': 'cleansers', 'cleansers': 'cleansers',
                'serum': 'serums', 'serums': 'serums',
                'moisturizer': 'moisturizers', 'moisturizers': 'moisturizers',
                'sunscreen': 'sunscreens', 'sunscreens': 'sunscreens',
                'toner': 'toners', 'toners': 'toners',
                'exfoliant': 'exfoliants', 'exfoliants': 'exfoliants',
                'acne_treatment': 'acne_treatments', 'acne_treatments': 'acne_treatments'
            }
            if cat_key in mapping:
                keys = [mapping[cat_key]]
            else:
                keys = products.keys()

        for k in keys:
            for p in products[k]:
                p_price = p.get('price', 9999)  # default high price
                p_skins = [s.lower() for s in p.get('skin', [])]
                if (budget is None or p_price <= budget) and (skin_type.lower() == 'all' or skin_type.lower() in p_skins or 'all' in p_skins):
                    # basic concern check in name/skin
                    if concern.lower() == 'all' or concern.lower() in p.get('name', '').lower() or concern.lower() in ' '.join(p_skins):
                        matches.append((p['name'], k[:-1].capitalize(), p.get('price', 'N/A'), p.get('skin')))
        return matches, None

    return rows, None

# ---------------- GUI Setup ---------------- #
root = tk.Tk()
root.title("Skin Care Recommendation System")
root.geometry("650x520")
root.configure(bg='#f7e9f3')

# Title
title_lbl = tk.Label(root, text="Skin Care Recommendation System", font=("Helvetica", 18, "bold"), bg='#f7e9f3')
title_lbl.pack(pady=10)

# Input Frame
frame = tk.Frame(root, bg='#f7e9f3')
frame.pack(pady=10)

# Skin Type
tk.Label(frame, text="Skin Type:", bg='#f7e9f3').grid(row=0, column=0, padx=10, pady=5, sticky='w')
skin_type_var = ttk.Combobox(frame, values=["Oily", "Dry", "Combination", "Sensitive", "Normal", "All"], width=20)
skin_type_var.grid(row=0, column=1)
skin_type_var.set('All')

# Concern
tk.Label(frame, text="Skin Concern:", bg='#f7e9f3').grid(row=1, column=0, padx=10, pady=5, sticky='w')
concern_var = ttk.Combobox(frame, values=["Acne", "Pigmentation", "Dryness", "Aging", "Pores", "Redness", "Hydration", "Barrier Repair", "All"], width=20)
concern_var.grid(row=1, column=1)
concern_var.set('All')

# Budget
tk.Label(frame, text="Max Budget (₹):", bg='#f7e9f3').grid(row=2, column=0, padx=10, pady=5, sticky='w')
budget_var = tk.Entry(frame, width=23)
budget_var.grid(row=2, column=1)
budget_var.insert(0, '1000')

# Category
tk.Label(frame, text="Product Category:", bg='#f7e9f3').grid(row=3, column=0, padx=10, pady=5, sticky='w')
category_var = ttk.Combobox(frame, values=["Serum", "Moisturizer", "Cleanser", "Toner", "Sunscreen", "Exfoliant", "All"], width=20)
category_var.grid(row=3, column=1)
category_var.set('All')

# ---------------- Output Box ---------------- #
result_box = tk.Text(root, width=80, height=18, wrap='word')
result_box.pack(pady=15)

# ---------------- Button Action ---------------- #
def show_recommendations():
    skin = skin_type_var.get() or 'All'
    concern = concern_var.get() or 'All'
    budget_text = budget_var.get() or ''
    category = category_var.get() or 'All'

    try:
        budget = int(budget_text) if budget_text else 99999
    except ValueError:
        messagebox.showerror("Input Error", "Budget must be a valid integer (e.g., 500).")
        return

    result_box.delete(1.0, tk.END)

    rows, err = get_recommendations(skin, concern, budget, category)
    if err:
        result_box.insert(tk.END, f"Error: {err}")
        return

    if not rows:
        result_box.insert(tk.END, "No matching products found. Try adjusting filters or use a higher budget.\n")
        return

    # rows can be from DB (tuples) or from fallback (list of tuples)
    for r in rows:
        # DB rows are tuples of (name, category, price, ingredients)
        if len(r) == 4:
            name, cat, price, ingredients = r
            result_box.insert(tk.END, f"Product: {name}\nCategory: {cat}\nPrice: ₹{price}\nIngredients: {ingredients}\n")
        else:
            # fallback format (name, category, price, skins)
            name, cat, price, skins = r
            result_box.insert(tk.END, f"Product: {name}\nCategory: {cat}\nPrice: ₹{price}\nSuitable for skin types: {skins}\n")
        result_box.insert(tk.END, "-------------------------------------------\n")


# Button
tk.Button(root, text="Get Recommendations", command=show_recommendations, font=("Helvetica", 12), bg="#ffb3d9", width=20).pack(pady=5)

# ---------------- Helpful Debug Info ---------------- #
# If the GUI appears blank or crashes, run this script from a terminal/command prompt to see traceback messages.
# Common fixes:
# - If ModuleNotFoundError: No module named 'tkinter' -> Install Python with Tcl/Tk or use your package manager (on Debian/Ubuntu: sudo apt-get install python3-tk)
# - If ModuleNotFoundError: No module named 'pandas' -> This version does not require pandas. If earlier versions used pandas, remove or install pandas via 'pip install pandas'.
# - If you see _tkinter.TclError: couldn't connect to display -> On Linux, ensure an X server is available or run with an environment providing DISPLAY (or use WSLg/remote X11).
# - For permission errors with the DB file, ensure you have write permissions in the folder where the script runs.

root.mainloop()