# Imagen de python
FROM python:3.11-slim
# carpeta de trabajo del contenedor
WORKDIR /app
# Copio los archivos necesarios
COPY requirements.txt .
COPY app.py .
# Instalacion de las dependencias a utilizar
RUN pip install -r requirements.txt
# Puerto del servicio
EXPOSE 8001
# Comando para correr el servicio
CMD ["python", "app.py"]