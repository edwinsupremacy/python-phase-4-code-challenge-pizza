from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([{"address": restaurant.address, "id": restaurant.id, "name": restaurant.name} for restaurant in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    return jsonify({
        "address": restaurant.address,
        "id": restaurant.id,
        "name": restaurant.name,
        "restaurant_pizzas": [
            {
                "id": restaurant_pizza.id,
                "pizza_id": restaurant_pizza.pizza_id,
                "price": restaurant_pizza.price,
                "restaurant_id": restaurant_pizza.restaurant_id,
                "pizza": {
                    "id": restaurant_pizza.pizza.id,
                    "name": restaurant_pizza.pizza.name,
                    "ingredients": restaurant_pizza.pizza.ingredients
                }
            } for restaurant_pizza in restaurant.restaurant_pizzas
        ]
    })

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404
    else:   
       for restaurantpizza in restaurant.restaurant_pizzas:
        db.session.delete(restaurantpizza)
    db.session.delete(restaurant)
    db.session.commit()
    return '', 204

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([{"id": pizza.id, "ingredients": pizza.ingredients, "name": pizza.name} for pizza in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def post_restaurant_pizza():
    data = request.get_json()
    if not data or "price" not in data or "pizza_id" not in data or "restaurant_id" not in data:
        return jsonify({"error": "Missing data"}), 400

    if not (1 <= data["price"] <= 30):
        return jsonify({"error": "Price must be between 1 and 30"}), 400

    pizza = Pizza.query.get(data["pizza_id"])
    restaurant = Restaurant.query.get(data["restaurant_id"])

    if not pizza:
        return jsonify({"error": "Pizza not found"}), 404
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    restaurant_pizza = RestaurantPizza(price=data["price"], pizza_id=data["pizza_id"], restaurant_id=data["restaurant_id"])

    db.session.add(restaurant_pizza)
    db.session.commit()

    response = {
        "id": restaurant_pizza.id,
        "pizza": {
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name
        },
        "pizza_id": pizza.id,
        "price": restaurant_pizza.price,
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        },
        "restaurant_id": restaurant.id
    }

    return jsonify(response), 201

@app.route('/restaurants')
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([{"address":restaurant.address,"id":restaurant.id,"name":restaurant.name}for restaurant in restaurants])


@app.route('/restaurants/<int:id>')
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({'error':'Resturant not found'}),404
    else:
        restaurants_exists = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name,
            "restaurant_pizzas": [
                {
                    "id": restaurant_pizza.id,
                    "pizza_id": restaurant_pizza.pizza_id,
                    "price": restaurant_pizza.price,
                    "restaurant_id": restaurant_pizza.restaurant_id,
                    "pizza": {
                        "id": restaurant_pizza.pizza.id,
                        "name": restaurant_pizza.pizza.name,
                        "ingredients": restaurant_pizza.pizza.ingredients
                    }
                } for restaurant_pizza in restaurant.restaurant_pizzas
            ]
        }
    return jsonify(restaurants_exists)

@app.route('/restaurants/<int:id>',methods=['DELETE'])
def delete_restaurant(id):
    restaurants=Restaurant.query.get(id)

    if not restaurants:
        return jsonify({"error":"Restaurant not found"}), 404
    
    else:
        db.session.delete(restaurants)

        if restaurants.restaurant_pizzas:
            for restaurant_pizza in restaurants.restaurant_pizzas:
                 db.session.delete(restaurant_pizza)

        db.session.commit()
        return jsonify({}), 204
        

@app.route('/pizzas')
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([{"id":pizza.id,"ingredients":pizza.ingredients,"name":pizza.name}for pizza in pizzas])


@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    restaurant_pizza = RestaurantPizza(price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"]
        )
    db.session.add(restaurant_pizza)
    db.session.commit()
    return jsonify(restaurant_pizza.to_dict()), 201
    


if __name__ == "__main__":
    app.run(port=5555, debug=True)
