#!/bin/bash

systemctl stop httpd.service
systemctl disable httpd.service

systemctl stop mariadb.service
systemctl disable mariadb.service
