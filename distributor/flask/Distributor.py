from flask import Flask, jsonify, request
from random import randrange
import requests
import time

# Create a Flask app
app = Flask(__name__)

# A simple in-memory store for products (could be replaced with a database in a real app)
JSON_db = []
retailers_db = dict()

# Memory for retailers (there can be multiple)
retailer_registry = set()

@app.route('/register', methods=['POST'])
def register_retailer():
    data = request.json
    retailer_url = data.get('url')
    if not retailer_url:
        return jsonify({"error": "Missing retailer URL"}), 400

    retailer_registry.add(retailer_url)
    return jsonify({"message": f"Retailer {retailer_url} registered successfully."})

@app.route('/unregister', methods=['POST'])
def unregister_retailer():
    data = request.json
    retailer_url = data.get('url')
    if not retailer_url:
        return jsonify({"error": "Missing retailer URL"}), 400

    if retailer_url in retailer_registry:
        retailer_registry.remove(retailer_url)
        return jsonify({"message": f"Retailer {retailer_url} unregistered successfully."})
    else:
        return jsonify({"error": f"Retailer {retailer_url} not found."}), 404
    

@app.route('/retailers', methods=['GET'])
def get_retailers():
    return jsonify(list(retailer_registry))

@app.route('/')
def home():
    return "Welcome to the Distributor API!"

@app.route('/compute', methods=['POST'])
def compute():
    product_data = request.json   

    # JSON_db.append(product_data)
    JSON_db.append({
        "product": product_data.get("product"),
        "proof": product_data.get("proof")
    })
    # Define the URL where you want to forward the request
    for url in retailer_registry:
        try:
            resp = requests.post(f"{url}/compute", json=product_data, timeout=3)
            print(f"Sent to {url}: {resp.status_code}")
        except Exception as e:
            print(f"Failed to send to {url}: {e}")
    
    # Return the response from the forwarded request
    # return jsonify({
    #     "status": response.status_code,
    #     "response": response.json()
    # })

@app.route('/proofRetrieval', methods=['GET'])
def proofRetrieval():
    return "TODO /proofRetrieval"

@app.route('/info', methods=['GET'])
def info():
    return "Workflow Position: 3<br>This TCU functions as a distributor, forwarding successfully certified products from the certifier to the retailer."

@app.route('/display', methods=['GET'])
def display():
    # # Convert each product in products_db to a dictionary using the to_dict method
    # products_list = [product.to_dict() for product in JSON_db]
    
    # Return the list as JSON
    #return JSON_db
    return jsonify(JSON_db)


# later for having multiple retailers
# @app.route('/addRetailer', methods=['POST'])
# def addRetailer():
#     retailer_data = request.json
#     name = retailer_data['name']
#     port = retailer_data['port']
#     retailers_db[name] = port



# def send_to_retailer(product_data):
#     """
#     Send a certification request to the Flask API.
#     """
#     url = "http://127.0.0.1:5006/compute"
#     try:
#         response = requests.post(url, json=product.to_dict())
#         if response.status_code == 200:
#             data = response.json()
#             print(f"Certification Successful: {data['message']}")
#             print(f"Certified Product Data: {data['product']}")
#         elif response.status_code == 404:
#             print("Product not found in the certifier's database!")
#         else:
#             print(f"Failed to certify product: {response.status_code}")
#     except requests.RequestException as e:
#         print("Error connecting to certifier:", e)


if __name__ == '__main__':
    # Run the app on the local development server
    app.run(debug=True, port=5004, use_reloader=False)