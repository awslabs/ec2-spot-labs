#!/bin/bash

yum -y remove php* node

yum -y update

amazon-linux-extras install -y php7.2 epel

yum -y install \
  php-mbstring \
  php-xml \
  php-zip \
  httpd \
  amazon-efs-utils \
  stress-ng

curl --silent --location https://rpm.nodesource.com/setup_8.x | bash -
curl --silent --location https://dl.yarnpkg.com/rpm/yarn.repo | tee /etc/yum.repos.d/yarn.repo

yum -y install nodejs yarn

php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"

php composer-setup.php --quiet

rm composer-setup.php
mv composer.phar /usr/local/bin/composer