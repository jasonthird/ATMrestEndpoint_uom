FROM python:3.10

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY ./main.py /app/main.py
COPY ./clientLib.py /app/clientLib.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
