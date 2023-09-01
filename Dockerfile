FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 8501
COPY looker.ini ./app
COPY app.py ./app
ENTRYPOINT ['streamlit', 'run']
CMD ['app.py']