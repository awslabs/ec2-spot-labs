#!/bin/bash

sed -i 's/LoadModule mpm_prefork_module/#LoadModule mpm_prefork_module/g' /etc/httpd/conf.modules.d/00-mpm.conf
sed -i 's/#LoadModule mpm_event_module/LoadModule mpm_event_module/g' /etc/httpd/conf.modules.d/00-mpm.conf

sed -i 's/memory_limit = 128M/memory_limit = 4096M/g' /etc/php.ini
