#!/bin/bash

sed -i 's/DB_HOST=127.0.0.1/DB_HOST=%endpoint%/g' /var/www/koel/.env
