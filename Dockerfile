FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=application.py
ENV FLASK_RUN_HOST=0.0.0.0

# Create a startup script
RUN echo '#!/bin/bash\n\
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"\n\
flask run\n'\
> /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
