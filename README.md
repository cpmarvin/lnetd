# lnetd
demo site : http://demo.lnetd.co.uk

#slack channel , contact me if you need support 
https://networktocode.slack.com #lnetd

#if you are are using LnetD in your network and are willing to share that contact me:
cpmarvin at gmail.com or slack ( cpmarvin )

#How to 
- you need python3.6 
- clone lnetd (or download as a zip archive from github) most of the paths are hardcoded so use /opt/lnetd/
```
cd /opt/
git clone https://github.com/cpmarvin/lnetd.git
pip install -r requirements.txt
```
- forecast module requires more dependencies,if you can't install fbprophet disable the forecast function.
```
cd /opt/
pip install -r requirements_forecast.txt
```

- change the ip address of the WEB server in the admin module. 

``` 
- run **/opt/lnetd/web_app**.
```
cd /opt/lnetd/web_app
python3 app.py
```
- go to webserver port 8801 , username is lab password is lab123

For input you can use either isisd or rpc scripts.

For ISISd ( Legacy not supported anymore ).
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
python3 isis_get.py
```

Once you have the input info to move the info from input database to web app database run below . there is config.ini that you select the input
```
cd /opt/lnetd/output
python3 to_db_links.py
python3 to_db_prefixes.py
python3 to_db_routers.py

example for jnp_rpc below , see crontab_example.txt for all 

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

#aggregate 1h 
0 * * * * cd /opt/lnetd/output/h_aggregated/ && python h_aggregate_influxdb.py

- pmacct integration , to use netflow traffic as a demand you need pmacctd configured with sqlite3 support.
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
App_config              International_PoP_temp  Routers               
App_external_flows      Inventory_cards         Script_run            
Bgp_customers           Inventory_interfaces    User                  
Bgp_peering_points      Links                   isisd_links           
Bgp_peers               Links_latency           isisd_prefixes        
External_position       Links_time              isisd_routers         
External_topology       Node_position           rpc_links             
External_topology_temp  Node_position_temp      rpc_prefixes          
International_PoP       Prefixes                rpc_routers
```

The input module will write to either isisd_ or rpc_ while the output module will read from isisd_|rpc_ and write to Links,Prefixes or Routers


