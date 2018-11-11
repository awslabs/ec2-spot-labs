#!/bin/bash

systemctl stop httpd.service
systemctl disable httpd.service

umount /var/www/media