"""
VeraPOS - Point of Sale System
Flask backend with REST API and SPA frontend
"""

import os
import re
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

# ---------------------------------------------------------------------------
# App config
# ---------------------------------------------------------------------------
app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL", "sqlite:///pos.db")
# Railway gives postgres:// but SQLAlchemy needs postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))

db = SQLAlchemy(app)

JWT_SECRET = app.config["SECRET_KEY"]
JWT_EXP_HOURS = 24


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${h.hex()}"


def check_password(password: str, hashed: str) -> bool:
    try:
        salt, h = hashed.split("$")
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex() == h
    except Exception:
        return False


def make_token(user_id: int, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXP_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception:
        return None


def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        payload = decode_token(auth[7:])
        if not payload:
            return jsonify({"error": "Invalid token"}), 401
        request.user_id = payload["sub"]
        request.user_role = payload["role"]
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        payload = decode_token(auth[7:])
        if not payload or payload["role"] != "admin":
            return jsonify({"error": "Admin access required"}), 403
        request.user_id = payload["sub"]
        request.user_role = payload["role"]
        return f(*args, **kwargs)
    return wrapper


def gen_reference() -> str:
    now = datetime.now()
    rand = secrets.token_hex(3).upper()
    return f"S{now.strftime('%y%m%d%H%M%S')}{rand}"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(50), default="cashier")  # admin, manager, cashier
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "email": self.email,
            "role": self.role, "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    products = db.relationship("Product", backref="category", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=True)
    barcode = db.Column(db.String(100), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    price = db.Column(db.Float, nullable=False, default=0)
    cost = db.Column(db.Float, default=0)
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "sku": self.sku,
            "barcode": self.barcode, "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "price": self.price, "cost": self.cost, "stock": self.stock,
            "is_active": self.is_active,
        }


class Sale(db.Model):
    __tablename__ = "sales"
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    cashier_name = db.Column(db.String(255))
    customer_name = db.Column(db.String(255), default="Walk-in")
    subtotal = db.Column(db.Float, default=0)
    discount = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    payment_method = db.Column(db.String(50), default="cash")
    amount_paid = db.Column(db.Float, default=0)
    change_amount = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    items = db.relationship("SaleItem", backref="sale", lazy=True)

    def to_dict(self):
        return {
            "id": self.id, "reference": self.reference,
            "cashier_name": self.cashier_name,
            "customer_name": self.customer_name,
            "subtotal": self.subtotal, "discount": self.discount,
            "tax": self.tax, "total": self.total,
            "payment_method": self.payment_method,
            "amount_paid": self.amount_paid, "change_amount": self.change_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "items": [i.to_dict() for i in self.items],
        }


class SaleItem(db.Model):
    __tablename__ = "sale_items"
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))
    product_name = db.Column(db.String(255))
    price = db.Column(db.Float, default=0)
    quantity = db.Column(db.Integer, default=1)
    subtotal = db.Column(db.Float, default=0)

    def to_dict(self):
        return {
            "id": self.id, "product_id": self.product_id,
            "product_name": self.product_name, "price": self.price,
            "quantity": self.quantity, "subtotal": self.subtotal,
        }


# ---------------------------------------------------------------------------
# Database init
# ---------------------------------------------------------------------------
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email="admin@verapos.com").first():
            admin = User(
                name="Admin",
                email="admin@verapos.com",
                password=hash_password("admin123"),
                role="admin",
            )
            db.session.add(admin)
            # Seed some categories
            cats = ["Food", "Beverages", "Snacks", "Personal Care", "Household"]
            for c in cats:
                if not Category.query.filter_by(name=c).first():
                    db.session.add(Category(name=c))
            db.session.commit()


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("login.html")


@app.route("/app")
def main_app():
    return render_template("app.html")


@app.route("/setup")
def setup():
    """Initialize database and show status."""
    init_db()
    users = User.query.all()
    return jsonify({
        "status": "ok",
        "message": "Database initialized",
        "users": [u.to_dict() for u in users],
    })


