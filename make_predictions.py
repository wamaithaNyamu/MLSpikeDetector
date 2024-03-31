from ultralyticsplus import YOLO,render_result
import pandas as pd
import numpy as np
from save_data import create_folder,start_date_formatted,end_date_formatted,symbol_without_spaces
import cv2
from ta.trend import EMAIndicator
import sys

local_model_path = "best.pt"
csv_path_for_symbol="./DATA/Crash1000Index/Crash1000Index-2022-01-01-2024-01-01-5.csv"
images_folder_for_symbol=f'IMAGES/{symbol_without_spaces}-{start_date_formatted}-{end_date_formatted}'

def error_line(message):
    print(f'❌❌❌❌❌❌')
    print(message)


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

def backtest(predictions, close_prices, actual_outcome,EMA_values):
    """
    Backtests the predictions against the actual classes.
    @params predictions: Predicted class IDs ( "down",  "up").
    @params close_prices: Close prices corresponding to each prediction.
    @params actual_classes : Actual class prices of the actual close that happened
    @params EMA_values: values of the 200 EMA 
    @returns win_loss_record : value of the percentage of won
                             
    """
    try:
        total = len(predictions)
        won_count=0
        won_count_with_ema = 0
        lost_count=0
        for prediction, close_price, the_actual_outcome ,EMA_value in zip(predictions, close_prices, actual_outcome,EMA_values):
            if prediction == "down"  :  # Predicted class is "down"
                if the_actual_outcome < close_price:
                    print("✅Won Down")
                    won_count = won_count + 1  # Correct prediction, won
                    if close_price < EMA_value:
                       won_count_with_ema += 1
                else:
                    print("❌Lost Down")
                    lost_count= lost_count + 1  # Incorrect prediction, lost
            elif prediction == "up" :  # Predicted class is "up"
                if the_actual_outcome > close_price:
                    print("✅Won Up")
                    won_count = won_count + 1 # Correct prediction, won
                    if close_price < EMA_value:
                       won_count_with_ema += 1
                else:
                    print("❌Lost Up")
                    lost_count= lost_count + 1  # Incorrect prediction, lost
        return [won_count / total * 100, won_count_with_ema/ total * 100]
    except Exception as e:
        error_line(e)

def calculate_MA(df):
    """"
    Get data from the csv  and draw  it 
    @params df: Data to be used
    @return df: The df with the indicators added
    """  
    try:
        indicator_EMA = EMAIndicator(close=df['close'],window=200)
        df['200EMA'] = indicator_EMA.ema_indicator()
        return df

    except Exception as e:
        error_line(e)

def append_to_txt(filename, text):
    try:
        # Open the file in append mode
        with open(filename, 'a') as file:
            # Write the text to the file
            file.write(text + '\n')
        print("Text appended successfully to", filename)
    except Exception as e:
        error_line(e)


def draw_data(csv_path,images_folder,model,tf,symbol):
    """"
    Get data from the csv  and draw  it 
    @params csv_path: Data to be used
    @params images_folder: The path to which we should save all the images
    @params model: The YOLO model to be used for prediction
    """  
    try:
        height = 500
        bars = 300
        width = 500        
        prediction = []
        prediction_close_price=[]
        actual_outcome =[]
        EMA_values=[]
        # create the folder
        create_folder(images_folder)
          # read csv
        df = pd.read_csv(csv_path)
        df = calculate_MA(df)
        print(df.head())
        print(df.tail())
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
        # scaling_factor = 0.9 # Adjust as needed to fit the graph within the image
        scaling_factor =1# Adjust as needed to fit the graph within the image
        scaled_high_values *= scaling_factor
        scaled_low_values *= scaling_factor
        print("Scaled high values ",scaled_high_values[0])

        start_candle, end_candle = 1, bars
        for chart_counter in range(1, len(df) - bars):
            graph = np.zeros((height, width, 3), dtype=np.uint8)
            graph.fill(255)  # Fill with white
            x = 1 # starting x coordinate
            thickness = 3 # thickness of the lines
            candle_width = 2  # Adjust the candlestick width as needed

            # plot each point 
            for i in range(start_candle,end_candle+1):
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
                for box in result.boxes:
                    class_id = int(box.data[0][-1])
                    print(model.names[class_id])
                    current_preds.append(model.names[class_id])
            if chart_counter+bars + 1 < len(df) and len(current_preds)>0 :
                prediction.append(current_preds[0])
                prediction_close_price.append(df['close'][chart_counter+bars])
                actual_outcome.append(df['close'][chart_counter+bars+1])
                EMA_values.append(df['200EMA'][chart_counter+bars])
            print(f'The current boxes for chart {chart_counter} are {current_preds}')
            render = render_result(model=model, image=graph, result=results[0])
            # Assuming 'render' contains the PIL Image returned by render_result
            render_np = np.array(render)  # Convert PIL Image to numpy array
            # Convert RGB to BGR (OpenCV uses BGR color order)
            render_np = cv2.cvtColor(render_np, cv2.COLOR_RGB2BGR)
            # Create the file name with sequency number
            filename = f"graph_{chart_counter}.jpg"
            # Figure out the local path
            output_path = f'./{images_folder}/{filename}'
            print(output_path)
            # Save your sample
            cv2.imwrite(output_path, render_np)
            # Increment counters
            start_candle, end_candle = start_candle + 1, end_candle + 1
        win_loss = backtest(prediction, prediction_close_price, actual_outcome,EMA_values)
        print("This model had a win loss of ", win_loss)
        txt = f'{symbol} {tf} {win_loss[0]} {win_loss[1]}'
        append_to_txt("backtest.txt",txt)
            
    except Exception as e:
        error_line(e)


csv_names=['./DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-1minute.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-2minutes.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-3minutes.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-4minutes.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-5minutes.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-6minutes.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-10minutes.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-12minutes.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-15minutes.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-20minutes.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-30minutes.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-1hour.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-2hours.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-3hours.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-4hours.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-6hours.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-8hours.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-12hours.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-1day.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-1week.csv', './DATA/Boom1000Index/Boom1000Index-2022-01-01-2024-01-01-1month.csv']

timeframe_full_names = [
            "1 minute", #0
            "2 minutes",#1
            "3 minutes",#2
            "4 minutes",#3
            "5 minutes",#4
            "6 minutes",#5
            "10 minutes",#6
            "12 minutes",#7
            "15 minutes",#8
            "20 minutes",#9
            "30 minutes",#10
            "1 hour",#11
            "2 hours",#12
            "3 hours",#13
            "4 hours",#14
            "6 hours",#15
            "8 hours",#16
            "12 hours",#17
            "1 day",#18
            "1 week",#19
            "1 month",#20
        ]


def make_predicitons(start_index):
    csv_name = csv_names[start_index]
    tf = timeframe_full_names[start_index]
    print(f'Now working on {csv_name} which is on the {tf} timeframe')
    images_folder = images_folder_for_symbol+'/'+ tf.replace(" ", "")
    print("The images folder is ",images_folder)
    model = load_model(local_model_path)
    draw_data(csv_name,images_folder,model,tf,symbol_without_spaces)
    images_folder = images_folder_for_symbol


if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    print(sys.argv)
    if len(sys.argv) != 2:
        sys.exit(1)
    # Extract arguments from command line
    start_index = sys.argv[1]
    make_predicitons(int(start_index))

