import csv
import io
import warnings
import requests
from bs4 import BeautifulSoup
import re
import os

# 忽略 urllib3 的 SSL 警告
warnings.filterwarnings('ignore', category=UserWarning)

# 目标URL列表
urls = [
    'https://cf.090227.xyz',
    'https://ip.164746.xyz/ipTop10.html',
    'https://bihai.cf/CFIP/CUCC/standard.txt',
    'https://bihai.cf/CFIP/CMCC/standard.txt',
    'https://ipdb.030101.xyz/api/bestcf.csv',
    'https://ipdb.030101.xyz/api/bestproxy.csv'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 检查ip.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 使用集合来存储唯一的IP地址
unique_ips = set()

# 处理每个URL
for url in urls:
    try:
        print(f"\n正在处理 URL: {url}")
        response = requests.get(url)
        response.raise_for_status()

        elements = []
        # 根据URL类型处理不同的响应
        if url.endswith('.txt'):
            elements = response.text.split('\n')[:50]
            print(f"从txt文件中获取到 {len(elements)} 个元素")
        elif url.endswith('.csv'):
            content = response.content.decode('utf-8')
            csv_reader = csv.reader(io.StringIO(content))
            next(csv_reader)  # 跳过标题行
            if url == 'https://ipdb.030101.xyz/api/bestcf.csv':
                # 获取前20个IP
                elements = [next(csv_reader)[0] for _ in range(30)]
                print(f"从bestcf.csv中获取前30个IP")
            elif url == 'https://ipdb.030101.xyz/api/bestproxy.csv':
                # 获取所有IP
                elements = [row[0] for row in csv_reader]
                print(f"从bestproxy.csv中获取所有IP")
            print(f"从CSV文件中获取到 {len(elements)} 个元素")
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            if url == 'https://cf.090227.xyz':
                elements = soup.find_all('tr')
            elif url == 'https://ip.164746.xyz/ipTop10.html':
                elements = soup
            print(f"从HTML中获取到 {len(elements)} 个元素")

        # 遍历所有元素,查找IP地址
        for element in elements:
            element_text = element if isinstance(element, str) else element.get_text()
            ip_matches = re.findall(ip_pattern, element_text)
            
            # 将找到的IP地址添加到集合中（自动去重）
            for ip in ip_matches:
                unique_ips.add(ip)
                print(f"找到IP: {ip}")

    except Exception as e:
        print(f"处理 {url} 时出错: {str(e)}")
        continue

# 将去重后的IP地址写入文件
with open('ip.txt', 'w') as file:
    for ip in unique_ips:
        file.write(ip + '\n')

print(f'\n总共找到 {len(unique_ips)} 个唯一IP地址')
print('IP地址已保存到ip.txt文件中。')