# ---------------------------------------------------------------------------
# Auth API
# ---------------------------------------------------------------------------
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password(password, user.password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403

    token = make_token(user.id, user.role)
    return jsonify({"token": token, "user": user.to_dict()})


@app.route("/api/auth/me")
@auth_required
def api_me():
    user = User.query.get(request.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()})


# ---------------------------------------------------------------------------
# Dashboard API
# ---------------------------------------------------------------------------
@app.route("/api/dashboard/stats")
@auth_required
def api_dashboard():
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_products = Product.query.filter_by(is_active=True).count()
    low_stock = Product.query.filter(Product.is_active == True, Product.stock <= 10).count()
    total_sales_today = Sale.query.filter(Sale.created_at >= today).count()
    revenue_today = db.session.query(db.func.coalesce(db.func.sum(Sale.total), 0)).filter(
        Sale.created_at >= today
    ).scalar()

    # Last 7 days revenue
    week_ago = today - timedelta(days=7)
    revenue_week = db.session.query(db.func.coalesce(db.func.sum(Sale.total), 0)).filter(
        Sale.created_at >= week_ago
    ).scalar()

    total_sales_all = Sale.query.count()
    revenue_all = db.session.query(db.func.coalesce(db.func.sum(Sale.total), 0)).scalar()

    # Recent sales
    recent = Sale.query.order_by(Sale.created_at.desc()).limit(10).all()

    # Top products (by quantity sold)
    top_products = (
        db.session.query(
            SaleItem.product_name,
            db.func.sum(SaleItem.quantity).label("qty"),
            db.func.sum(SaleItem.subtotal).label("revenue"),
        )
        .group_by(SaleItem.product_name)
        .order_by(db.func.sum(SaleItem.quantity).desc())
        .limit(5)
        .all()
    )

    return jsonify({
        "total_products": total_products,
        "low_stock": low_stock,
        "sales_today": total_sales_today,
        "revenue_today": float(revenue_today),
        "revenue_week": float(revenue_week),
        "total_sales": total_sales_all,
        "revenue_all": float(revenue_all),
        "recent_sales": [s.to_dict() for s in recent],
        "top_products": [
            {"name": p[0], "quantity": int(p[1]), "revenue": float(p[2])}
            for p in top_products
        ],
    })


# ---------------------------------------------------------------------------
# Categories API
# ---------------------------------------------------------------------------
@app.route("/api/categories")
@auth_required
def api_categories_list():
    cats = Category.query.order_by(Category.name).all()
    return jsonify([c.to_dict() for c in cats])


@app.route("/api/categories", methods=["POST"])
@auth_required
def api_categories_create():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name required"}), 400
    cat = Category(name=name)
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201


