FROM python:3.8

WORKDIR /therapeutics_experiment

COPY ./requirements.txt .
COPY ./data ./data
COPY ./app.py .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "./app.py"]
