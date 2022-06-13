#!/bin/bash

aws --endpoint-url=http://localhost:4566 \
s3api put-bucket-notification-configuration --bucket davis-crud-bucket \
--notification-configuration file://s3-notif-config.json