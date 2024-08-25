from flask import Flask, jsonify, request
import Robot as R

app = Flask(__name__)
robot = None


@app.route('/')
def home():
    response = {
        "status": 200,
        'info': 'Connection is OK.'
    }
    return jsonify(response)


@app.route('/init-robot', methods=['POST'])
def init_robot():
    if (not request.is_json):
        response = {
            "status": 404,
            "error": "Data must be in JSON format."
        }
        return jsonify(response)

    global robot
    robot_data = request.get_json()

    ip = robot_data.get("ip")
    port = robot_data.get("port")
    name = robot_data.get("name")

    print ip, port, name
    # robot = R.Robot(r_id, r_port, r_name)

    response = {
        "status": 200,
        "info": "Connection between IDE and robot was established."
    }
    return jsonify(response)


if (__name__ == '__main__'):
    app.run(host='localhost', port=5000)
