#!/bin/bash

systemctl enable mariadb.service
systemctl start mariadb.service

mysql -e "CREATE DATABASE koel DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;"
mysql -e "CREATE USER 'koel'@'127.0.0.1' IDENTIFIED BY 'SoSecureMuchWow';"
mysql -e "GRANT ALL PRIVILEGES ON koel.* TO 'koel'@'127.0.0.1' WITH GRANT OPTION;"

mysql koel < /var/www/koel/koel.sql
