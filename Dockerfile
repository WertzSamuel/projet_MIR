FROM python:3.13-slim

RUN apt-get update -yq && apt-get upgrade -yq && apt-get install libgl1 -yq

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
