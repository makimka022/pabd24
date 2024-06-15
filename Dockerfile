# syntax=docker/dockerfile:1

FROM python:3.9
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
CMD ["gunicorn", "-b", "0.0.0.0", "src.predict_app:app", "--daemon "] 
EXPOSE 8000