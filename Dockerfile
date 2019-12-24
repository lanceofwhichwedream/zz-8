FROM python:3.7.6-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && apt-get update && apt-get install -y libffi-dev libnacl-dev python3-dev libopus-dev

COPY . .

CMD [ "python", "./zz-8.py" ]
