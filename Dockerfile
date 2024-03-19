FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src .

ENTRYPOINT ["gunicorn", "--reload", "-b", "0.0.0.0:5000", "app:app"]