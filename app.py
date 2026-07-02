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
    - Return a pure JSON array of objects.
    - Each object must have "category" (from the allowed list) and "preference" (the specific brand/type requested, or null if general).
    - Ignore items that don't fit allowed categories.

    EXAMPLES:
    Input: "bibili ako ng bigas, dalawang maling, at pancit canton"
    Output: [
        {{"category": "RICE", "preference": null}},
        {{"category": "CANNED GOODS", "preference": "maling"}},
        {{"category": "NOODLES & PASTA", "preference": "pancit canton"}}
    ]
    
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

def fetch_candidate_products(categories):
    """Fetches all available products for the requested categories to feed to the AI."""
    if not categories:
        return []
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    format_strings = ','.join(['%s'] * len(categories))
    
    query = f"""
    SELECT p.product_id, p.product_name, p.price, p.unit, p.unit_per_qty, b.brand_name, c.category_name
    FROM products p
    LEFT JOIN brands b ON p.brand_id = b.brand_id
    JOIN categories c ON p.category_id = c.category_id
    WHERE c.category_name IN ({format_strings})
    """
    
    cursor.execute(query, tuple(categories))
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    for p in products:
        p['price'] = float(p['price'])
        p['unit_per_qty'] = float(p['unit_per_qty'])
        
    return products

def optimize_receipt_with_ai(user_data, available_products, user_preferences):
    """Phase 2 AI: Determines optimal quantities while respecting specific brand/item requests."""
    client = genai.Client()
    
    prompt = f"""
    You are an expert budget planner. Calculate the optimal grocery list for this household.

    HOUSEHOLD DEMOGRAPHICS & BUDGET:
    - Budget: PHP {user_data['budget']}
    - Days to ration: {user_data['ration_days']}
    - Adults: {user_data['adult']}, Elderly: {user_data['elderly']}, Teens: {user_data['teen']}, Children: {user_data['children']}

    USER PREFERENCES (Prioritize these specific items if they exist!):
    {json.dumps(user_preferences)}

    AVAILABLE PRODUCTS (JSON):
    {json.dumps(available_products)}

    RULES:
    1. Select EXACTLY ONE product for each category requested.
    2. TARGET MATCHING: Look at the USER PREFERENCES. If a preference is listed (e.g., "maling", "tuna"), you MUST prioritize picking a product whose name matches that preference, provided it fits the budget.
    3. Determine the "calculated_qty" (an integer) needed to feed this household for the requested ration days based on unit_per_qty.
    4. Stay within the budget!
    5. Return ONLY a pure JSON array of objects with "product_id" and "calculated_qty". No markdown.

    EXAMPLE OUTPUT:
    [
        {{"product_id": 14, "calculated_qty": 3}},
        {{"product_id": 2, "calculated_qty": 5}}
    ]
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini Optimization Error: {e}")
        return []

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
        
        user_data = {
            "user_id": data.get("user_id"),
            "elderly": data.get("elderly_count", 0),
            "adult": data.get("adult_count", 0),
            "teen": data.get("teen_count", 0),
            "children": data.get("children_count", 0),
            "ration_days": data.get("ration_days", 0),
            "budget": float(data.get('budget', 0.0))
        }

        raw_input_string = data.get('raw_text', "")
        
        if not raw_input_string:
            raw_items_array = data.get('raw_items', [])
            raw_input_string = ", ".join(raw_items_array)

        parsed_items = parse_raw_groceries(raw_input_string)
        
        if not parsed_items:
            return jsonify({"status": "error", "message": "Could not identify valid categories."}), 400

        clean_categories = [item.get('category') for item in parsed_items if item.get('category')]
        
        clean_categories = list(set(clean_categories)) 

        candidate_products = fetch_candidate_products(clean_categories)
        
        ai_receipt_decisions = optimize_receipt_with_ai(user_data, candidate_products, parsed_items)

        final_receipt = []
        total_cost = 0.0
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO userinputs
            (user_id, elderly_count, adult_count, teen_count, children_count, budget, ration_days)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (user_data['user_id'], user_data['elderly'], user_data['adult'], user_data['teen'], user_data['children'], user_data['budget'], user_data['ration_days'])
        )
        conn.commit()
        input_id = cursor.lastrowid

        for decision in ai_receipt_decisions:
            chosen_id = decision.get("product_id")
            calc_qty = decision.get("calculated_qty", 1)
            
            selected_product = next((p for p in candidate_products if p["product_id"] == chosen_id), None)
            
            if selected_product:
                item_subtotal = float(selected_product["price"]) * calc_qty
                total_cost += item_subtotal
                
                cursor.execute(
                    """INSERT INTO grocery_list (input_id, product_id, quantity, unit_price, subtotal)
                    VALUES (%s,%s,%s,%s,%s)""", 
                    (input_id, chosen_id, calc_qty, selected_product["price"], item_subtotal)
                )

                category_of_chosen = selected_product["category_name"]
                
                alternatives = [
                    {
                        "product_id": p["product_id"],
                        "product_name": p["product_name"],
                        "brand_name": p.get("brand_name", "Local"),
                        "price": p["price"],
                        "unit": p["unit"],
                        "unit_per_qty": p["unit_per_qty"]
                    }
                    for p in candidate_products 
                    if p["category_name"] == category_of_chosen and p["product_id"] != chosen_id
                ]

                alternatives = sorted(alternatives, key=lambda x: x["price"])
                
                final_receipt.append({
                    "product_id": chosen_id,
                    "product_name": selected_product["product_name"],
                    "brand_name": selected_product.get("brand_name", "Local"),
                    "category_name": selected_product["category_name"],
                    "unit": selected_product["unit"],
                    "unit_per_qty": selected_product["unit_per_qty"],
                    "price": selected_product["price"],
                    "calculated_qty": calc_qty,
                    "subtotal": round(item_subtotal, 2),
                    "alternatives": alternatives
                })

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "original_budget": user_data['budget'],
            "total_cost": round(total_cost, 2),
            "remaining_balance": round(user_data['budget'] - total_cost, 2),
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