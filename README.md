# data-middleman（数据中间人）
用于负责采集snmp-exporter收集到的数据，并使用Prometheus能够接受的格式转发给Pushgateway。

# 运行
1.修改SNMP_EXPORTER_BASE_URL参数中[snmp-exporterIP]、[snmp-exporterPort]、[job name]为您自定义的相关参数。
``` bash
  [snmp-exporterIP]：snmp-exporter采集端IP地址；
  [snmp-exporterPort]：snmp-exporter采集端端口号，默认为9116；
  [job name]：snmp.yml中定义的关键字，默认为if_mib;
```
2.修改PUSHGATEWAY_URL_TEMPLATE参数中[pushgatewayIP]、[pushgatewayPort]为您自定义的相关参数。
``` bash
  [pushgatewayIP]：Pushgateway部署所在服务器IP地址；
  [pushgatewayPort]：Pushgateway部署所在服务器端口号，默认为9091；
```
3.添加想要采集的网络设备IP地址至SNMP_TARGETS参数中括号内，比如：
``` bash
SNMP_TARGETS = ['192.168.1.1', '192.168.2.1','172.16.1.1']  
```
4.run

#基本逻辑
首先查询snmp-exporter收集的网络设备信息，将数据格式化为Prometheus能够识别的格式，发送至Pushgateway组件，如果此脚本与Pushgateway或snmp-exporter无法通信，则会产生报错“Failed to fetch metrics from snmp-exporter for {target}: {response.status_code}”，反之提示“Metrics pushed to Pushgateway for {target} successfully.”，每60秒查询并推送一次。
