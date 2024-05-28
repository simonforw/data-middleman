import requests
import time
import logging
import configparser

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件中获取SNMP Exporter的查询URL模板
SNMP_EXPORTER_BASE_URL = config.get('SNMP', 'exporter_base_url')

# 从配置文件中获取SNMP目标列表
SNMP_TARGETS = config.get('SNMP', 'targets').split(',')

# 从配置文件中获取Pushgateway的URL模板
PUSHGATEWAY_URL_TEMPLATE = config.get('Pushgateway', 'url_template')

def fetch_snmp_metrics(target):
    """从SNMP Exporter获取Prometheus格式的指标数据"""
    url = SNMP_EXPORTER_BASE_URL + '&target=' + target
    try:
        response = requests.get(url)
        response.raise_for_status()
        metrics = response.text
        # 保存获取的指标数据进行检查（可选）
        with open(f"{target.replace('.', '_')}_metrics.txt", 'w') as f:
            f.write(metrics)
        return metrics
    except requests.RequestException as e:
        logging.error(f"Failed to fetch metrics from snmp-exporter for {target}: {e}")
        return None

def clean_metrics_data(metrics):
    """清理和格式化指标数据，确保每行以换行符结尾"""
    lines = metrics.split('\n')
    cleaned_lines = [line for line in lines if line.strip() != '' and not line.startswith('#')]
    # 确保最后一行有换行符
    if cleaned_lines[-1] != '':
        cleaned_lines.append('')
    cleaned_metrics = '\n'.join(cleaned_lines)
    return cleaned_metrics

def push_metrics_to_pushgateway(metrics, target):
    """将指标数据推送到Pushgateway"""
    cleaned_metrics = clean_metrics_data(metrics)
    push_url = PUSHGATEWAY_URL_TEMPLATE.format(target.replace('.', '_'))
    headers = {'Content-Type': 'text/plain'}
    try:
        response = requests.post(push_url, data=cleaned_metrics, headers=headers)
        response.raise_for_status()
        if response.status_code == 200 or response.status_code == 202:
            logging.info(f"Metrics pushed to Pushgateway for {target} successfully.")
        else:
            logging.error(f"Failed to push metrics to Pushgateway for {target}: {response.status_code}")
            logging.error(response.text)
    except requests.RequestException as e:
        logging.error(f"Failed to push metrics to Pushgateway for {target}: {e}")

def main():
    while True:
        for target in SNMP_TARGETS:
            metrics = fetch_snmp_metrics(target)
            if metrics:
                push_metrics_to_pushgateway(metrics, target)
        time.sleep(60)

if __name__ == "__main__":
    main() 