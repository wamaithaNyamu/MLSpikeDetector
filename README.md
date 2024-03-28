Prerequisites:

- Python 3.10+
- Pip
- Venv 
- MT5 installed
- Broker account - Deriv


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
