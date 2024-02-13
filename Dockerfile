FROM python:3.11

WORKDIR /app

COPY ./app/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./ /app/

ENV SQLALCHEMY_DATABASE_URL=sqlite:///app/data/owltracker.db

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "111"]
