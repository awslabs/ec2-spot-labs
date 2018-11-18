#!/bin/bash

cd /var/www/koel && /usr/bin/yarn

cd /var/www/koel && /usr/local/bin/composer install

chown -R apache.apache /var/www/koel
