FROM amazonlinux:1

RUN yum -y --security update

RUN yum -y install \
  aws-cli \
  ImageMagick \
  util-linux

COPY convert-worker.sh /usr/local/bin/convert-worker.sh

ENTRYPOINT ["/usr/local/bin/convert-worker.sh"]