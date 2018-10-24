# lnetd

more info at : http://cpmarvin.blogspot.co.uk/ 
   
- clone lnetd (or download as a zip archive from github) most of the paths are hardcoded so use /opt/lnetd/
```
cd /opt/
git clone https://github.com/cpmarvin/lnetd.git
pip install -r requirements.txt
```

- change webserver if not run local
```
lab@cpe:/opt/lnetd/web_app$ grep -R ":8801" *           
base/static/custom/topology/create_graph.js:    var url = "http://127.0.0.1:8801/api/ifName?"+"ip="+interface+"&"+"host="+source
base/static/custom/topology/create_graph.js:    var rawDataURL = "http://127.0.0.1:8801/api/graph_ifindex?"+"ip="+interface+"&"+"host="+source
base/static/custom/topology/getSPF.js:  url = "http://127.0.0.1:8801/api/spf?"+"arr="+arrStr+"&"+"source="+source+"&"+"target="+target
base/static/custom/topology/getSPF_latency.js:        url = "http://127.0.0.1:8801/api/spf_and_latency?"+"arr="+arrStr+"&"+"source="+source+"&"+"target="+target
data/templates/model_demand.html:            url = "http://127.0.0.1:8801/api/model_demand?"+"arr="+arrStr+"&"+"demand="+demandArrStr

``` 
- run **/opt/lnetd/web_app**.
```
cd /opt/lnetd/web_app
python2 app.py
```
- go to webserver port 8801 , username is lab password is lab123

To use your own information you need to run all the isis_get.py from inputs directory.

For ISIS:
```
cd /opt/lnetd/inputs/jnp_isis_links
python2 isis_get.py
```

For OSPF via Ted database:
```
cd /opt/lnetd/inputs/jnp_ted_links
python2 ted_get.py
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

pmacct integration , to use netflow traffic as a demand you need pmacctd configured with sqlite3 support.

```
cd to pmacct/sbin directory and run 
./nfacctd -f /opt/lnetd/pmacct/etc/netflow.conf
```

LnetD expect the db to be in /opt/lnetd/web_app/database.db and pmacct.db while the web app gets the netflow demand using get_demand_netflow() in /opt/lnetd/webapp/data/ 

```
@blueprint.route('/model_demand', methods=['GET', 'POST'])
@login_required
def model_demand():
    netflow_demands = get_demand_netflow()
```

To deploy traffic goto webapp > Data Presentation > What if Demand > make sure "Use Netflow Demands as well" is checked and click Deploy Demand. You can also deploy without Netflow using the input box for source/target/demand.

* ISISd passive speaker to get the topology.Still requires TLV22 support with subtlv 6 and 8.

```
cd /opt/lnetd/inputs/isisd/
modify isisd.ini
ip link set eth<x> promisc on
sudo python lnetd.py
```

It takes couple of minutes depending of the size of the network. The only packets we LNETD is sending are HELLO and PSNP to request new LSP's.
No auth support for now.

