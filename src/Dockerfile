FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY wheelhouse /app/wheelhouse

RUN pip install --no-index --find-links=/app/wheelhouse -r requirements.txt

COPY . .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]