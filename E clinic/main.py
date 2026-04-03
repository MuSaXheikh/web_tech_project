import customtkinter as ctk

import tkinter as tk

from tkinter import ttk, messagebox

import sqlite3
from datetime import datetime
import os

import webbrowser

DB_NAME = 'eman_clinic.db'

# --- Database functions ---

def run_query(query, parameters=()):

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(query, parameters)
        conn.commit()

        return cursor.fetchall()

def setup_db():

    run_query('''CREATE TABLE IF NOT EXISTS patients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, address TEXT, phone TEXT)''')

    run_query('''CREATE TABLE IF NOT EXISTS inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, item_name TEXT UNIQUE NOT NULL, quantity INTEGER NOT NULL, price REAL NOT NULL)''')

    run_query('''CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, total_amount REAL, date TEXT, FOREIGN KEY(patient_id) REFERENCES patients(id))''')

    run_query('''CREATE TABLE IF NOT EXISTS invoice_items (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id INTEGER, item_name TEXT, quantity INTEGER, price REAL, FOREIGN KEY(invoice_id) REFERENCES invoices(id))''')

def create_invoice_html(invoice_id):

    res = run_query("SELECT patient_id, total_amount, date FROM invoices WHERE id=?", (invoice_id,))

    if not res: return None

    pat_id, total, date = res[0]
    

    pat = run_query("SELECT name, address, phone FROM patients WHERE id=?", (pat_id,))

    if not pat: return None

    pat_name, pat_addr, pat_phone = pat[0]
    

    items = run_query("SELECT item_name, quantity, price FROM invoice_items WHERE invoice_id=?", (invoice_id,))
    

    # Generate an elegant HTML string to print the invoice natively in a browser

    html_content = f"""

    <!DOCTYPE html>

    <html lang="en">

    <head>

    <meta charset="UTF-8">

    <title>Invoice #{invoice_id}</title>

    <style>

        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; }}

        .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, 0.15); font-size: 16px; line-height: 24px; background: white; border-radius: 8px; margin-top: 40px; }}

        .invoice-box table {{ width: 100%; line-height: inherit; text-align: left; border-collapse: collapse; }}

        .invoice-box table td {{ padding: 10px; vertical-align: top; }}

        .title {{ font-size: 45px; line-height: 45px; color: #1e3d59; font-weight: bold; padding-bottom: 20px; }}

        .heading td {{ background: #1e3d59; color: white; border-bottom: 1px solid #ddd; font-weight: bold; border-radius: 4px; }}

        .item td {{ border-bottom: 1px solid #eee; }}

        .total td {{ font-weight: bold; font-size: 1.2em; border-top: 2px solid #1e3d59; }}

        .print-btn {{ background: #1e3d59; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }}

        @media print {{ .print-btn {{ display: none; }} body {{ background: white; }} .invoice-box {{ box-shadow: none; border: none; margin-top: 0; padding: 0; }} }}

    </style>

    </head>

    <body>

        <div class="invoice-box">

            <table cellpadding="0" cellspacing="0">

                <tr>

                    <td colspan="2" class="title">Eman Clinic</td>

                    <td colspan="2" style="text-align: right">

                        <b>Invoice #:</b> {invoice_id}<br>

                        <b>Date:</b> {date}

                    </td>

                </tr>

                <tr>

                    <td colspan="2" style="padding-bottom: 30px;">

                        <b>Clinic Details:</b><br>

                        Eman Clinic<br>

                        Eman clinic ghoray shah road lahore<br>

                        03317086465

                    </td>

                    <td colspan="2" style="text-align: right; padding-bottom: 30px;">

                        <b>Patient Info:</b><br>

                        {pat_name}<br>

                        {pat_addr}<br>

                        Phone: {pat_phone}

                    </td>

                </tr>

                <tr class="heading">

                    <td>Item</td>

                    <td style="text-align: center">Quantity</td>

                    <td style="text-align: center">Price</td>

                    <td style="text-align: right">Subtotal</td>

                </tr>
    """

    for item in items:

        item_name, qty, price = item

        html_content += f"""

                <tr class="item">

                    <td>{item_name}</td>

                    <td style="text-align: center">{qty}</td>

                    <td style="text-align: center">RS{price:.2f}</td>

                    <td style="text-align: right">RS{(qty*price):.2f}</td>

                </tr>
        """
        

    html_content += f"""

                <tr class="total">

                    <td colspan="2"></td>

                    <td colspan="2" style="text-align: right">Total: RS{total:.2f}</td>

                </tr>

            </table>

            <div style="text-align: center; margin-top: 40px;">

                <p><i>Thank you for choosing Eman Clinic!</i></p>

                <button class="print-btn" onclick="window.print()">🖨️ Print Invoice</button
>
            </div>

        </div>

    </body>

    </html>
    """

    filename = f"invoice_{invoice_id}.html"

    filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)

    with open(filepath, "w", encoding="utf-8") as f:

        f.write(html_content)

    return filepath

