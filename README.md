# Aidon/Hafslund AMS parsing code

Use with an M-Bus dongle such as [this one](https://www.aliexpress.com/item/USB-to-MBUS-slave-module-MBUS-master-slave-communication-debugging-bus-monitor-TSS721-No-spontaneity-Self/32894249052.html).

Parser class (aidon_obis.py) requires python module crcmod (sudo pip install crcmod).

NB: This is not a full COSEM parser, as the number of OBIS fields and their sequence is assumed to be as on a Hafslund meter.

### aidon_test.py
Test output <br/>
./aidon_test.py <port> <br/>
./aidon_test.py /dev/ttyUSB0 <br/>

### aidon_influxdb_forward.py
Forward to influxdb. <br/>
./aidon_influxdb_forward.py <port> <influxdb API address> <database> <br/>
./aidon_influxdb_forward.py /dev/ttyUSB0 http://localhost:8086 metering <br/>

### aidon_read.py
Parses preliminary protocol used by Hafslund. <br/>
"./aidon_read.py /dev/ttyUSB0" <br/>


### Example output
```
List with 1 elements
1.0.1.7.0.255   : {'unit': 'W', 'value': 2501, 'obis_shortname': 'p_act_in'}
```

```
List with 12 elements
1.1.0.2.129.255 : {'value': 'AIDON_V0001', 'obis_shortname': 'obis_list_id'}
0.0.96.1.0.255  : {'value': '0000000000000000', 'obis_shortname': 'meter_id'}
0.0.96.1.7.255  : {'value': '6525', 'obis_shortname': 'meter_type'}
1.0.1.7.0.255   : {'unit': 'W', 'value': 2501, 'obis_shortname': 'p_act_in'}
1.0.2.7.0.255   : {'unit': 'W', 'value': 0, 'obis_shortname': 'p_act_out'}
1.0.3.7.0.255   : {'unit': 'var', 'value': 0, 'obis_shortname': 'p_react_in'}
1.0.4.7.0.255   : {'unit': 'var', 'value': 257, 'obis_shortname': 'p_react_out'}
1.0.31.7.0.255  : {'unit': 'A', 'value': 7.9, 'obis_shortname': 'il1'}
1.0.71.7.0.255  : {'unit': 'A', 'value': 3.5, 'obis_shortname': 'il3'}
1.0.32.7.0.255  : {'unit': 'V', 'value': 221.9, 'obis_shortname': 'ul1'}
1.0.52.7.0.255  : {'unit': 'V', 'value': 226.1, 'obis_shortname': 'ul2'}
1.0.72.7.0.255  : {'unit': 'V', 'value': 223.7, 'obis_shortname': 'ul3'}
```

```
List with 17 elements
1.1.0.2.129.255 : {'value': 'AIDON_V0001', 'obis_shortname': 'obis_list_id'}
0.0.96.1.0.255  : {'value': '0000000000000000', 'obis_shortname': 'meter_id'}
0.0.96.1.7.255  : {'value': '6525', 'obis_shortname': 'meter_type'}
1.0.1.7.0.255   : {'unit': 'W', 'value': 1302, 'obis_shortname': 'p_act_in'}
1.0.2.7.0.255   : {'unit': 'W', 'value': 0, 'obis_shortname': 'p_act_out'}
1.0.3.7.0.255   : {'unit': 'var', 'value': 0, 'obis_shortname': 'p_react_in'}
1.0.4.7.0.255   : {'unit': 'var', 'value': 213, 'obis_shortname': 'p_react_out'}
1.0.31.7.0.255  : {'unit': 'A', 'value': 5.3, 'obis_shortname': 'il1'}
1.0.71.7.0.255  : {'unit': 'A', 'value': 3.4, 'obis_shortname': 'il3'}
1.0.32.7.0.255  : {'unit': 'V', 'value': 222.0, 'obis_shortname': 'ul1'}
1.0.52.7.0.255  : {'unit': 'V', 'value': 226.0, 'obis_shortname': 'ul2'}
1.0.72.7.0.255  : {'unit': 'V', 'value': 225.0, 'obis_shortname': 'ul3'}
0.0.1.0.0.255   : {'deviation': 0, 'clock_status': 0, 'obis_shortname': 'clockdate', 'datetime': '2019.02.09T22:00:00'}
1.0.1.8.0.255   : {'unit': 'Wh', 'value': 7956270, 'obis_shortname': 'e_act_in_cum_h'}
1.0.2.8.0.255   : {'unit': 'Wh', 'value': 0, 'obis_shortname': 'e_act_out_cum_h'}
1.0.3.8.0.255   : {'unit': 'varh', 'value': 700, 'obis_shortname': 'e_react_in_cum_h'}
1.0.4.8.0.255   : {'unit': 'varh', 'value': 1128220, 'obis_shortname': 'e_react_out_cum_h'}
```