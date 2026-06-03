FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
COPY app.py .
RUN pip install -r requirements.txt
EXPOSE 8001
CMD ["python", "app.py"]