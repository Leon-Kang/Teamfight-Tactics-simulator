FROM tiangolo/uvicorn-gunicorn:python3.10

ENV VIRTUAL_ENV=/opt/venv

RUN python3 -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN mkdir /teamfight

WORKDIR /teamfight

RUN git clone https://github.com/Leon-Kang/Teamfight-Tactics-simulator.git /teamfight

RUN  pip install --no-cache-dir --upgrade pip

RUN  pip install --no-cache-dir -r requirements.txt

EXPOSE 8999

CMD ["uvicorn", "main:app", "--proxy-headers", "--timeout-keep-alive","86400", "--host", "0.0.0.0", "--port", "8999"]