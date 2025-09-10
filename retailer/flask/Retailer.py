from flask import Flask, jsonify, request
from random import randrange
import requests
import time
import os
import atexit


# Create a Flask app
app = Flask(__name__)

# A simple in-memory store for products (could be replaced with a database in a real app)
products_db = []

distributor_url = os.getenv('DISTRIBUTOR_URL', 'http://localhost:5004')
retailer_url = os.getenv('RETAILER_URL', 'http://localhost:5006')

def register_with_distributor():
    try:
        resp = requests.post(f"{distributor_url}/register", json={"url": retailer_url})
        print("Registration response:", resp.json())
    except Exception as e:
        print("Failed to register retailer:", e)

@app.route('/unregister')
def unregister_from_distributor():
    try:
        resp = requests.post(f"{distributor_url}/unregister", json={"url": retailer_url})
        print("Unregistration response:", resp.json())
    except Exception as e:
        print("Failed to unregister retailer:", e)

atexit.register(unregister_from_distributor)

@app.route('/')
def home():
    return "Welcome to the Retailer API!"

@app.route('/compute', methods=['POST'])
def compute():
    # Check if the product exists in our "database"
    # product = products_db.get(product_id)
    product_data = request.json
    
    product = Product(
        id=product_data['id'],
        name=product_data['name'],
        volume=product_data['volume'],
        certified=product_data['certified'],
        sender=product_data.get('sender')
    )

    if not product:
        return jsonify({"error": "Product not found!"}), 404

    products_db.append(product)

    return jsonify({
        "message": "Product certified successfully",
        "product": product.to_dict()
    })

@app.route('/proofRetrieval', methods=['GET'])
def proofRetrieval():
    # Simulate creating a product
    return "TODO /proofRetrieval"

@app.route('/info', methods=['GET'])
def info():
    # Simulate creating a product
    return "Workflow Position: 4<br>This TCU functions as a retailer, storing the certified products from the distributor."

@app.route('/display', methods=['GET'])
def display():
    # Convert each product in products_db to a dictionary using the to_dict method
    products_list = [product.to_dict() for product in products_db]
    
    # Return the list as JSON
    return jsonify(products_list)


class Product:
    def __init__(self, id, name, volume, certified, sender):
        self.id = id
        self.name = name  
        self.volume = volume
        self.certified = certified
        self.sender = sender  # initially set, immutable for manufacturer
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "volume": self.volume,
            "certified": self.certified,
            "sender": self.sender
        }

    # @property
    # def sender(self):
    #     return self._sender
    

    def __repr__(self):
        return (f"Product(name='{self.name}', id={self.id}, volume={self.volume}, certified={self.certified}, sender='{self.sender}')")

# Factory function
def generate_product(name, volume):
    product = Product(name, volume)
    print(product)
    return product


if __name__ == '__main__':
    # Run the app on the local development server
    register_with_distributor()
    app.run(debug=True, port=int(os.getenv('PORT', 5006)), use_reloader=False)