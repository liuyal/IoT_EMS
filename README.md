# Temperature_System

## Server

## Nodes


## Django Guides
 - [Django Document](https://docs.djangoproject.com/en/3.0/)
 - [Django Guide](https://simpleisbetterthancomplex.com/series/beginners-guide/1.11/)
 - [Multi-Table Single Model](https://stackoverflow.com/questions/5036357/single-django-model-multiple-tables)
 - [Celery Periodic Tasks](https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html)
 - [Background Tasks](https://django-background-tasks.readthedocs.io/en/latest/)
 - [Django Socket](https://pypi.org/project/django-socket-server/)
 - [Twisted](https://twistedmatrix.com/trac/)


## MISC

- [AP Config](https://www.diyhobi.com/install-wifi-hotspot-raspberry-pi-ubuntu-mate/)
- [RFC 1812](https://tools.ietf.org/html/rfc1812#section-2)

### CODE & CMD
```
--TIME--
TIMESTAMP = date +%Y%m%d
YESTERDAY_STAMP = date --date="1 day ago" +%Y%m%d
timedatectl set-ntp false
sudo ntpdate 1.ro.pool.ntp.org
date +%Y%m%d -s "20191217"
date +%T -s "23:59:50"

--CRON--
* * * * * sudo python3 /var/www/html/Temperature_System/backend/python/udp_cmd.py -f -u -l
@midnight sudo python3 /var/www/html/Temperature_System/backend/python/data_backup.py -v -l

--BASH--
mysqldump --databases nova > dump.sql
netstat -tlpn | grep mysql
sudo -H pip3 --default-timeout=1000 install --upgrade pip

--SQL--
CREATE USER 'nova'@'%' IDENTIFIED BY 'Airlink_1';
GRANT ALL PRIVILEGES ON *.* TO  'nova'@'%';
ALTER USER 'nova'@'%' IDENTIFIED WITH mysql_native_password BY 'Airlink_1';  

CREATE USER 'zeus'@'192.168.1.80' IDENTIFIED BY 'Airlink_1';
GRANT ALL PRIVILEGES ON *.* TO 'zeus'@'192.168.1.80';
ALTER USER 'zeus'@'192.168.1.80' IDENTIFIED WITH mysql_native_password BY 'Airlink_1';  

SELECT * FROM data ORDER BY time DESC LIMIT 1;
SELECT COUNT(*) FROM nodes WHERE status=true;
```