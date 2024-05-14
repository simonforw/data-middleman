import requests  
import time  
  
# SNMP Exporter的查询URL模板（不含target参数）  
SNMP_EXPORTER_BASE_URL = 'http://[snmp-exporterIP]:[snmp-exporterPort]/snmp?auth=public_v2&module=[job name]'  
  
# SNMP目标的列表  
SNMP_TARGETS = ['deviceip 1', 'deviceip 2','device n']  
  
# Pushgateway的地址和端口号，以及对应的job和instance  
PUSHGATEWAY_URL_TEMPLATE = 'http://[pushgatewayIP]:[pushgatewayPort]/metrics/job/snmp_exporter/instance/snmp_target_{}'  
  
def fetch_snmp_metrics(target):  
    # 构建完整的SNMP exporter查询URL  
    url = SNMP_EXPORTER_BASE_URL + '&target=' + target  
    # 从snmp-exporter获取Prometheus格式的指标数据  
    response = requests.get(url)  
    if response.status_code == 200:  
        return response.text  
    else:  
        print(f"Failed to fetch metrics from snmp-exporter for {target}: {response.status_code}")  
        return None  
  
def push_metrics_to_pushgateway(metrics, target):  
    # 构建Pushgateway的完整URL  
    push_url = PUSHGATEWAY_URL_TEMPLATE.format(target.replace('.', '_'))  
    headers = {'Content-Type': 'text/plain'}  
    response = requests.post(push_url, data=metrics, headers=headers)  
    if response.status_code == 200 or response.status_code == 202:  # 200 和 202 都表示成功  
        print(f"Metrics pushed to Pushgateway for {target} successfully.")  
    else:  
        print(f"Failed to push metrics to Pushgateway for {target}: {response.status_code}")  
        print(response.text)  # 打印出返回的内容以便调试  
  
def main():  
    while True:  
        for target in SNMP_TARGETS:  
            metrics = fetch_snmp_metrics(target)  
            if metrics:  
                push_metrics_to_pushgateway(metrics, target)  
        time.sleep(60)  # 每60秒推送一次  
  
if __name__ == "__main__":  
    main()