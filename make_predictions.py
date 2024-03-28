from ultralyticsplus import YOLO,render_result
import pandas as pd
import numpy as np
from save_data import create_folder,symbol,start_date_formatted,end_date_formatted
import cv2

local_model_path = "best.pt"
csv_path_for_symbol="DATA/Crash1000Index/Crash1000Index-2022-01-01-2024-01-01-16408.csv"
images_folder_for_symbol=f'IMAGES/{symbol}-{start_date_formatted}-{end_date_formatted}'

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

def backtest(predictions, close_prices, actual_outcome):
    """
    Backtests the predictions against the actual classes.
    @params predictions: Predicted class IDs ( "down",  "up").
    @params close_prices: Close prices corresponding to each prediction.
    @params actual_classes : Actual class prices of the actual close that happened

    @returns win_loss_record : value of the percentage of won
                             
    """
    try:
        total = len(predictions)
        won_count=0
        lost_count=0
        for prediction, close_price, the_actual_outcome in zip(predictions, close_prices, actual_outcome):
            if prediction == "down":  # Predicted class is "down"
                if the_actual_outcome < close_price:
                    print("✅Won Down")
                    won_count = won_count + 1  # Correct prediction, won
                else:
                    print("❌Lost Down")
                    lost_count= lost_count + 1  # Incorrect prediction, lost
            elif prediction == "up":  # Predicted class is "up"
                if the_actual_outcome > close_price:
                    print("✅Won Up")
                    won_count = won_count + 1 # Correct prediction, won
                else:
                    print("❌Lost Up")
                    lost_count= lost_count + 1  # Incorrect prediction, lost
        return won_count / total * 100
    except Exception as e:
        error_line(e)


def draw_data(csv_path,images_folder,model):
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
        
        # create the folder
        create_folder(images_folder)
          # read csv
        df = pd.read_csv(csv_path)
  
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
            # Save your sample
            cv2.imwrite(output_path, render_np)
            # Increment counters
            start_candle, end_candle = start_candle + 1, end_candle + 1


        win_loss = backtest(prediction, prediction_close_price, actual_outcome)
        print("This model had a win loss of ", win_loss)
            
    except Exception as e:
        error_line(e)


def main():
   model = load_model(local_model_path)
   draw_data(csv_path_for_symbol,images_folder_for_symbol,model)
main()
