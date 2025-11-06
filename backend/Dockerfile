FROM python:3.13-slim

WORKDIR /app
RUN mount type=bind,source=requirements.txt,target=/tmp/requirements.txt,readonly \
    && pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
