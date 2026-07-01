import os
import json
import requests
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from google import genai
from google.genai import types
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
load_dotenv()

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "DLq28@03LjpDQ2005!LjM"),
        database=os.getenv("MYSQL_DB", "pasabuy_db")
    )

def parse_raw_groceries(raw_input_string):
    """Uses Gemini to clean and categorize messy user inputs."""
    client = genai.Client()
    prompt = f"""
    You are an expert grocery data parser for the "Sapat App". Your goal is to map unstructured user requests into a strict list of database categories.

    ALLOWED CATEGORIES:
    ["FRUITS", "CONDIMENTS", "OIL", "SPICES", "FISH", "VEGETABLES", "RICE", "CORN", "BEANS", "MEAT", "LIVESTOCK AND POULTRY PRODUCTS", "CANNED GOODS", 
    "BATH SOAP", "BATTERIES", "SALT", "PROCESSED MILK", "COFFEE", "BOTTLED WATER", "BREAD", "CANNED GOODS", "NOODLES", "SNACKS", "BEVERAGES", "SHAMPOO", 
    "TOOTHPASTE", "HAIR CONDITIONER", "DISHWASHING", "DETERGENT", "FABRIC CONDITIONER", "DAIRY & SPREADS", "COFFEE", "PANTRY STAPLES", "NOODLES & PASTA", 
    "CONDIMENTS & SAUCES", "SNACKS & SNACK FOODS", "LOTION", "BLEACH"]

    RULES:
    - If an item doesn't fit into an allowed category, ignore it entirely.
    - If multiple items map to the same category, only list the category once.
    - Output must be a pure JSON array of strings. No markdown, no explanations.

    EXAMPLES:
    Input: "bibili ako ng bigas, sardinas, at sabon"
    Output: ["RICE", "CANNED GOODS", "BATH SOAP"]
    
    USER INPUT TO PARSE: "{raw_input_string}"
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return []

def find_cheapest_and_alternatives(category_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT p.product_id, p.product_name, p.price, b.brand_name, c.category_name
    FROM products p
    LEFT JOIN brands b
        ON p.brand_id = b.brand_id
    JOIN categories c
        ON p.category_id = c.category_id
    WHERE c.category_name = %s
    ORDER BY p.price ASC;
    """

    cursor.execute(query, (category_name,))
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    if not products:
        return None
    
    for product in products:
        product['price'] = float(product['price'])

    return {
        "selected": products[0],
        "alternatives": products[1:]
    }

def get_nearby_stores(lat, lng):
    """
    Calls the Google Maps Places API with strict type filtering 
    to guarantee only retail food markets are returned.
    """
    api_key = os.getenv("MAPS_API_KEY")
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        "location": f"{lat},{lng}",
        "radius": 10000,
        "keyword": "grocery OR wet market OR palengke OR supermarket OR super market OR PUREGOLD OR Waltermart",
        "type": "store",
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        stores = []
        for place in data.get('results', [])[:5]:
            
            stores.append({
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "lat": place["geometry"]["location"]["lat"],
                "lng": place["geometry"]["location"]["lng"]
            })
        return stores
    except Exception as e:
        print(f"Maps API Error: {e}")
        return []

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "active", "message": "Sapat App Backend engine is running!"})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, user_password) VALUES (%s, %s, %s)",
            (username, email, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if user and check_password_hash(user['user_password'], password):
        return jsonify({
            "status": "success", 
            "message": "Login successful", 
            "user_id": user['user_id']
        }), 200
    else:
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

@app.route('/calculate', methods=['POST'])
def calculate_grocery_list():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        elderly = data.get("elderly_count", 0)
        adult = data.get("adult_count", 0)
        teen = data.get("teen_count", 0)
        children = data.get("children_count", 0)
        ration_days = data.get("ration_days", 0)
        budget = float(data.get('budget', 0.0))
        raw_items_array = data.get('raw_items', [])

        raw_input_string = ", ".join(raw_items_array)

        clean_categories = parse_raw_groceries(raw_input_string)

        final_receipt = []
        total_cost = 0.0

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO userinputs
            (user_id, elderly_count, adult_count, teen_count, children_count, budget, ration_days)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (user_id, elderly, adult, teen, children, budget,ration_days)
        )

        conn.commit()
        input_id = cursor.lastrowid

        total_portions_per_day = (adult * 1.0) + (teen * 1.0) + (elderly * 0.8) + (children * 0.5)

        total_multiplier = max(1, round(total_portions_per_day * (ration_days / 7)))

        non_food_categories = ["SHAMPOO", "HAIR CONDITIONER", "DETERGENT", "FABRIC CONDITIONER", "DISHWASHING", "TOOTHPASTE", "BATH SOAP", "BLEACH"]

        for category in clean_categories:
            result = find_cheapest_and_alternatives(category)

            if category in non_food_categories:
                calculated_qty = max(1, round(total_multiplier * 0.25)) 
            else:
                calculated_qty = total_multiplier

            if result:
                selected = result["selected"]
                item_subtotal = selected["price"] * calculated_qty

                cursor.execute(
                    """INSERT INTO grocery_list (input_id, product_id, quantity, unit_price, subtotal)
                    VALUES (%s,%s,%s,%s,%s)""", 
                    (input_id, selected["product_id"], calculated_qty, selected["price"], item_subtotal)
                )
                
                total_cost += float(item_subtotal)
                
                result["selected"]["calculated_qty"] = calculated_qty
                result["selected"]["subtotal"] = item_subtotal
                final_receipt.append(result)

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "original_budget": budget,
            "total_cost": total_cost,
            "remaining_balance": budget - total_cost,
            "receipt": final_receipt
        }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
@app.route('/nearby-stores', methods=['POST'])
def nearby_stores():
    try:
        data = request.get_json()
        lat = data.get('lat')
        lng = data.get('lng')

        if not lat or not lng:
            return jsonify({"status": "error", "message": "Missing coordinates"}), 400

        stores = get_nearby_stores(lat, lng)

        return jsonify({
            "status": "success",
            "stores": stores
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)