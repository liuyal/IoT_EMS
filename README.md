# Temperature_System


## Server

- [Charts](https://www.chartjs.org/)

## Nodes



## Django Guides
 - [Django Document](https://docs.djangoproject.com/en/3.0/)
 - [Django Guide](https://simpleisbetterthancomplex.com/series/beginners-guide/1.11/)
 - [Multi-Table Single Model](https://stackoverflow.com/questions/5036357/single-django-model-multiple-tables)
 - [Celery Periodic Tasks](https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html)
 - [Background Tasks](https://django-background-tasks.readthedocs.io/en/latest/)
 - [python CRONTAB](https://pypi.org/project/python-crontab/) 
 - [Django Socket](https://pypi.org/project/django-socket-server/)
 - [Twisted](https://twistedmatrix.com/trac/)


## MISC
- [AP Config](https://www.diyhobi.com/install-wifi-hotspot-raspberry-pi-ubuntu-mate/)
- [RFC 1812](https://tools.ietf.org/html/rfc1812#section-2)
- [Rest API Code](https://www.restapitutorial.com/httpstatuscodes.html)



### CODE & CMD
```
--CRON--
* * * * * sudo python3 /var/www/html/Temperature_System/backend/python/udp_cmd.py -f -u -l
@midnight sudo python3 /var/www/html/Temperature_System/backend/python/data_backup.py -v -l

--BASH--
netstat -tlpn | grep mysql
timedatectl set-ntp false
sudo ntpdate 1.ro.pool.ntp.org
TIMESTAMP = date +%Y%m%d
YESTERDAY_STAMP = date --date="1 day ago" +%Y%m%d
date +%Y%m%d -s "20191217"
date +%T -s "23:59:50"

--SQL--
mysqldump -u root --databases nova > dump.sql

CREATE USER 'nova'@'%' IDENTIFIED BY 'Airlink_1';
GRANT ALL PRIVILEGES ON *.* TO  'nova'@'%';
ALTER USER 'nova'@'%' IDENTIFIED WITH mysql_native_password BY 'Airlink_1';  

SHOW VARIABLES LIKE "max_connections";
SET GLOBAL max_connections = 500;

SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';
SET GLOBAL innodb_lock_wait_timeout = 300;

SELECT * FROM data ORDER BY time DESC LIMIT 1;
SELECT COUNT(*) FROM nodes WHERE status=true;
```