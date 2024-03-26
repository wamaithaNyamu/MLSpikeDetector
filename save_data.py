import MetaTrader5 as mt5
from datetime import datetime
import pytz
import pandas as pd

from dotenv.main import load_dotenv
import os



load_dotenv()  # take environment variables from .env.

wamaitha_account=int(os.getenv("DERIV_ACCOUNT"))
wamaitha_password=str(os.getenv("DERIV_PASSWORD"))
wamaitha_server=str(os.getenv("DERIV_SERVER"))
symbol='Crash 1000 Index'
timezone = pytz.timezone("Etc/UTC")

start_date=datetime(2024, 1, 1, tzinfo=timezone)
end_date=datetime(2024, 3, 1, tzinfo=timezone)

symbol_without_spaces= symbol.replace(" ", "")

folder_path_for_symbol= f'./DATA/{symbol_without_spaces}'
start_date_formatted = start_date.strftime("%Y-%m-%d")
end_date_formatted = end_date.strftime("%Y-%m-%d")

csv_name_for_symbol=f'{symbol_without_spaces}-{start_date_formatted}-{end_date_formatted}'




def error_line(message):
    print(f'❌❌❌❌❌❌')
    print(message)


def create_folder(folder_path):
    """
    Checks if a folder exists
    @param folder_path: A string representing the path to the folder.   
    """
    try:
        check = os.path.exists(folder_path) and os.path.isdir(folder_path)
        if check:
            print('✅Folder already exists')
        else:
            os.makedirs(folder_path)
            print("✅Folder created successfully")
        
    except Exception as e:
        error_line(e)


def authenticate_to_mt5(account,password,server):
    """
    @param account: The MT5 account number that we want to log in to
    @param password: Password of the MT5 acc
    @param server: Server of the broker where we created the MT5 account
    @return None
        
    """
    try:
        print(f'Connecting to {account}...')
        if not mt5.initialize(login=account, password=password, server=server):
            print(f'failed to connect at account {account}, error code: {mt5.last_error()}')
            quit()

        authorized=mt5.login(account, password=password, server=server)
        if authorized:
            print(f'connected to account {account}')
        else:
            error_line(f'failed to connect at account {account}, error code: {mt5.last_error()}')

    except Exception as e:
            error_line(e)
    




def save_historic_data(symbol,start_date,end_date,folder_path,csv_name):
    """
    @param symbol: The asset we need to get the data from
    @param start_date: How far back to go for the data fetching
    @param end_date: Last date to terminate the data fetching
    @param folder_path: Folder that will store all the CSVs for the specic symbol
    @param csv_name:  name of the csv

    """
    try:
        create_folder(folder_path)
        print(f'Getting the historic data for {symbol} starting from date {start_date} to date {end_date}')
        timeframe = mt5.TIMEFRAME_M5
        raw_data_from_mt5 = mt5.copy_rates_range(str(symbol),timeframe , start_date, end_date)
        df = pd.DataFrame(raw_data_from_mt5)
        if timeframe == 5 :
            timeframe = '5Minute'
        csv_path =f'{folder_path}/{csv_name}-{timeframe}.csv'
        df.to_csv(csv_path)
        print(f'✅Data saved successfully to {csv_path}')
    
    except Exception as e:
        error_line(e) 





def main():
    try:
        # authenticate to MT5
        authenticate_to_mt5(wamaitha_account,wamaitha_password,wamaitha_server)
        save_historic_data(symbol,start_date,end_date,folder_path_for_symbol,csv_name_for_symbol) 

    except Exception as e:
        error_line(e)


main()