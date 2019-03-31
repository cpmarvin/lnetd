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
web_app/data/templates/topology.html   
web_app/data/templates/topology.html       
web_app/data/templates/model_edit.html        
web_app/data/templates/topology_errors.html   
web_app/data/templates/topology_errors.html        
web_app/data/templates/model_demand.html        
web_app/base/static/custom/topology/create_graph.js    
web_app/base/static/custom/topology/create_graph.js   
web_app/base/static/custom/topology/getSPF.js
web_app/base/static/custom/topology/getSPF_latency.js
...
``` 
- run **/opt/lnetd/web_app**.
```
cd /opt/lnetd/web_app
python2 app.py
```
- go to webserver port 8801 , username is lab password is lab123

For input you can use either isisd or rpc scripts.

For ISISd.
```
cd /opt/lnetd/inputs/isisd
sudo python lnetd.py
```

For RPC via a juniper device
```
cd /opt/lnetd/inputs/
jnp_isis_links
jnp_isis_prefixes
jnp_isis_routers
python2 isis_get.py
```

Once you have the input info to move the info from input database to web app database run below . there is config.ini that you select the input
```
cd /opt/lnetd/output
python2 to_db_links.py
python2 to_db_prefixes.py
python2 to_db_routers.py

pmacct integration , to use netflow traffic as a demand you need pmacctd configured with sqlite3 support.

example for jnp_rpc below 
*/5 * * * *  cd /opt/lnetd/inputs/jnp_isis_prefixes && python isis_get.py
*/5 * * * *  cd /opt/lnetd/inputs/jnp_isis_links && python isis_get.py
*/5 * * * *  cd /opt/lnetd/inputs/jnp_isis_routers && python isis_get.py
*/5 * * * *  cd /opt/lnetd/output && python to_db_links.py
*/5 * * * *  cd /opt/lnetd/output && python to_db_routers.py
*/5 * * * *  cd /opt/lnetd/output && python to_db_prefixes.py

#international pop
*/5 * * * *  cd /opt/lnetd/inputs/international_pop && python generate_pop_capacity.py

#external topology
*/5 * * * * cd /opt/lnetd/inputs/external_topology && python generate_topology.py

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


The database is formed of the following tables. 
```
sqlite> .tables
Links               Prefixes            isisd_prefixes      rpc_routers
Links_latency       Routers             isisd_routers
Node_position       User                rpc_links
Node_position_temp  isisd_links         rpc_prefixes
```

The input module will write to either isisd_ or rpc_ while the output module will read from isisd_|rpc_ and write to Links,Prefixes or Routers

Links:
sqlite> select * from isisd_links limit 1;
index|l_ip|metric|r_ip|source|target|l_ip_r_ip

sqlite> select * from rpc_links limit 1;
index|source|target|metric|l_ip|r_ip|l_ip_r_ip

sqlite> select * from Links limit 1;
index|l_ip|metric|r_ip|source|target|l_ip_r_ip|l_int|util|capacity|errors

Prefixes:
sqlite> select * from isisd_prefixes limit 1;
index|ip|name|country

sqlite> select * from rpc_prefixes limit 1;
index|name|ip|country

sqlite> select * from Prefixes limit 1;
index|ip|name|country|version

Routers:
sqlite> select * from isisd_routers limit 1;
index|ip|name|country

sqlite> select * from rpc_routers limit 1;
index|name|ip|country

sqlite> select * from Routers limit 1;
index|ip|name|country|vendor|model|version

