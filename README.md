# IoT Environment Monitor System (EMS)

## Monitor Hub
- TBA

## Monitor Nodes
- TBA
 
## Setup

#### Dependencies
- Python3
  - [Scapy](https://pypi.org/project/scapy/)
  - [Requests](https://pypi.org/project/requests/)
  - [mysql-connector](https://pypi.org/project/mysql-connector-python/)
- [XAMPP](https://www.apachefriends.org/index.html)
  - PHP
  - Apache
  - MYSQL
- [Django](https://docs.djangoproject.com/en/3.0/topics/install/)
- [Node.js](https://nodejs.org/en/download/)
- [React](https://react-cn.github.io/react/downloads.html)

#### Commands
```
--CRON--
* * * * * cd /var/www/html/IoT_Environment_Monitor_System/backend/python/ && sudo python3 /var/www/html/IoT_Environment_Monitor_System/backend/python/backend.py -fusvl -L 9996 2>&1
@midnight cd /var/www/html/IoT_Environment_Monitor_System/backend/python/ && sudo python3 /var/www/html/IoT_Environment_Monitor_System/backend/python/backend.py -bvl -threads 10 -l 2>&1
```

```
--BASH--
sudo timedatectl set-ntp false
sudo ntpdate 1.ro.pool.ntp.org

sudo date +%Y%m%d -s "20200101"
sudo date +%T -s "23:59:00"

CURRENT_TIME_STAMP = date +%Y%m%d
YESTERDAY_TIME_STAMP = date --date="1 day ago" +%Y%m%d
```

```
--SQL--
sudo netstat -tlpn | grep mysql
sudo mysqldump -u root --databases nova > dump.sql
sudo mysql -u root -p nova < dump.sql

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

```
--Git--
git fetch --all
git reset --hard origin/master

```

## Server Test Automation
- TBA

## Reference Links

#### Backend
- [Scapy](https://scapy.readthedocs.io/en/latest/introduction.html)
- [Celery Periodic Tasks](http://www.celeryproject.org/)
- [Twisted](https://github.com/twisted/twisted)
- [python CRONTAB](https://pypi.org/project/python-crontab/)

#### Frontend
- [Charts.js](https://www.chartjs.org/)
- [React API](https://reactjs.org/docs/react-api.html)
- [Node.js](https://nodejs.org/en/docs/)

#### Django Guides
- [Django Documentation](https://docs.djangoproject.com/en/3.0/)
- [Django Guide](https://simpleisbetterthancomplex.com/series/beginners-guide/1.11/)
- [Django Background Tasks](https://django-background-tasks.readthedocs.io/en/latest/)
- [Django Socket](https://pypi.org/project/django-socket-server/)
- [Multi-Table Single Model](https://stackoverflow.com/questions/5036357/single-django-model-multiple-tables)

#### MISC
- [Access Point Configuration](https://www.diyhobi.com/install-wifi-hotspot-raspberry-pi-ubuntu-mate/)
- [HTTP Status Codes](https://www.restapitutorial.com/httpstatuscodes.html)
- [RFC 1812](https://tools.ietf.org/html/rfc1812#section-2)
