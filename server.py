from flask import Flask, request, jsonify, send_from_directory,session, redirect, url_for, render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes
app.secret_key = 'your_super_secret_key'
# Path to the users.json file
USERS_FILE = 'users.json'
ORDERS_FILE = 'orders.json'
CARTS_FILE = 'carts.json'
session={}
@app.route('/')
def serve_index():
    return send_from_directory('', 'index.html')

@app.route('/index.html')
def redirect_index():
    return serve_index()

@app.route('/register')
def serve_register():
    return send_from_directory('', 'register.html')

@app.route('/register.html')
def redirect_register():
    return serve_register()


@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid input.'}), 400

    email = data.get('email')
    password = data.get('password')
    user_type = data.get('userType')
    name = data.get('name')
    if not email or not password or not user_type:
        return jsonify({'message': 'Missing required fields.'}), 400

    users_file = 'users.json'
    # Load existing users from the JSON file, or create an empty list if the file doesn't exist or is empty.
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
        except json.JSONDecodeError:
            users = []
    else:
        users = []

    # Check if a user with the same email already exists
    if any(user.get('email') == email for user in users):
        return jsonify({'message': 'User already exists.'}), 400

    # Create new user dictionary
    new_user = {
        'email': email,
        'password': password,  # Note: In production, NEVER store plain passwords.
        'role': user_type,
        'name':name,
        'totalOrders': 0,
        'cancellations': 0
    }
    # Append the new user and save to the file
    users.append(new_user)
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=4)

    return jsonify({'message': 'Registration successful.'}), 201

@app.route('/customer_dashboard')
def serve_customer_dashboard():
    print(session)
    if 'user' not in session:
        return redirect(url_for('login_page'))  # Ensure login page exists

    user_email = session['user']

    # Load users from users.json
    users = read_users()  # Use the read_users function

    # Find the user's name based on email
    user = next((u for u in users if u['email'] == user_email), None)

    if not user:
        return "Unauthorized", 401  # Handle missing user case

    return render_template('customer_dashboard.html', user_name=user['name'],to=user['totalOrders'],co=user['cancellations'])


@app.route('/customer_dashboard.html')
def redirect_customer_dashboard():
    return serve_customer_dashboard()

@app.route('/restaurant_dashboard')
def serve_restaurant_dashboard():
    return send_from_directory('', 'restaurant_dashboard.html')

@app.route('/restaurant_dashboard.html')
def redirect_restaurant_dashboard():
    return serve_restaurant_dashboard()

@app.route('/admin_dashboard')
def serve_admin_dashboard():
    return send_from_directory('', 'admin_dashboard.html')

@app.route('/admin_dashboard.html')
def redirect_admin_dashboard():
    return serve_admin_dashboard()

@app.route('/menu.json')
def serve_menu():
    return send_from_directory('', 'menu.json')

# Remove duplicate definition of serve_images

@app.route('/cart')
def serve_cart():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    user_email = session.get('user')

    # Load the user's cart from CARTS_FILE (assumed to be structured as a dict)
    if os.path.exists(CARTS_FILE):
        with open(CARTS_FILE, 'r') as f:
            carts = json.load(f)
    else:
        carts = {}

    cart_items = carts.get(user_email, [])
    
    # Render the template and pass cart_items and user_email to it
    return render_template('cart.html', cart_items=cart_items, user_email=user_email)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401
    current_user = session.get('user')
    item_name = request.json.get('name')
    
    # Load existing carts
    if os.path.exists(CARTS_FILE):
        with open(CARTS_FILE, 'r') as f:
            carts = json.load(f)
    else:
        carts = {}
    
    if current_user in carts:
        # Remove items that match the given name
        carts[current_user] = [item for item in carts[current_user] if item.get('name') != item_name]
    
    # Save the updated carts back to the file
    with open(CARTS_FILE, 'w') as f:
        json.dump(carts, f, indent=4)
    
    return jsonify({"success": True})




@app.route('/cart.html')
def serve_cart_html():
    return send_from_directory('', 'cart.html')

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('images', filename)

@app.route('/create-order', methods=['POST'])
def create_order():
    order_data = request.json
    order_data['type'] = "SAFE"  # Set default value for type
    with open('orders.json', 'r+') as file:
        orders = json.load(file)
        orders.append(order_data)
        file.seek(0)
        #print(order_data)
        json.dump(orders, file, indent=4)
    return jsonify({"message": "Order created successfully!"}), 201


@app.route('/save_cart', methods=['POST'])
def save_cart():
    if 'user' not in session:
        return jsonify({"error": "Not logged in"}), 401

    customer = session['user']  # This is our customer identifier
    new_items = request.json.get("items", [])  # Expecting a JSON payload like { "items": ["item1", "item2"] }
    
    # Load existing carts from file (or initialize if not present)
    if os.path.exists(CARTS_FILE):
        with open(CARTS_FILE, 'r') as f:
            carts = json.load(f)
    else:
        carts = {}

    # If the customer already has a cart, add new items to it.
    # Otherwise, create a new cart entry for the customer.
    #print(customer)
    if customer in carts:
        carts[customer].extend(new_items)
    else:
        carts[customer] = new_items

    # Write back the updated carts to the file
    with open(CARTS_FILE, 'w') as f:
        json.dump(carts, f, indent=4)

    return jsonify({"message": "Cart saved successfully!", "cart": carts[customer]}), 200

