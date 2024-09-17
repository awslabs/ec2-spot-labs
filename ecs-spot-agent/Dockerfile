FROM public.ecr.aws/docker/library/python:3.9.20-slim

LABEL maintainer "mats16 <mats.kazuki@gmail.com>"

RUN pip install boto3==1.9.101 requests==2.21.0

COPY ecs/ /opt/ecs/

ENV CHECK_INTERVAL=5

CMD ["python", "-u", "/opt/ecs/check_termination.py"]
