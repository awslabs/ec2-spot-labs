#!/bin/bash

mount -t efs %fileSystem%:/ /var/www/media

cd /var/www/koel && php artisan koel:init

systemctl enable httpd.service
systemctl start httpd.service
