FROM python:3.9-slim

RUN apt-get update && apt-get install -y curl && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip show newrelic

COPY . .

# Copia la configuración de New Relic (debe estar en el mismo directorio que el Dockerfile)
COPY newrelic.ini .

EXPOSE 5000

ENV FLASK_APP=application.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV NEW_RELIC_CONFIG_FILE=newrelic.ini

#CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
# Comando para ejecutar con New Relic
#CMD ["newrelic-admin", "run-program", "flask", "run", "--host=0.0.0.0", "--port=5000"]
CMD ["newrelic-admin", "run-program", "python", "application.py"]

