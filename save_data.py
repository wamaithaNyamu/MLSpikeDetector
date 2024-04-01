import MetaTrader5 as mt5
from datetime import datetime
import pytz
import pandas as pd
from dotenv.main import load_dotenv
import os


load_dotenv()  # take environment variables from .env.

wamaitha_account = int(os.getenv("DERIV_ACCOUNT"))
wamaitha_password = str(os.getenv("DERIV_PASSWORD"))
wamaitha_server = str(os.getenv("DERIV_SERVER"))
symbol = "META"
timezone = pytz.timezone("Etc/UTC")

start_date = datetime(2022, 1, 1, tzinfo=timezone)
end_date = datetime(2024, 1, 1, tzinfo=timezone)
symbol_without_spaces = symbol.replace(" ", "")
folder_path_for_symbol = f"./DATA/{symbol_without_spaces}"
start_date_formatted = start_date.strftime("%Y-%m-%d")
end_date_formatted = end_date.strftime("%Y-%m-%d")
csv_name_for_symbol = (
    f"{symbol_without_spaces}-{start_date_formatted}-{end_date_formatted}"
)

csv_names = []

def error_line(message):
    print(f"❌❌❌❌❌❌")
    print(message)


def create_folder(folder_path):
    """
    Checks if a folder exists
    @param folder_path: A string representing the path to the folder.
    """
    try:
        check = os.path.exists(folder_path) and os.path.isdir(folder_path)
        if check:
            print("✅Folder already exists")
        else:
            os.makedirs(folder_path)
            print("✅Folder created successfully")

    except Exception as e:
        error_line(e)


def authenticate_to_mt5(account, password, server):
    """
    @param account: The MT5 account number that we want to log in to
    @param password: Password of the MT5 acc
    @param server: Server of the broker where we created the MT5 account
    @return None

    """
    try:
        print(f"Connecting to {account}...")
        if not mt5.initialize(login=account, password=password, server=server):
            print(
                f"failed to connect at account {account}, error code: {mt5.last_error()}"
            )
            quit()

        authorized = mt5.login(account, password=password, server=server)
        if authorized:
            print(f"connected to account {account}")
        else:
            error_line(
                f"failed to connect at account {account}, error code: {mt5.last_error()}"
            )

    except Exception as e:
        error_line(e)


def get_timeframe(tf_name):
    timeframes = {
        "1 minute": mt5.TIMEFRAME_M1,
        "2 minutes": mt5.TIMEFRAME_M2,
        "3 minutes": mt5.TIMEFRAME_M3,
        "4 minutes": mt5.TIMEFRAME_M4,
        "5 minutes": mt5.TIMEFRAME_M5,
        "6 minutes": mt5.TIMEFRAME_M6,
        "10 minutes": mt5.TIMEFRAME_M10,
        "12 minutes": mt5.TIMEFRAME_M12,
        "15 minutes": mt5.TIMEFRAME_M15,
        "20 minutes": mt5.TIMEFRAME_M20,
        "30 minutes": mt5.TIMEFRAME_M30,
        "1 hour": mt5.TIMEFRAME_H1,
        "2 hours": mt5.TIMEFRAME_H2,
        "3 hours": mt5.TIMEFRAME_H3,
        "4 hours": mt5.TIMEFRAME_H4,
        "6 hours": mt5.TIMEFRAME_H6,
        "8 hours": mt5.TIMEFRAME_H8,
        "12 hours": mt5.TIMEFRAME_H12,
        "1 day": mt5.TIMEFRAME_D1,
        "1 week": mt5.TIMEFRAME_W1,
        "1 month": mt5.TIMEFRAME_MN1,
    }
    return timeframes.get(tf_name, mt5.TIMEFRAME_D1)


def save_historic_data(symbol, start_date, end_date, folder_path, csv_name, tf):
    """
    @param symbol: The asset we need to get the data from
    @param start_date: How far back to go for the data fetching
    @param end_date: Last date to terminate the data fetching
    @param folder_path: Folder that will store all the CSVs for the specic symbol
    @param csv_name:  name of the csv

    """
    try:
        create_folder(folder_path)
        print(
            f"Getting the historic data for {symbol} starting from date {start_date} to date {end_date} for {tf}"
        )

        timeframe = get_timeframe(tf)

        raw_data_from_mt5 = mt5.copy_rates_range(
            str(symbol), timeframe, start_date, end_date
        )
        df = pd.DataFrame(raw_data_from_mt5)
        tf = tf.replace(" ", "")
        csv_path = f"{folder_path}/{csv_name}-{tf}.csv"
        csv_names.append(csv_path)
        df.to_csv(csv_path)
        print(f"✅Data saved successfully to {csv_path}")

    except Exception as e:
        error_line(e)


def main():
    try:
        timeframe_full_names = [
            "1 minute",
            "2 minutes",
            "3 minutes",
            "4 minutes",
            "5 minutes",
            "6 minutes",
            "10 minutes",
            "12 minutes",
            "15 minutes",
            "20 minutes",
            "30 minutes",
            "1 hour",
            "2 hours",
            "3 hours",
            "4 hours",
            "6 hours",
            "8 hours",
            "12 hours",
            "1 day",
            "1 week",
            "1 month",
        ]

        # authenticate to MT5
        authenticate_to_mt5(wamaitha_account, wamaitha_password, wamaitha_server)
        for tf in timeframe_full_names:
            save_historic_data(
                symbol, start_date, end_date, folder_path_for_symbol, csv_name_for_symbol,tf
            )

        print('-----------------------------')
        print(csv_names)
    except Exception as e:
        error_line(e)


# main()
