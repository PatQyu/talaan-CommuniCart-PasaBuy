import os
import json
import requests
from db_config import get_db_connection
from flask import Flask, request, jsonify
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def parse_raw_groceries(raw_input_string):
    """Uses Gemini to clean and categorize messy user inputs."""
    client = genai.Client()
    prompt = f"""
    Map the following user input ONLY to these exact database categories:
    - Rice, Chicken, Pork, Canned Goods, Instant Noodles, Bath Soap, Shampoo.
    Return ONLY a valid JSON array of strings. No markdown.
    User Input: "{raw_input_string}"
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
    conn = get_db_connection() # Connect to the database
    cursor = conn.cursor(dictionary=True)

    # Query to find the cheapest product and alternatives
    query = """
    SELECT p.product_id, p.product_name, p.general_name, p.price, b.brand_name, c.category_name
    FROM products p
    JOIN brands b
        ON p.brand_id = b.brand_id
    JOIN categories c
        ON p.category_id = c.category_id
    WHERE p.general_name = %s
    ORDER BY p.price ASC;
    """

    cursor.execute(query, (category_name,))
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    if not products:
        return None

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
        "radius": 5000,
        "keyword": "grocery OR wet market OR palengke",
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

@app.route('/calculate', methods=['POST'])
def calculate_grocery_list():
    try:
        data = request.get_json()
        # Extract user inputs
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

        # Insert user input data into the database
        cursor.execute(
            """INSERT INTO userinputs
            (user_id, elderly_count, adult_count, teen_count, children_count, budget, ration_days)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (user_id, elderly, adult, teen, children, budget,ration_days)
        )

        conn.commit()
        input_id = cursor.lastrowid

        for category in clean_categories:
            result = find_cheapest_and_alternatives(category)

            # If a product is found, insert it into the grocery_list table
            if result:
                selected = result["selected"]

                cursor.execute(
                """INSERT INTO grocery_list (input_id, product_id, quantity, unit_price, subtotal)
                VALUES (%s,%s,%s,%s,%s)""", (input_id, selected["product_id"], 1, selected["price"], selected["price"] )
                )
            if result:
                item_cost = result['selected']['price']
                total_cost += item_cost
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