# --- Main App Styling ---

ctk.set_appearance_mode("Dark")

ctk.set_default_color_theme("blue")

class EmanClinicApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Eman Clinic Management System")

        self.geometry("1100x750")
        

        setup_db()

        self.current_invoice_items = []
        

        # Header

        self.header = ctk.CTkLabel(self, text="Eman Clinic Management", font=ctk.CTkFont(size=28, weight="bold"))

        self.header.pack(pady=10)

        # TabView

        self.tabview = ctk.CTkTabview(self, width=1050, height=650)

        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        

        self.tabview.add("Patients")

        self.tabview.add("Inventory")

        self.tabview.add("Billing")

        self.tabview.add("Invoices History")

        self.setup_patients_tab()

        self.setup_inventory_tab()

        self.setup_billing_tab()

        self.setup_invoices_tab()

    # --- STYLE TREEVIEW (used across tabs for tables) ---

    def create_treeview(self, parent, columns):

        style = ttk.Style()

        style.theme_use("default")

        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=30, fieldbackground="#343638", bordercolor="#343638", borderwidth=0, font=('Helvetica', 11))

        style.map('Treeview', background=[('selected', '#22559b')])

        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat", font=('Helvetica', 12, 'bold'))

        style.map("Treeview.Heading", background=[('active', '#3484F0')])

        tree = ttk.Treeview(parent, columns=columns, show="headings")

        for col in columns:

            tree.heading(col, text=col)
        return tree

    # --- PATIENTS TAB ---

    def setup_patients_tab(self):

        tab = self.tabview.tab("Patients")

        tab.grid_columnconfigure(0, weight=1)
        

        action_frame = ctk.CTkFrame(tab)

        action_frame.pack(fill="x", padx=10, pady=5)
        

        ctk.CTkLabel(action_frame, text="Search Name:").pack(side="left", padx=10, pady=10)

        self.p_search = ctk.CTkEntry(action_frame, width=150)

        self.p_search.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(action_frame, text="Search", command=self.search_patient).pack(side="left", padx=10, pady=10)

        ctk.CTkButton(action_frame, text="Clear", command=self.load_patients).pack(side="left", padx=10, pady=10)
        

        ctk.CTkButton(action_frame, text="Delete Selected", command=self.delete_patient, fg_color="#dc3545", hover_color="#c82333").pack(side="right", padx=10, pady=10)

        ctk.CTkButton(action_frame, text="Edit Selected", command=self.edit_patient).pack(side="right", padx=10, pady=10)
        

        frame = ctk.CTkFrame(tab)

        frame.pack(fill="x", padx=10, pady=5)
        

        ctk.CTkLabel(frame, text="Patient Name:").grid(row=0, column=0, padx=10, pady=10)

        self.p_name = ctk.CTkEntry(frame, width=180)

        self.p_name.grid(row=0, column=1, padx=10, pady=10)
        

        ctk.CTkLabel(frame, text="Address:").grid(row=0, column=2, padx=10, pady=10)

        self.p_addr = ctk.CTkEntry(frame, width=220)

        self.p_addr.grid(row=0, column=3, padx=10, pady=10)
        

        ctk.CTkLabel(frame, text="Phone:").grid(row=0, column=4, padx=10, pady=10)

        self.p_phone = ctk.CTkEntry(frame, width=150)

        self.p_phone.grid(row=0, column=5, padx=10, pady=10)
        

        ctk.CTkButton(frame, text="Add Patient", command=self.add_patient, fg_color="#28a745", hover_color="#218838").grid(row=0, column=6, padx=10, pady=10)

        ctk.CTkButton(frame, text="Update", command=self.update_patient, fg_color="#ffc107", text_color="black").grid(row=0, column=7, padx=10, pady=10)
        

        self.p_tree = self.create_treeview(tab, ("ID", "Name", "Address", "Phone"))

        self.p_tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_patients()

        self.editing_patient_id = None


    def search_patient(self):

        query = self.p_search.get()

        for r in self.p_tree.get_children(): self.p_tree.delete(r)

        for row in run_query("SELECT * FROM patients WHERE name LIKE ?", (f"%{query}%",)): self.p_tree.insert("", "end", values=row)


    def delete_patient(self):
        selected = self.p_tree.selection()

        if not selected:

            messagebox.showerror("Error", "Select a patient to delete")
            return

        pat_id = self.p_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this patient?"):

            run_query("DELETE FROM patients WHERE id=?", (pat_id,))
            self.load_patients()

            self.refresh_dropdowns()


    def edit_patient(self):
        selected = self.p_tree.selection()

        if not selected:

            messagebox.showerror("Error", "Select a patient to edit")
            return

        pat_id, name, addr, phone = self.p_tree.item(selected[0])['values']

        self.p_name.delete(0, 'end'); self.p_name.insert(0, name)

        self.p_addr.delete(0, 'end'); self.p_addr.insert(0, addr if addr is not None and str(addr) != 'None' else '')

        self.p_phone.delete(0, 'end'); self.p_phone.insert(0, phone if phone is not None and str(phone) != 'None' else '')

        self.editing_patient_id = pat_id


    def update_patient(self):

        if not self.editing_patient_id:

            messagebox.showerror("Error", "Please load a patient to edit first (Edit Selected)")
            return

        name = self.p_name.get()

        if not name:

            messagebox.showerror("Error", "Name is required!")
            return

        run_query("UPDATE patients SET name=?, address=?, phone=? WHERE id=?", (name, self.p_addr.get(), self.p_phone.get(), self.editing_patient_id))

        self.p_name.delete(0, 'end'); self.p_addr.delete(0, 'end'); self.p_phone.delete(0, 'end')

        self.editing_patient_id = None

        self.load_patients(); self.refresh_dropdowns()


    def add_patient(self):

        name = self.p_name.get()

        if not name:

            messagebox.showerror("Error", "Name is required!")
            return

        run_query("INSERT INTO patients (name, address, phone) VALUES (?, ?, ?)", (name, self.p_addr.get(), self.p_phone.get()))

        self.p_name.delete(0, 'end'); self.p_addr.delete(0, 'end'); self.p_phone.delete(0, 'end')

        self.load_patients(); self.refresh_dropdowns()

    def load_patients(self):

        for r in self.p_tree.get_children(): self.p_tree.delete(r)

        for row in run_query("SELECT * FROM patients"): self.p_tree.insert("", "end", values=row)

    # --- INVENTORY TAB ---

    def setup_inventory_tab(self):

        tab = self.tabview.tab("Inventory")
        

        action_frame = ctk.CTkFrame(tab)

        action_frame.pack(fill="x", padx=10, pady=5)
        

        ctk.CTkLabel(action_frame, text="Search Item:").pack(side="left", padx=10, pady=10)

        self.i_search = ctk.CTkEntry(action_frame, width=150)

        self.i_search.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(action_frame, text="Search", command=self.search_item).pack(side="left", padx=10, pady=10)

        ctk.CTkButton(action_frame, text="Clear", command=self.load_inventory).pack(side="left", padx=10, pady=10)
        

        ctk.CTkButton(action_frame, text="Delete Selected", command=self.delete_item, fg_color="#dc3545", hover_color="#c82333").pack(side="right", padx=10, pady=10)

        ctk.CTkButton(action_frame, text="Edit Selected", command=self.edit_item).pack(side="right", padx=10, pady=10)


        frame = ctk.CTkFrame(tab)

        frame.pack(fill="x", padx=10, pady=5)
        

        ctk.CTkLabel(frame, text="Item Group Name:").grid(row=0, column=0, padx=10, pady=10)

        self.i_name = ctk.CTkEntry(frame, width=180)

        self.i_name.grid(row=0, column=1, padx=10, pady=10)
        

        ctk.CTkLabel(frame, text="Current Stock:").grid(row=0, column=2, padx=10, pady=10)

        self.i_qty = ctk.CTkEntry(frame, width=120)

        self.i_qty.grid(row=0, column=3, padx=10, pady=10)
        

        ctk.CTkLabel(frame, text="Unit Price (RS):").grid(row=0, column=4, padx=10, pady=10)

        self.i_price = ctk.CTkEntry(frame, width=120)

        self.i_price.grid(row=0, column=5, padx=10, pady=10)
        

        ctk.CTkButton(frame, text="Save", command=self.save_item, fg_color="#28a745", hover_color="#218838").grid(row=0, column=6, padx=10, pady=10)

        ctk.CTkButton(frame, text="Update", command=self.update_item, fg_color="#ffc107", text_color="black").grid(row=0, column=7, padx=10, pady=10)
        

        self.i_tree = self.create_treeview(tab, ("ID", "Item Name", "Quantity", "Price (RS)"))

        self.i_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_inventory()

        self.editing_item_id = None


    def search_item(self):

        query = self.i_search.get()

        for r in self.i_tree.get_children(): self.i_tree.delete(r)

        for row in run_query("SELECT * FROM inventory WHERE item_name LIKE ?", (f"%{query}%",)): self.i_tree.insert("", "end", values=row)


    def delete_item(self):
        selected = self.i_tree.selection()

        if not selected:

            messagebox.showerror("Error", "Select an item to delete")
            return

        item_id = self.i_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):

            run_query("DELETE FROM inventory WHERE id=?", (item_id,))

            self.load_inventory()

            self.refresh_dropdowns()


    def edit_item(self):
        selected = self.i_tree.selection()

        if not selected:

            messagebox.showerror("Error", "Select an item to edit")
            return

        item_id, item_name, qty, price = self.i_tree.item(selected[0])['values']

        self.i_name.delete(0, 'end'); self.i_name.insert(0, item_name)

        self.i_qty.delete(0, 'end'); self.i_qty.insert(0, qty)

        self.i_price.delete(0, 'end'); self.i_price.insert(0, price)

        self.editing_item_id = item_id


    def update_item(self):

        if not self.editing_item_id:

            messagebox.showerror("Error", "Please load an item to edit first")
            return

        name = self.i_name.get()

        try:

            qty, price = int(self.i_qty.get()), float(self.i_price.get())

        except ValueError:

            messagebox.showerror("Error", "Check quantity/price formats!")
            return

        run_query("UPDATE inventory SET item_name=?, quantity=?, price=? WHERE id=?", (name, qty, price, self.editing_item_id))

        self.i_name.delete(0, 'end'); self.i_qty.delete(0, 'end'); self.i_price.delete(0, 'end')

        self.editing_item_id = None

        self.load_inventory(); self.refresh_dropdowns()


    def save_item(self):

        name = self.i_name.get()

        try:

            qty, price = int(self.i_qty.get()), float(self.i_price.get())

        except ValueError:

            messagebox.showerror("Error", "Check quantity/price formats!")
            return
        

        existing = run_query("SELECT id, quantity FROM inventory WHERE item_name=?", (name,))

        if existing:

            run_query("UPDATE inventory SET quantity=?, price=? WHERE item_name=?", (existing[0][1]+qty, price, name))

        else:

            run_query("INSERT INTO inventory (item_name, quantity, price) VALUES (?, ?, ?)", (name, qty, price))
            

        self.i_name.delete(0, 'end'); self.i_qty.delete(0, 'end'); self.i_price.delete(0, 'end')

        self.load_inventory(); self.refresh_dropdowns()

    def load_inventory(self):

        for r in self.i_tree.get_children(): self.i_tree.delete(r)

        for row in run_query("SELECT * FROM inventory"): self.i_tree.insert("", "end", values=row)

    # --- BILLING TAB ---

    def setup_billing_tab(self):

        tab = self.tabview.tab("Billing")
        

        top_frame = ctk.CTkFrame(tab)

        top_frame.pack(fill="x", padx=10, pady=10)
        

        ctk.CTkLabel(top_frame, text="Search Patient:").grid(row=0, column=0, padx=10, pady=10)

        self.b_pat_search_var = tk.StringVar()
        self.b_pat_search_var.trace_add("write", self.filter_b_patients)

        self.b_pat_search = ctk.CTkEntry(top_frame, width=150, placeholder_text="Search...", textvariable=self.b_pat_search_var)

        self.b_pat_search.grid(row=0, column=1, padx=10, pady=10)


        ctk.CTkLabel(top_frame, text="Select Patient:").grid(row=0, column=2, padx=10, pady=10)

        self.b_pat_cb = ctk.CTkComboBox(top_frame, width=250)

        self.b_pat_cb.grid(row=0, column=3, padx=10, pady=10)
        

        ctk.CTkLabel(top_frame, text="Search Item:").grid(row=1, column=0, padx=10, pady=10)

        self.b_item_search_var = tk.StringVar()

        self.b_item_search_var.trace_add("write", self.filter_b_items)

        self.b_item_search = ctk.CTkEntry(top_frame, width=150, placeholder_text="Search...", textvariable=self.b_item_search_var)

        self.b_item_search.grid(row=1, column=1, padx=10, pady=10)


        ctk.CTkLabel(top_frame, text="Select Item:").grid(row=1, column=2, padx=10, pady=10)

        self.b_item_cb = ctk.CTkComboBox(top_frame, width=250)

        self.b_item_cb.grid(row=1, column=3, padx=10, pady=10)
        

        ctk.CTkLabel(top_frame, text="Qty:").grid(row=1, column=4, padx=10, pady=10)

        self.b_qty = ctk.CTkEntry(top_frame, width=60)

        self.b_qty.insert(0, "1")

        self.b_qty.grid(row=1, column=5, padx=10, pady=10)
        

        ctk.CTkButton(top_frame, text="Add to Cart", command=self.add_to_cart).grid(row=1, column=6, padx=10, pady=10)
        

        self.b_tree = self.create_treeview(tab, ("Item Name", "Qty", "Unit Price", "Subtotal"))

        self.b_tree.pack(fill="both", expand=True, padx=10, pady=5)
        

        sum_frame = ctk.CTkFrame(tab)

        sum_frame.pack(fill="x", padx=10, pady=10)

        self.b_total_lbl = ctk.CTkLabel(sum_frame, text="Total: RS0.00", font=ctk.CTkFont(size=24, weight="bold"), text_color="#28a745")

        self.b_total_lbl.pack(side="left", padx=20, pady=10)

        ctk.CTkButton(sum_frame, text="Checkout & Generate Invoice", fg_color="#1f6aa5", hover_color="#185280", font=ctk.CTkFont(weight="bold", size=15), command=self.checkout).pack(side="right", padx=20, pady=10)
        

        self.refresh_dropdowns()


    def filter_b_patients(self, *args):

        if not hasattr(self, 'all_patient_names'): return

        search = self.b_pat_search_var.get().lower()

        if not search:

            self.b_pat_cb.configure(values=self.all_patient_names if self.all_patient_names else ["No Patients Found"])
            return

        filtered = [p for p in self.all_patient_names if search in p.lower()]

        self.b_pat_cb.configure(values=filtered if filtered else ["No results found"])

        if filtered:

            self.b_pat_cb.set(filtered[0])

        else:

            self.b_pat_cb.set("No results found")


    def filter_b_items(self, *args):

        if not hasattr(self, 'all_item_names'): return

        search = self.b_item_search_var.get().lower()

        if not search:

            self.b_item_cb.configure(values=self.all_item_names if self.all_item_names else ["No Items Found"])
            return

        filtered = [i for i in self.all_item_names if search in i.lower()]

        self.b_item_cb.configure(values=filtered if filtered else ["No results found"])

        if filtered:

            self.b_item_cb.set(filtered[0])

        else:

            self.b_item_cb.set("No results found")

    def add_to_cart(self):

        item_sel = self.b_item_cb.get()

        if not item_sel or item_sel in ["No results found", "No Items Found"]: return

        item_name = item_sel.split(" (RS")[0]

        try:

            qty = int(self.b_qty.get())

        except ValueError: return
        

        price, stock = self.inv_map.get(item_name, (0, 0))

        if qty > stock:

            messagebox.showerror("Error", f"Only {stock} in stock!")
            return
            

        for i, item in enumerate(self.current_invoice_items):

            if item['name'] == item_name:

                if item['qty'] + qty > stock:

                    messagebox.showerror("Error", "Stock limit reached!")
                    return

                self.current_invoice_items[i]['qty'] += qty

                self.current_invoice_items[i]['sub'] = self.current_invoice_items[i]['qty'] * price
                self.upd_cart()
                return

        self.current_invoice_items.append({'name': item_name, 'qty': qty, 'price': price, 'sub': qty*price})
        self.upd_cart()

    def upd_cart(self):

        for r in self.b_tree.get_children(): self.b_tree.delete(r)

        total = 0

        for i in self.current_invoice_items:

            self.b_tree.insert("", "end", values=(i['name'], i['qty'], f"RS{i['price']}", f"RS{i['sub']}"))

            total += i['sub']

        self.b_total_lbl.configure(text=f"Total: RS{total:.2f}")

    def checkout(self):

        pat_sel = self.b_pat_cb.get()

        if not pat_sel or not self.current_invoice_items or pat_sel in ["No results found", "No Patients Found"]:

            messagebox.showerror("Error", "Select patient and add items.")
            return

        try:

            pat_id = int(pat_sel.split(" - ")[0])

        except ValueError:

            messagebox.showerror("Error", "Invalid patient selected.")
            return

        total = sum(i['sub'] for i in self.current_invoice_items)

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        c.execute("INSERT INTO invoices (patient_id, total_amount, date) VALUES (?, ?, ?)", (pat_id, total, date_str))

        inv_id = c.lastrowid

        for i in self.current_invoice_items:

            c.execute("INSERT INTO invoice_items (invoice_id, item_name, quantity, price) VALUES (?, ?, ?, ?)", (inv_id, i['name'], i['qty'], i['price']))

            c.execute("UPDATE inventory SET quantity = quantity - ? WHERE item_name = ?", (i['qty'], i['name']))

        conn.commit(); conn.close()
        

        self.current_invoice_items = []
        self.upd_cart()

        self.load_inventory()

        self.refresh_dropdowns()

        self.load_invoices()
        

        html_path = create_invoice_html(inv_id)

        if html_path: webbrowser.open(f'file:///{html_path}')

    def refresh_dropdowns(self):

        pats = run_query("SELECT id, name FROM patients")

        self.all_patient_names = [f"{p[0]} - {p[1]}" for p in pats] if pats else []

        self.b_pat_cb.configure(values=self.all_patient_names if self.all_patient_names else ["No Patients Found"])

        if self.all_patient_names: self.b_pat_cb.set(self.all_patient_names[0])
        

        inv = run_query("SELECT item_name, price, quantity FROM inventory WHERE quantity > 0")

        self.all_item_names = [f"{i[0]} (RS{i[1]} | Stock: {i[2]})" for i in inv] if inv else []

        self.b_item_cb.configure(values=self.all_item_names if self.all_item_names else ["No Items Found"])

        if self.all_item_names: self.b_item_cb.set(self.all_item_names[0])

        self.inv_map = {i[0]: (i[1], i[2]) for i in inv}

    # --- INVOICES HISTORY TAB ---

    def setup_invoices_tab(self):

        tab = self.tabview.tab("Invoices History")
        

        top = ctk.CTkFrame(tab)

        top.pack(fill="x", padx=10, pady=10)
        

        ctk.CTkLabel(top, text="Search Patient:").pack(side="left", padx=10, pady=10)

        self.invs_search = ctk.CTkEntry(top, width=150)

        self.invs_search.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(top, text="Search", command=self.search_invoices).pack(side="left", padx=10, pady=10)

        ctk.CTkButton(top, text="Clear / Refresh", command=self.load_invoices).pack(side="left", padx=10, pady=10)
        

        ctk.CTkButton(top, text="Delete Invoice", command=self.delete_invoice, fg_color="#dc3545", hover_color="#c82333").pack(side="right", padx=10, pady=10)

        ctk.CTkButton(top, text="View / Print Selected", font=ctk.CTkFont(weight="bold"), fg_color="#1f6aa5", command=self.print_selected_invoice).pack(side="right", padx=10, pady=10)
        

        self.invs_tree = self.create_treeview(tab, ("Invoice ID", "Patient Name", "Total Amount", "Date"))

        self.invs_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_invoices()


    def search_invoices(self):

        query = self.invs_search.get()

        for r in self.invs_tree.get_children(): self.invs_tree.delete(r)

        rows = run_query("SELECT i.id, p.name, i.total_amount, i.date FROM invoices i JOIN patients p ON i.patient_id = p.id WHERE p.name LIKE ? ORDER BY i.id DESC", (f"%{query}%",))

        for row in rows: self.invs_tree.insert("", "end", values=(row[0], row[1], f"RS{row[2]:.2f}", row[3]))


    def delete_invoice(self):

        selected = self.invs_tree.selection()

        if not selected:

            messagebox.showerror("Error", "Select an invoice to delete")
            return

        inv_id = self.invs_tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Confirm", f"Are you sure you want to delete invoice #{inv_id}?"):

            run_query("DELETE FROM invoice_items WHERE invoice_id=?", (inv_id,))

            run_query("DELETE FROM invoices WHERE id=?", (inv_id,))

            self.load_invoices()


    def load_invoices(self):

        for r in self.invs_tree.get_children(): self.invs_tree.delete(r)

        rows = run_query("SELECT i.id, p.name, i.total_amount, i.date FROM invoices i JOIN patients p ON i.patient_id = p.id ORDER BY i.id DESC")

        for row in rows: self.invs_tree.insert("", "end", values=(row[0], row[1], f"RS{row[2]:.2f}", row[3]))

    def print_selected_invoice(self):

        selected = self.invs_tree.selection()

        if not selected:

            messagebox.showerror("Error", "Please select an invoice from the list!")
            return

        inv_id = self.invs_tree.item(selected[0])['values'][0]

        html_path = create_invoice_html(inv_id)

        if html_path:

            webbrowser.open(f'file:///{html_path}')

if __name__ == "__main__":

    app = EmanClinicApp()
    app.mainloop()

