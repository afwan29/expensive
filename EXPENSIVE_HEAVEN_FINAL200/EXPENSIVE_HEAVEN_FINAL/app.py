
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def db():
    conn = sqlite3.connect("store.db")
    conn.row_factory = sqlite3.Row
    return conn

def init():
    conn = db()

    conn.execute('''
    CREATE TABLE IF NOT EXISTS settings(
        id INTEGER PRIMARY KEY,
        site_name TEXT,
        tagline TEXT,
        header_image TEXT,
        popup_banner TEXT
    )
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        image TEXT
    )
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT,
        phone TEXT,
        address TEXT,
        payment TEXT,
        trxid TEXT,
        custom_text TEXT,
        custom_image TEXT,
        product_name TEXT,
        total INTEGER,
        status TEXT
    )
    ''')

    s = conn.execute("SELECT COUNT(*) FROM settings").fetchone()[0]

    if s == 0:
        conn.execute(
            "INSERT INTO settings(site_name,tagline,header_image,popup_banner) VALUES (?,?,?,?)",
            (
                "Expensive Heaven",
                "Premium Custom Gifts Marketplace",
                "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?q=80&w=1400&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?q=80&w=1200&auto=format&fit=crop"
            )
        )

    p = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    if p == 0:
        demo = [
            ("Customize Key Ring K1",350,"https://images.unsplash.com/photo-1619994403073-2cec2fab91a7?q=80&w=1200&auto=format&fit=crop"),
            ("Customize Key Ring K2",350,"https://images.unsplash.com/photo-1619994403073-2cec2fab91a7?q=80&w=1200&auto=format&fit=crop"),
            ("Customize Key Ring K3",350,"https://images.unsplash.com/photo-1619994403073-2cec2fab91a7?q=80&w=1200&auto=format&fit=crop"),
            ("Customize Key Ring K4",350,"https://images.unsplash.com/photo-1619994403073-2cec2fab91a7?q=80&w=1200&auto=format&fit=crop"),
            ("Special Key Ring K1",400,"https://images.unsplash.com/photo-1619994403073-2cec2fab91a7?q=80&w=1200&auto=format&fit=crop"),
            ("Special Key Ring K2",400,"https://images.unsplash.com/photo-1619994403073-2cec2fab91a7?q=80&w=1200&auto=format&fit=crop"),
            ("Customize Wallet",700,"https://images.unsplash.com/photo-1548036328-c9fa89d128fa?q=80&w=1200&auto=format&fit=crop"),
            ("Ring & Regular Wallet Combo",1050,"https://images.unsplash.com/photo-1548036328-c9fa89d128fa?q=80&w=1200&auto=format&fit=crop"),
            ("Ring & Large Wallet Combo",1250,"https://images.unsplash.com/photo-1548036328-c9fa89d128fa?q=80&w=1200&auto=format&fit=crop")
        ]

        conn.executemany(
            "INSERT INTO products(name,price,image) VALUES (?,?,?)",
            demo
        )

    conn.commit()
    conn.close()

init()

@app.route("/")
def home():
    conn = db()
    products = conn.execute("SELECT * FROM products").fetchall()
    settings = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
    conn.close()
    return render_template("index.html", products=products, settings=settings)

@app.route("/buy/<int:id>", methods=["GET","POST"])
def buy(id):
    conn = db()
    product = conn.execute("SELECT * FROM products WHERE id=?", (id,)).fetchone()
    settings = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()

    if request.method == "POST":
        conn.execute(
            "INSERT INTO orders(customer,phone,address,payment,trxid,custom_text,custom_image,product_name,total,status) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                request.form["customer"],
                request.form["phone"],
                request.form["address"],
                request.form["payment"],
                request.form["trxid"],
                request.form["custom_text"],
                request.form["custom_image"],
                product["name"],
                product["price"],
                "Pending"
            )
        )

        conn.commit()
        conn.close()

        return render_template("success.html", settings=settings)

    conn.close()
    return render_template("checkout.html", product=product, settings=settings)

@app.route("/admin")
def admin():
    conn = db()

    products = conn.execute("SELECT * FROM products").fetchall()
    settings = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()

    conn.close()

    return render_template("admin.html", products=products, settings=settings, orders=orders)

@app.route("/update-settings", methods=["POST"])
def update_settings():
    conn = db()

    conn.execute(
        "UPDATE settings SET site_name=?, tagline=?, header_image=?, popup_banner=? WHERE id=1",
        (
            request.form["site_name"],
            request.form["tagline"],
            request.form["header_image"],
            request.form["popup_banner"]
        )
    )

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/edit-product/<int:id>", methods=["GET","POST"])
def edit_product(id):
    conn = db()

    if request.method == "POST":
        conn.execute(
            "UPDATE products SET name=?, price=?, image=? WHERE id=?",
            (
                request.form["name"],
                request.form["price"],
                request.form["image"],
                id
            )
        )
        conn.commit()
        conn.close()
        return redirect("/admin")

    product = conn.execute("SELECT * FROM products WHERE id=?", (id,)).fetchone()
    conn.close()

    return render_template("edit.html", product=product)

@app.route("/delete-product/<int:id>")
def delete_product(id):
    conn = db()
    conn.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/confirm-order/<int:id>")
def confirm_order(id):
    conn = db()
    conn.execute("UPDATE orders SET status='Confirmed' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)