@app.route("/api/categories/<int:cat_id>", methods=["DELETE"])
@admin_required
def api_categories_delete(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Products API
# ---------------------------------------------------------------------------
@app.route("/api/products")
@auth_required
def api_products_list():
    q = request.args.get("q", "").strip()
    cat_id = request.args.get("category_id")
    query = Product.query
    if q:
        query = query.filter(
            db.or_(
                Product.name.ilike(f"%{q}%"),
                Product.sku.ilike(f"%{q}%"),
                Product.barcode.ilike(f"%{q}%"),
            )
        )
    if cat_id:
        query = query.filter_by(category_id=int(cat_id))
    active_only = request.args.get("active")
    if active_only == "1":
        query = query.filter_by(is_active=True)
    products = query.order_by(Product.name).all()
    return jsonify([p.to_dict() for p in products])


@app.route("/api/products", methods=["POST"])
@auth_required
def api_products_create():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name required"}), 400
    product = Product(
        name=name,
        sku=data.get("sku", "").strip() or None,
        barcode=data.get("barcode", "").strip() or None,
        category_id=data.get("category_id") or None,
        price=float(data.get("price", 0)),
        cost=float(data.get("cost", 0)),
        stock=int(data.get("stock", 0)),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201


@app.route("/api/products/<int:pid>", methods=["PUT"])
@auth_required
def api_products_update(pid):
    product = Product.query.get_or_404(pid)
    data = request.get_json() or {}
    if "name" in data:
        product.name = data["name"].strip()
    if "sku" in data:
        product.sku = data["sku"].strip() or None
    if "barcode" in data:
        product.barcode = data["barcode"].strip() or None
    if "category_id" in data:
        product.category_id = data["category_id"] or None
    if "price" in data:
        product.price = float(data["price"])
    if "cost" in data:
        product.cost = float(data["cost"])
    if "stock" in data:
        product.stock = int(data["stock"])
    if "is_active" in data:
        product.is_active = bool(data["is_active"])
    db.session.commit()
    return jsonify(product.to_dict())


@app.route("/api/products/<int:pid>", methods=["DELETE"])
@admin_required
def api_products_delete(pid):
    product = Product.query.get_or_404(pid)
    product.is_active = False
    db.session.commit()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Sales API
# ---------------------------------------------------------------------------
@app.route("/api/sales", methods=["POST"])
@auth_required
def api_sales_create():
    data = request.get_json() or {}
    items = data.get("items", [])
    if not items:
        return jsonify({"error": "No items"}), 400

    user = User.query.get(request.user_id)

    subtotal = 0
    sale_items = []
    for item in items:
        product = Product.query.get(item["product_id"])
        if not product:
            return jsonify({"error": f"Product {item['product_id']} not found"}), 400
        qty = int(item.get("quantity", 1))
        if product.stock < qty:
            return jsonify({"error": f"Insufficient stock for {product.name}"}), 400
        line_total = product.price * qty
        subtotal += line_total
        sale_items.append(SaleItem(
            product_id=product.id,
            product_name=product.name,
            price=product.price,
            quantity=qty,
            subtotal=line_total,
        ))
        product.stock -= qty

    discount = float(data.get("discount", 0))
    total = subtotal - discount
    amount_paid = float(data.get("amount_paid", total))
    change_amount = max(0, amount_paid - total)

    sale = Sale(
        reference=gen_reference(),
        user_id=request.user_id,
        cashier_name=user.name if user else "Unknown",
        customer_name=data.get("customer_name", "Walk-in") or "Walk-in",
        subtotal=subtotal,
        discount=discount,
        total=total,
        payment_method=data.get("payment_method", "cash"),
        amount_paid=amount_paid,
        change_amount=change_amount,
    )
    db.session.add(sale)
    db.session.flush()

    for si in sale_items:
        si.sale_id = sale.id
        db.session.add(si)

    db.session.commit()
    return jsonify(sale.to_dict()), 201


@app.route("/api/sales")
@auth_required
def api_sales_list():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    query = Sale.query
    if date_from:
        query = query.filter(Sale.created_at >= date_from)
    if date_to:
        query = query.filter(Sale.created_at <= date_to)

    query = query.order_by(Sale.created_at.desc())
    total = query.count()
    sales = query.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        "sales": [s.to_dict() for s in sales],
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page,
    })


@app.route("/api/sales/<int:sid>")
@auth_required
def api_sales_get(sid):
    sale = Sale.query.get_or_404(sid)
    return jsonify(sale.to_dict())


# ---------------------------------------------------------------------------
# Users API (admin)
# ---------------------------------------------------------------------------
@app.route("/api/users")
@admin_required
def api_users_list():
    users = User.query.order_by(User.name).all()
    return jsonify([u.to_dict() for u in users])


@app.route("/api/users", methods=["POST"])
@admin_required
def api_users_create():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    role = data.get("role", "cashier")

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(name=name, email=email, password=hash_password(password), role=role)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@app.route("/api/users/<int:uid>", methods=["PUT"])
@admin_required
def api_users_update(uid):
    user = User.query.get_or_404(uid)
    data = request.get_json() or {}
    if "name" in data:
        user.name = data["name"].strip()
    if "email" in data:
        user.email = data["email"].strip()
    if "role" in data:
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = bool(data["is_active"])
    if "password" in data and data["password"]:
        user.password = hash_password(data["password"])
    db.session.commit()
    return jsonify(user.to_dict())


@app.route("/api/users/<int:uid>", methods=["DELETE"])
@admin_required
def api_users_delete(uid):
    user = User.query.get_or_404(uid)
    user.is_active = False
    db.session.commit()
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "verapos", "version": "2.0.0"})


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
