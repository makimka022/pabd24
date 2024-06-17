# syntax=docker/dockerfile:1

FROM python:3.9
WORKDIR /app
COPY ./src/predict_app.py ./src/predict_app.py
COPY ./.env ./.env
COPY ./models/xgb_reg_v3.joblib ./models/xgb_reg_v3.joblib
RUN pip3 install flask flask-cors flask_httpauth \
          scikit-learn python-dotenv joblib gunicorn geopy xgboost
CMD ["gunicorn", "-b", "0.0.0.0", "-w", "1", "src.predict_app:app"]
EXPOSE 8000