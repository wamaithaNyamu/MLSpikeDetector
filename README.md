
[![Youtube Walkthrough](https://img.youtube.com/vi/9UZZHxky3E8/0.jpg)](https://youtu.be/9UZZHxky3E8?si=5odfHzZX3m14ALku)

Prerequisites:

- Python 3.10+
- Pip
- Venv 
- MT5 installed
- Broker account - Deriv

Create a .env file and add

```shell
DERIV_ACCOUNT=
DERIV_PASSWORD=
DERIV_SERVER=

```

Install dependencies

```shell
    pip install -r requirements.txt

```

Donwload the model from huggingface https://huggingface.co/foduucom/stockmarket-future-prediction/tree/main


Run the scheduler 6 is the hours, and the last string is the symbol

```shell
 python scheduler.py  python 6 "hours" "Crash 1000 Index"
```

On a separate terminal 

```shell
 flask --app app run --debug -p 4000 -h 0.0.0.0   

```
Test the endpoint

```shell
curl http://127.0.0.1:5000/predict?symbol=Crash1000Index&Timeframe=6hours
```

Add the endpoint to the MQL5 Bot that can be downloaded here https://ko-fi.com/s/597c59bd4f

------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Instructions for using this project with wine on MacOS 
Prerequisites:
- homebrew installed - https://brew.sh/

- Install wine stable on Mac
```shell
brew cask install wine-stable

```
- Install python inside wine. Go to https://www.python.org/downloads/windows/ and download the windows installer. Then install it using:

```shell

wine <path-to-the-python-windows.exe>
```

- Install mt5 inside wine. First download the windows mt5 installer at https://deriv.com/trading-platforms/deriv-mt5#download . Then install the mt5 in wine using:

```shell
wine <path-to-thederiv-mt5.exe>

```
- Launch MT5 

```shell

cd /Users/wamaitha/.wine/drive_c/Program\ Files/MetaTrader\ 5\ Terminal && wine terminal64.exe 

```

- Install dependencies

```shell
 wine pip install -r requirements.txt

```

- Run the scheduler code inside wine 

```shell

 wine  python scheduler.py  python 6 "hours" "Crash 1000 Index"
```
- Optionally run the flask endpoint inisde wine too 

```shell
wine flask --app app run --debug -p 4000 -h 0.0.0.0 

```
- If you choose to run the flask endpoint on Mac, use the http://<add-ip-here>:<port> on the MT5 bot https://ko-fi.com/s/597c59bd4f

- To check ip on Mac
ipconfig getifaddr $(route -n get default|awk '/interface/ { print $2 }')
