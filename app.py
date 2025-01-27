from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_swagger_ui import get_swaggerui_blueprint
from flasgger import Swagger
import datetime

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)
app.config['SWAGGER'] = {
    'title': 'Flask API with JWT',
    'uiversion': 3
}

jwt = JWTManager(app)
Swagger(app)

# Mock database
users = {
    "testuser": {
        "password": "password123",
        "email": "testuser@example.com"
    }
}

items = [
    {"id": 1, "name": "Item1", "description": "Description of Item1"},
    {"id": 2, "name": "Item2", "description": "Description of Item2"}
]

# Endpoint to login and generate JWT
@app.route('/login', methods=['POST'])
def login():
    """
    Login to generate a JWT token
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Token generated successfully
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Invalid credentials
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users.get(username)
    if not user or user['password'] != password:
        return jsonify({"msg": "Invalid username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify({"access_token": access_token})

# Secured endpoint to get user details
@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    """
    Get user details of the logged-in user
    ---
    tags:
      - Users
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Bearer token
    responses:
      200:
        description: User details retrieved successfully
        schema:
          type: object
          properties:
            user:
              type: object
    """
    current_user = get_jwt_identity()
    user_info = users.get(current_user, {})
    return jsonify({"user": user_info})

# Secured endpoint to get all items
@app.route('/items', methods=['GET'])
@jwt_required()
def get_items():
    """
    Get all items
    ---
    tags:
      - Items
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Bearer token
    responses:
      200:
        description: List of items
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                type: object
    """
    return jsonify({"items": items})

# Secured endpoint to create a new item
@app.route('/items', methods=['POST'])
@jwt_required()
def create_item():
    """
    Create a new item
    ---
    tags:
      - Items
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Bearer token
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      201:
        description: Item created successfully
        schema:
          type: object
          properties:
            msg:
              type: string
            item:
              type: object
    """
    data = request.json
    new_item = {
        "id": len(items) + 1,
        "name": data.get('name'),
        "description": data.get('description')
    }
    items.append(new_item)
    return jsonify({"msg": "Item created", "item": new_item}), 201

# Secured endpoint to update an item
@app.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    """
    Update an item
    ---
    tags:
      - Items
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Bearer token
      - name: item_id
        in: path
        required: true
        type: integer
        description: ID of the item to update
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      200:
        description: Item updated successfully
        schema:
          type: object
          properties:
            msg:
              type: string
            item:
              type: object
      404:
        description: Item not found
    """
    data = request.json
    item = next((item for item in items if item["id"] == item_id), None)
    if not item:
        return jsonify({"msg": "Item not found"}), 404

    item.update({
        "name": data.get('name', item['name']),
        "description": data.get('description', item['description'])
    })
    return jsonify({"msg": "Item updated", "item": item})

# Secured endpoint to delete an item
@app.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    """
    Delete an item
    ---
    tags:
      - Items
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Bearer token
      - name: item_id
        in: path
        required: true
        type: integer
        description: ID of the item to delete
    responses:
      200:
        description: Item deleted successfully
        schema:
          type: object
          properties:
            msg:
              type: string
    """
    global items
    items = [item for item in items if item["id"] != item_id]
    return jsonify({"msg": "Item deleted"})

# Secured endpoint to get a single item by ID
@app.route('/items/<int:item_id>', methods=['GET'])
@jwt_required()
def get_item_by_id(item_id):
    """
    Get an item by ID
    ---
    tags:
      - Items
    parameters:
      - name: Authorization
        in: header
        required: true
        type: string
        description: Bearer token
      - name: item_id
        in: path
        required: true
        type: integer
        description: ID of the item to retrieve
    responses:
      200:
        description: Item retrieved successfully
        schema:
          type: object
          properties:
            item:
              type: object
      404:
        description: Item not found
    """
    item = next((item for item in items if item["id"] == item_id), None)
    if not item:
        return jsonify({"msg": "Item not found"}), 404
    return jsonify({"item": item})

if __name__ == '__main__':
    app.run(debug=True)
