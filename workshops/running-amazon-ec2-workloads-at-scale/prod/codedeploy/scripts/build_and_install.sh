#!/bin/bash

cd /var/www/koel && /usr/bin/yarn

cd /var/www/koel && /usr/local/bin/composer install

chown -R apache.apache /var/www/koel

mkdir /var/www/media

chown apache.apache /var/www/media