FROM python:3.11-alpine as base



RUN mkdir /svc COPY . /svc

WORKDIR /svc



RUN pip install wheel && pip wheel . --wheel-dir=/svc/wheels



FROM python:3.11-alpine

EXPOSE 8080

COPY --from=base /svc /svc

WORKDIR /svc

RUN pip install --no-index --find-links=/shadow_reporting/wheels -r requirements.txt


CMD streamlit run --server.port 8080 --server.enableCORS false app.py
