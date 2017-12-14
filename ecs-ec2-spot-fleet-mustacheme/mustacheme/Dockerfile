FROM python:2.7

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -q update && \
	apt-get -y -q install \
	nginx \
	libjpeg-dev \
	zlibc \
	zip \
	supervisor

# Drop in application source
RUN mkdir -p /var/www/mustacheme
COPY api-static/ /var/www/mustacheme

# Disable daemon mode for nginx and remove default site page
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default

# Install python packages
RUN cd /var/www/mustacheme && \
	virtualenv venv && \
	. venv/bin/activate && \
	pip install uwsgi numpy geopy flask pillow boto3

# Drop in application nginx config
RUN cd /var/www/mustacheme && \
	ln -s $PWD/nginx/nginx.conf /etc/nginx/conf.d

# Drop in supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/

# Expose port 80 and start supervisor
EXPOSE 80/tcp
CMD ["/usr/bin/supervisord"]
