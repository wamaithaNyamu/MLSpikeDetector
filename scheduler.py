import sched
import sys
import time
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
from save_data import authenticate_to_mt5,create_folder, wamaitha_account, wamaitha_password, wamaitha_server
# from make_predictions import load_model, local_model_path
import json
import cv2
from datetime import datetime,timedelta
import numpy as np
from ultralyticsplus import YOLO,render_result

# symbol='Crash 1000 Index'
bars = 300
images_folder_for_symbol=f'LIVEDATA'
local_model_path = "best.pt"
symbol =''
time_schedule = 0

scheduler = sched.scheduler(time.time, time.sleep)
def load_model(model_path):
    """
    Loads the  model for use in our project
    @returns model
    """
    try:
        print('Loading model ...')
        model = YOLO(model_path)
        # set model parameters
        model.overrides['conf'] = 0.25  # NMS confidence threshold
        model.overrides['iou'] = 0.45  # NMS IoU threshold
        model.overrides['agnostic_nms'] = False  # NMS class-agnostic
        model.overrides['max_det'] = 5  # maximum number of detections per image
        return model
    except Exception as e:
        error_line(e)



def error_line(message):
    print(f'❌❌❌❌❌❌')
    print(message)


def get_prediction(model,df,bars,images_folder=images_folder_for_symbol):
    """"
    Use the data retreived from the live data, draw the bars on a graph, then save the file to the images folder.
    
    @params model: The YOLO model to be used for prediction
    @params df: The YOLO model to be used for prediction
    @params bars: The YOLO model to be used for prediction
    @params images_folder: The YOLO model to be used for prediction
    """  
    try:

        height = 500
        width = 500        
        # Normalise high and low
        columns_to_normalize = ['high','low']
        # Min-Max scaling only on selected columns
        df[columns_to_normalize] = (df[columns_to_normalize] - df[columns_to_normalize].min()) / (df[columns_to_normalize].max() - df[columns_to_normalize].min())
        normalized_high_values = df['high'].values
        normalized_low_values = df['low'].values
        print("Normalized high ", normalized_high_values[0])
        # Calculate scaling factors for the 'High' and 'Low' values
        scaled_high_values = (normalized_high_values * (height-20)).astype(np.float32)
        scaled_low_values = (normalized_low_values * (height-20)).astype(np.float32)
        # Scale the values to fit within the image height
        scaling_factor = 0.9 # Adjust as needed to fit the graph within the image
        scaled_high_values *= scaling_factor
        scaled_low_values *= scaling_factor
        print("Scaled high values ",scaled_high_values[0])
        start_candle, end_candle = 0, bars
        graph = np.zeros((height, width, 3), dtype=np.uint8)
        graph.fill(255)  # Fill with white
        x = 1 # starting x coordinate
        thickness = 3 # thickness of the lines
        candle_width = 2  # Adjust the candlestick width as needed

        # plot each point 
        for i in range(start_candle,end_candle): 
            # Calculate rectangle coordinates for the high and low values
            high_y1 = height - 20 - int(scaled_high_values[i - 1])
            high_y2 = height - 20 - int(scaled_high_values[i])
            low_y1 = height - 20 - int(scaled_low_values[i - 1])
            low_y2 = height - 20 - int(scaled_low_values[i])
            # Determine the minimum and maximum y-coordinates for the rectangle
            y_min = min(high_y1, high_y2, low_y1, low_y2)
            y_max = max(high_y1, high_y2, low_y1, low_y2)
            # Determine if the candlestick is bullish or bearish
            if df['open'][i] <  df['close'][i]:
                color = (0, 0, 255)  # Bullish (red but using blue)
            else:
                color = (0, 255, 0)  # Bearish (green)
            # Draw rectangle for the candlestick (in red for high values, green for low values)
            cv2.rectangle(graph, (x - candle_width // 2, y_min), (x + candle_width // 2, y_max), color, thickness) 
            x += 1

        results = model.predict(graph, verbose=False)
        current_preds = []
        for result in results:
            print("********************************")
            for box in result.boxes:
                print("********************************")
                class_id = int(box.data[0][-1])
                print("Class ",model.names[class_id])
                current_preds.append(model.names[class_id])
        print(f'The current boxes for this chart are {current_preds} with the last prediction being {current_preds[0]}')
        render = render_result(model=model, image=graph, result=results[0])
        # Assuming 'render' contains the PIL Image returned by render_result
        render_np = np.array(render)  # Convert PIL Image to numpy array
        # Convert RGB to BGR (OpenCV uses BGR color order)
        render_np = cv2.cvtColor(render_np, cv2.COLOR_RGB2BGR)
        # Create the file name with sequency number
        filename = "graph.jpg"
        # Figure out the local path
        output_path = f'./{images_folder}/{filename}'
        # Save your sample
        cv2.imwrite(output_path, render_np)
        # Increment counters
        start_candle, end_candle = start_candle + 1, end_candle + 1

        return current_preds[0]
    except Exception as e:
        print("get_prediction")
        error_line(e)



def get_data(symbol):
    """
    @param symbol: The asset we need to get the data from
    @return df: Pandas dataframe
    """
    try:
        timeframe = mt5.TIMEFRAME_M1
        raw_data_from_mt5 = mt5.copy_rates_from_pos(str(symbol),timeframe, 0 , bars)
        df = pd.DataFrame(raw_data_from_mt5)
        return df
   
    except Exception as e:
        print("get_data")
        error_line(e) 



def update_json_file(prediction):
    """
    @params prediction: the prediction to write to the file
    """
    try:
        file_path = 'data.json'
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {} # If the file doesn't exist, create an empty dictionary
        # Update the data with new values
        prediction_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        data['prediction_time'] = prediction_time  # Renaming 'current_time' to 'prediction_time'
        data['prediction'] = prediction

        # Write the updated data back to the JSON file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    except Exception as e:
         print("update_json_file")
         error_line(e) 



def make_prediction():
    """
    This function authenticates to MT5 , loads the YOLO model, gets the data from mt5 and makes a prediction.The prediction is written to a file for later use.
    """
    try:
      
        print("Making prediction")
        authenticate_to_mt5(wamaitha_account,wamaitha_password,wamaitha_server)
        model = load_model(local_model_path)
        df = get_data(symbol)
        prediction = get_prediction(model,df,bars)
        print("Prediction is ",prediction)
        update_json_file(prediction)
 
    except Exception as e:
         print("make_prediction")
         error_line(e) 



def repeat_task():
    """
    Schedules the make_prediction() function to run every {time_schedule}
    
    """
    try:
        print("Time schedule ",time_schedule)
        scheduler.enter(time_schedule, 1, make_prediction, ())
        scheduler.enter(time_schedule, 1, repeat_task, ())
    except Exception as e:
         print("repeat_task")
         error_line(e) 

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    print(sys.argv, " -  ",len(sys.argv))
    if len(sys.argv) <= 2:
        print('Exiting!')
        sys.exit(1)
    # Extract arguments from command line
    time_schedule = int(sys.argv[1]) * 60 * 60
    symbol = str(sys.argv[2])
    print("The time is ",time_schedule, " for the ",symbol)
    make_prediction()
    repeat_task()
    scheduler.run()


