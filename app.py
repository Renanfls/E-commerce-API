import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user , login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

login_manager = LoginManager(app)
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

# Modelagem
# User (id, username, password, cart)
class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), nullable=False, unique=True)
  password = db.Column(db.String(80), nullable=True)
  cart = db.relationship('CartItem', backref='user', lazy=True)

# Produto (id, name, price, description)
class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  price = db.Column(db.Float, nullable=False)
  description = db.Column(db.Text, nullable=True)

# CartItem
class CartItem(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
  #quantity = db.Column(db.Integer, nullable=False, default=1)
  

# Autenticação
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

# === ROUTES ===

# LOGIN
@app.route('/login', methods=["POST"])
def login():
  data = request.json
  user = User.query.filter_by(username=data.get('username')).first()
  if user and user.password == data.get('password'):
    login_user(user)
    return jsonify({"message": "Login successful"}), 200
  return jsonify({"message": "Unauthorized. Invalid credentials"}), 401

# LOGOUT
@app.route('/logout', methods=["POST"])
@login_required
def logout():
  logout_user()
  return jsonify({"message": "Logout successful"})

# ADD
@app.route('/api/products/add', methods=["POST"])
@login_required  # Apenas usuários logados podem adicionar produtos
def add_product():
  data = request.json
  if 'name' in data and 'price' in data:
    product = Product(name=data['name'], price=data['price'], description=data.get('description' , ""))
    try:
      db.session.add(product)
      db.session.commit()
      return jsonify({"message": "Product added successfully"})
    except Exception as e:
      db.session.rollback()
      return jsonify({"message": f"Failed to add product: {str(e)}"}), 500
  return jsonify({"message": "Invalid product data"}), 400

# DELETE
@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required  # Apenas usuários logados podem deletar produtos
def delete_product(product_id):
  product = Product.query.get(product_id)
  if product:
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"})
  return jsonify({"message": "Product not found"}), 404

# GET_DETAILS
@app.route('/api/products/<int:product_id>', methods=["GET"])
def get_details(product_id):
  product = Product.query.get(product_id)
  if product:
    return jsonify({
      "id": product.id,
      "name": product.name,
      "price": product.price,
      "description": product.description
    })
  return jsonify({"message": "Product not found"}), 404

# UPDATE
@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required  # Apenas usuários logados podem editar produtos
def update_product(product_id):
  product = Product.query.get(product_id)
  if not product:
    return jsonify({"message": "Product not found"}), 404
  
  data = request.json
  if 'name' in data:
    product.name = data['name']

  if 'price' in data:
    product.price = data['price']
  
  if 'description' in data:
    product.description = data['description']

  db.session.commit()  
  return jsonify({"message": "Product updated successfully"})

# GET PRODUCTS
@app.route('/api/products', methods=["GET"])
def get_products():
  products = Product.query.all()
  products_list = [{
      "id": product.id,
      "name": product.name,
      "price": product.price,
  } for product in products]
  return jsonify(products_list)

# ADD_PRODUCT_TO_CART
@app.route('/api/cart/add/<int:product_id>', methods=["POST"])
@login_required 
def add_to_cart(product_id):
  user = User.query.get_or_404(int(current_user.id))
  product = Product.query.get(product_id)

  if user and product:
    cart_item = CartItem(user_id=user.id, product_id=product.id)
    db.session.add(cart_item)
    db.session.commit()
    return jsonify({"message": "Product added to cart successfully"})
  return jsonify({"message": "Failed to add product to cart"}), 400

# DELETE_PRODUCT_TO_CART
@app.route('/api/cart/remove/<int:product_id>', methods=["DELETE"])
@login_required
def remove_from_cart(product_id):
  cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
  if cart_item:
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Product deleted to cart successfully"})
  return jsonify({"message": "Failed to deleted product to cart"}), 400

# GET_PRODUCTS_TO_CART
@app.route('/api/cart', methods=["GET"])
@login_required
def view_cart():
  user = User.query.get_or_404(int(current_user.id))
  cart_items = user.cart

  # get all cart items
  product_ids = [item.product_id for item in cart_items]
  # get all products with their ids
  products = {product.id: product for product in Product.query.filter(Product.id.in_(product_ids)).all()}

  cart_content = [{
      "id": cart_item.id,
      "user_id": cart_item.user_id,
      "product_id": cart_item.product_id,
      "product_name": products[cart_item.product_id].name,
      "product_price": products[cart_item.product_id].price,
  } for cart_item in cart_items]
  return jsonify(cart_content)

# CHECKOUT
@app.route('/api/cart/checkout', methods=["POST"])
@login_required
def checkout():
  user = User.query.get_or_404(int(current_user.id))
  db.session.query(CartItem).filter_by(user_id=user.id).delete()
  db.session.commit()
  return jsonify({"message": "Checkout successful. Cart has been cleared."})

if __name__ == "__main__":
	app.run(debug=True)