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


Run the scheduler

```shell
 python scheduler.py
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



