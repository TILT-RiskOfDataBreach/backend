FROM python:3.11-slim

ENV MODE=DOCKER

COPY . .

RUN pip install -r requirements.txt

CMD [ "uvicorn", "--host", "0.0.0.0", "app.main:app" ]
