FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 8501
COPY looker.ini ./looker.ini
COPY looker_query.template ./looker_query.template
COPY app.py ./app.py
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]