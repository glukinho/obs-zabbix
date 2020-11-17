# obs-zabbix
Python script for sending OBS recording/scripting status to Zabbix.

Based on MTQQ script: https://obsproject.com/forum/resources/real-time-mqtt-status.1014/

Pre-requisites:
* OBS installed (tested on 26.0.2 x64)
* Python 3.6 installed (tested on 3.6.8 x64 portable)
* obspython module loaded (you can find it inside OBS installation folder)
* `zabbix-sender.exe` somewhere on PC with OBS
* Zabbix server (tested on 3.4.3) with your host and template 'Template OBS' attached (import from `zbx_export_templates.xml`)

How to:
1. Import the `obs-zabbix.py` to OBS (Tools - Scripts)
2. Write your appropriate settings: https://prnt.sc/vkzqv4
  * Path to `zabbix-sender.exe` on OBS PC
  * Zabbix server hostname or IP
  * Name of the host inside Zabbix server (most probably hostname of the PC with OBS)
  * how often OBS will send status to Zabbix, in seconds
  * Zabbix key that will receive data (do not touch if unsure)
3. If everything is OK, you will see some logs in Script Log window and JSON data in Zabbix server: https://prnt.sc/vkzp68

Zabbix rises trigger in cases:
  * recording status != true
  * streaming status != true
  * no data for `{$OBS_NODATA}` time (update your host or template, default is 1m)
