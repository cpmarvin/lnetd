# lnetd

   
- clone lnetd (or download as a zip archive from github)
```
cd /opt/
git clone https://github.com/cpmarvin/lnetd.git
```
    
- run **/opt/lnetd/web_app**.
```
cd /opt/lnetd/web_app
python app.py
```
- go to webserver port 8801 , username is lab password is lab123

To use your own information you need to run all the isis_get.py from inputs directory.

```
cd /opt/lnetd/isis_links
python isis_get.py
```

isis_routes/isis_prefixes don't required the information from influxdb + telegraf but isis_links does. To make it easier until you have the telegraf + influxdb up and running ( telegraf snmp configuration in the repo ) the if_index/util/and capacity is commented out and instead static values will be in the db. 

```
uncomment this if influxdb and telegraf info available
df4['l_int'] = df4.apply(lambda row: get_ifIndex_IP(row['source'],row['l_ip']),axis=1)
df4['util'] = df4.apply(lambda row: get_uti_ifIndex(row['source'],row['l_int'],0),axis=1)
df4['capacity'] = df4.apply(lambda row: get_capacity_ifIndex(row['source'],row['l_int']),axis=1)

#comment below once influxdb and telegraf is up and running
df4['l_int'] = 34
df4['util'] = 50
df4['capacity'] = 100

```
