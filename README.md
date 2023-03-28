# TR064_Syslog_Relais
A small Software to act as a Relais between a TR-064 enabled Device and a syslog service.

This Software is a proof of concept and does not implement any level of Security, 
implement needed Securities your self- 


## INSTALL

Add a new user and home directory for the Logging Service

```
sudo useradd -m tr064Logger
```
<br>


Copy the script and the requiremnts into the home of the new user
```
cp /home/<username>/Download/tr064CheckLog.py /home/tr064Logger
cp /home/<username>/Download/requirements.txt /home/tr064Logger
```
<br>
Give the new user ownership of the file

```
chown tr064Logger:tr064Logger tr064CheckLog.py
```

<br>
Mark the file as executable

```
chmod +x tr064CheckLog.py
```

<br>
Now add a credentials.ini file to the working directory. Feel free to implement safer Secret handling. <br>
File-Structure:<br>
<br>

```
HOST\n
PORT\n
UID\n
PASSWD\n
EOF
```

<br>
Add the Service to the System in /etc/systemd/system/

```
cp /home/<username>/Download/TR064Logging.service /etc/systemd/system/TR064Logging.service
```

<br>
Reload the daemon 

```
sudo systemctl daemon-reload
```

<br>
Now start and enable the service

```
sudo systemctl enable TR064Logging.service
sudo systemctl start TR064Logging.service
```
