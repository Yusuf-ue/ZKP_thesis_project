from flask import Flask, jsonify, request
from random import randrange
import requests
import subprocess
import json
import time

# Create a Flask app
app = Flask(__name__)

# A simple in-memory store for products (could be replaced with a database in a real app)
products_db = []
proof_store = {}       # maps product_id -> proof

@app.route('/')
def home():
    return "Welcome to the Manufacturer API!"

@app.route('/compute', methods=['POST'])
def compute():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input provided"}), 400
    # Assign an ID if it's a new product
    product_id = len(products_db) + 1
    data["id"] = product_id 
    
    try:
        result = subprocess.run(
            ["../zkp/target/release/host"],
            input=json.dumps(data),
            capture_output=True,
            text=True,
            check=True
        )
        output = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Rust host failed", "details": e.stderr}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON from Rust host", "raw": result.stdout}), 500

    product = output.get("product", {})
    proof = output.get("proof", "")

    # Save product + proof
    products_db.append({"product": {**product, "id": product_id}})
    proof_store[product_id] = proof
    
    
    product_obj = Product(
    name=product["name"],
    volume=product["volume"],
    )
    send_to_certify(product_obj)

    return jsonify(product)


@app.route('/proveRetrieval/<int:product_id>', methods=['GET'])
def prove_retrieval(product_id):
    proof = proof_store.get(product_id)
    if not proof:
        return jsonify({"error": "Proof not found"}), 404
    return jsonify({"product_id": product_id, "proof": proof})

@app.route('/info', methods=['GET'])
def info():
    return "Workflow Position: 1<br>This TCU functions as a manufacturer, generating products and sending them to the certifier."

@app.route('/display', methods=['GET'])
def display():

    # Return the list as JSON
    return jsonify(products_db)


def send_to_certify(product):
    """
    Send a certification request to the Flask API.
    """
    url = "http://127.0.0.1:5002/compute"
    try:
        response = requests.post(url, json=product.to_dict())
        if response.status_code == 200:
            data = response.json()
            print(f"Certification Successful: {data['message']}")
            print(f"Certified Product Data: {data['product']}")

        else:
            print(f"Failed to certify product: {response.status_code}")
    except requests.RequestException as e:
        print("Error connecting to certifier:", e)


class Product:
    _id_counter = 0  # class variable to track IDs

    def __init__(self, name, volume):
        Product._id_counter += 1
        self.id = Product._id_counter
        self.name = name
        self.volume = volume
        self.certified = False  # initially False, immutable for manufacturer
        self.sender = "Manufacturer A"  # initially set, immutable for manufacturer

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "volume": self.volume,
            "certified": self.certified,
            "sender": self.sender
        }


    # @property
    # def certified(self):
    #     # Manufacturer side: certified is read-only
    #     return self._certified
    
    # @property
    # def sender(self):
    #     # Manufacturer side: sender is read-only
    #     return self._sender

    def __repr__(self):
        return (f"Product(name='{self.name}', id={self.id}, volume={self.volume}, certified={self.certified}, sender='{self.sender}')")

# # Factory function
# def generate_product(name, volume):
#     product = Product(name, volume)
#     print(product)
#     return product

# if __name__ == "__main__":
#     # Example usage
#     generate_product(name="Product-X", volume=2)
#     generate_product(name="Product-Y", volume=5)
#     generate_product(name="Product-Z", volume=10)



if __name__ == '__main__':
    # Run the app on the local development server
    app.run(debug=True, port=5000)
    # newProduct=generate_product("käse", 2)
    # time.sleep(2.5)
    # send_to_certify(newProduct)