# Endpoint to fetch all orders
@app.route('/orders', methods=['GET'])
def fetch_orders():
    with open('orders.json', 'r+') as file:
        orders = json.load(file)
        users = read_users()  # Read users once instead of inside the loop
        
        for order in orders:
            user_email = order.get('name')
            
            # Check if 'name' contains an email string or a dictionary
            if isinstance(user_email, dict):  
                user_email = user_email.get('email', '')

            
            
            # Find the user by email
              # Assign 'Unknown' if user not found

    return jsonify(orders), 200

# Endpoint to update order status
@app.route('/update-order', methods=['POST'])
def update_order():
    data = request.json
    order_number = data.get('order_number')
    status = data.get('status').lower()  # Ensure status is lowercase
    
    with open(ORDERS_FILE, 'r') as file:
        orders = json.load(file)  # Read orders once
        for order in orders:
            if order.get('order_number') == order_number:  # Check if order_number matches
                order['status'] = status  # Update to the provided status
                break  # Exit the loop once the order is found

    with open(ORDERS_FILE, 'w') as file:  # Open for writing
        json.dump(orders, file, indent=4)  # Write the updated orders back to the file
        file.truncate()  # Ensure the file is truncated to remove any leftover data

    return jsonify({"message": f"Order status updated to {status}!"}), 200

# New endpoint for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    users = read_users()
    user = next((user for user in users if user['email'] == email and user['password'] == password), None)

    if user:
        # Store user email and role in the session to maintain login state.
        session['user'] = user['email']
        session['role'] = user['role']
        #print(session)
        return jsonify({'message': 'Login successful!', 'role': user['role']}), 200
    else:
        return jsonify({'message': 'Invalid email or password.'}), 401

@app.route('/login_page')
def login_page():
    # This could return a login.html template in a real app.
    return send_from_directory('', 'index.html')

# New endpoint for checkout
def get_next_order_number():
    try:
        with open(ORDERS_FILE, "r") as file:
            orders = json.load(file)
        return orders[-1]["order_number"] + 1 if orders else 1
    except (FileNotFoundError, json.JSONDecodeError):
        return 1

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 403
    
    user_email = session['user']
    users = read_users()  # Use the read_users function

    # Find the user's name based on email
    user = next((u for u in users if u['email'] == user_email), None)

    if not user:
        return "Unauthorized", 401

    data = request.json
    items = data.get("items", [])

    if not items:
        return jsonify({"success": False, "error": "No items in cart"}), 400
    total_orders = user['totalOrders']
    canceled_orders = user['cancellations']
    
    # Determine type (Good/Bad)
    order_type = "Good" if total_orders == 0 or (canceled_orders / total_orders) < 0.5 else "Bad"


    order = {
        "name": user['name'],  # You might replace this with a full user profile lookup
        "items": items,
        "status": "Pending",
        "type":order_type,
        "order_number": get_next_order_number()
    }
    cart_data = read_json(CARTS_FILE)
    del cart_data[user_email]
    write_json(CARTS_FILE, cart_data)
    try:
        with open(ORDERS_FILE, "r+") as file:
            try:
                orders = json.load(file)
            except json.JSONDecodeError:
                orders = []
            orders.append(order)
            file.seek(0)
            json.dump(orders, file, indent=4)
             
        return jsonify({"success": True, "message": "Order placed successfully!"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def read_json(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
def read_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r') as file:
        return json.load(file)

def write_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)

def read_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, 'r') as file:
        return json.load(file)

def write_orders(orders):
    with open(ORDERS_FILE, 'w') as file:
        json.dump(orders, file, indent=4)

def write_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
@app.route('/api/user')
def get_user():
    if 'user' in session:
        return jsonify({'user_email': session['user']})
    return jsonify({'error': 'User not logged in'}), 401


@app.route('/order_summary', methods=['GET'])
def order_summary():
    if 'user' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 403

    user_email = session['user']
    user_name = get_user_name(user_email)  # Fetch the user's name

    try:
        with open(ORDERS_FILE, "r") as file:
            orders = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        orders = {}

    user_orders = orders.get(user_email, [])  # Fetch only the user's orders
    
    # Count total and canceled orders
    total_orders = len(user_orders)
    canceled_orders = sum(1 for order in user_orders if order.get("status") == "Cancelled")
    
    # Determine type (Good/Bad)
    order_type = "Good" if total_orders == 0 or (canceled_orders / total_orders) < 0.5 else "Bad"

    return jsonify({
        "success": True,
        "user_name": user_name,
        "total_orders": total_orders,
        "canceled_orders": canceled_orders,
        "order_type": order_type
    })
def get_user_name(user_email):
    users = read_users()  # This function should read user data from your users file/database
    user = next((u for u in users if u['email'] == user_email), None)
    return user['name'] if user else "Unknown User"
if __name__ == '__main__':
    app.run(debug=True, port=5000)
