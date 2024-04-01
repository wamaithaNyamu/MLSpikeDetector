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
 python scheduler.py  python 6 "Crash 1000 Index"
```

On a separate terminal 

```shell
 flask --app app run --debug

```
Test the endpoint

```shell
curl http://127.0.0.1:5000/predict
```

Add the endpoint to the MQL5 Bot that can be downloaded here https://wamaitha.co/p/aispikedetector 



http://127.0.0.1:5000/predict