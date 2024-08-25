from flask import Flask, jsonify, request
import Robot as R

app = Flask(__name__)
robot = None  # robot instance that will be used to execute code


@app.route('/')
def home():
    """
    Sending test response to check connection to flask server
    """
    response = {
        "status": 200,
        'info': 'Connection is OK.'
    }
    return jsonify(response)


@app.route('/init-robot', methods=['POST'])
def init_robot():
    """
    Accept POST requests only.
    Trying to establish connection between flask server and a robot.
    """

    # Check if data are in json format
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

    print ">>>>>>", ip, port, name

    # Try to establish a connection to the robot
    try:
        robot = R
        # robot = R.Robot(ip, port, name)
    except Exception as e:
        print "There was an error while connecting to the robot."
        print "Error was:", e
        response = {
            "status": 404,
            "error": "Error while connecting to the robot."
        }
        return jsonify(response)

    # Return OK message if connection is successful
    response = {
        "status": 200,
        "info": "Connection between IDE and robot was established."
    }
    return jsonify(response)


@app.route('/execute', methods=["POST"])
def execute():
    """
    Accept POST request only.
    Trying to execute python2 code that was received from request.
    """

    global robot
    # Check if there is a connection to the robot
    if (not robot):
        response = {
            "status": 404,
            "error": "There is no connection to robot."
        }
        return jsonify(response)

    # Check data type from request
    if (not request.is_json):
        response = {
            "status": 404,
            "error": "Data must be in JSON format."
        }
        return jsonify(response)

    robot_data = request.get_json()
    code = robot_data.get("code")
    print ">>>>>", code, '\n'

    # Check if 'code' is not empty
    if (code):
        # Try to execute the code
        try:
            exec(code)
            response = {
                "status": 200,
                "info": "Code executing run successfully!"
            }
        except Exception as e:
            print "There was an error while executing the code."
            print "Error was:", e
            response = {
                "status": 404,
                "error": "Error while executing the code: " + e.message
            }
    else:
        # If 'code' parameter was empty
        response = {
            "status": 404,
            "error": "The parameter 'code' is empty"
        }

    return jsonify(response)



if (__name__ == '__main__'):
    app.run(host='localhost', port=5000)
