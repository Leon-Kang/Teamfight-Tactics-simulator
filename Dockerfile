FROM python:3.10

WORKDIR /app

RUN git clone https://github.com/Leon-Kang/Teamfight-Tactics-simulator.git /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8999

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8999"]