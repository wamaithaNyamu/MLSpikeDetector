from flask import Flask
import json
from datetime import datetime


local_model_path = "best.pt"
app = Flask(__name__)

def error_line(message):
    print(f'❌❌❌❌❌❌')
    print(message)


def get_prediction_status():
    # Define the file path
    file_path = 'data.json'
    try:
        # Read the existing JSON data
        with open(file_path, 'r') as file:
            data = json.load(file)

    except FileNotFoundError:
        # If the file doesn't exist, return "Not ready"
        print("get_prediction_status")
        return "Not ready"

    # Check if there are any predictions in the data
    if data:
        latest_prediction_time_str = data.get('prediction_time')
        latest_prediction_str = data.get('prediction')
        if latest_prediction_time_str and latest_prediction_str:
            # Convert prediction time string to datetime object
            latest_prediction_time = datetime.strptime(latest_prediction_time_str, "%Y-%m-%d %H:%M:%S")
            # Compare the prediction time with the current time
            current_time = datetime.now()
            if current_time < latest_prediction_time:
                # If the current time is greater than the prediction time, return the prediction
                return latest_prediction_str
            else:
                # If the current time is not greater than the prediction time, return "Not ready"
                print(1)
                return "Not ready"
        else:
            # If prediction data is incomplete, return "Not ready"
            print(2)
            return "Not ready"
    else:
        # If there are no predictions in the data, return "Not ready"
        print(3)
        return "Not ready"



@app.route("/predict", methods = ['GET'])
def read_prediction():
    """
    This function reads the prediction from data.json and returns the prediction as a response
    """
    try:       
        prediction = get_prediction_status()
        print("The prediction is ",prediction)
        return prediction
    except Exception as e:
        error_line(e)
        print("read_prediction")
        return None

if __name__ == '__main__':
    app.run(debug=True)


