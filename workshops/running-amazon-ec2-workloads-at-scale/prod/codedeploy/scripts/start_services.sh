#!/bin/bash

cd /var/www/koel && php artisan koel:init

systemctl enable httpd.service
systemctl start httpd.service
