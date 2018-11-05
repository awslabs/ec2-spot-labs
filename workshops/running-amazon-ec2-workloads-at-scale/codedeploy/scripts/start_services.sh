#!/bin/bash

systemctl enable mariadb.service
systemctl start mariadb.service

systemctl enable httpd.service
systemctl start httpd.service
