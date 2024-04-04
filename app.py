import redis
from flask import Flask, jsonify, request

app = Flask(__name__)

# Conexión a la instancia local de Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

users = [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Jane"}
]


# Endpoint para obtener todos los usuarios (GET) con caché
@app.route('/users', methods=['GET'])
def get_users():
    cached_users = redis_client.get('users')
    if cached_users:
        return jsonify(eval(cached_users))
    else:
        users = [
            {"id": 1, "name": "John"},
            {"id": 2, "name": "Jane"}
        ]
        redis_client.set('users', str(users))
        return jsonify(users)

# Endpoint para agregar un nuevo usuario (POST) con invalidación de caché
@app.route('/users', methods=['POST'])
def add_user():
    new_user = request.json
    users = eval(redis_client.get('users'))
    users.append(new_user)
    redis_client.set('users', str(users))
    return jsonify({"message": "User added successfully"})

# Endpoint para actualizar un usuario existente (PUT) con invalidación de caché
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    users = eval(redis_client.get('users'))
    for user in users:
        if user['id'] == user_id:
            user.update(request.json)
            redis_client.set('users', str(users))
            return jsonify({"message": "User updated successfully"})
    return jsonify({"message": "User not found"}), 404

# Endpoint para eliminar un usuario existente (DELETE) con invalidación de caché
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    users = eval(redis_client.get('users'))
    for user in users:
        if user['id'] == user_id:
            users.remove(user)
            redis_client.set('users', str(users))
            return jsonify({"message": "User deleted successfully"})
    return jsonify({"message": "User not found"}), 404

if __name__ == '__main__':
    app.run()
