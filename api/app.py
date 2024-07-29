# -*- coding: UTF-8 -*-
import re
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]

def getdata(name):
    headers = {
        'Referer': 'https://github.com/' + name,
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'X-Requested-With': 'XMLHttpRequest'
    }
    gitpage = requests.get(f"https://github.com/{name}?action=show&controller=profiles&tab=contributions&user_id={name}", headers=headers)
    data = gitpage.text
    datadatereg = re.compile(r'data-date="(.*?)" id="contribution-day-component')
    datacountreg = re.compile(r'<tool-tip .*?class="sr-only position-absolute">(.*?) contribution')
    datadate = datadatereg.findall(data)
    datacount = datacountreg.findall(data)
    datacount = list(map(int, [0 if i == "No" else i for i in datacount]))

    # 检查datadate和datacount是否为空
    if not datadate or not datacount:
        # 处理空数据情况
        return {"total": 0, "contributions": []}

    # 将datadate和datacount按照字典序排序
    sorted_data = sorted(zip(datadate, datacount))
    datadate, datacount = zip(*sorted_data)
    contributions = sum(datacount)
    datalist = []
    for index, item in enumerate(datadate):
        itemlist = {"date": item, "count": datacount[index]}
        datalist.append(itemlist)
    datalistsplit = list_split(datalist, 7)
    returndata = {
        "total": contributions,
        "contributions": datalistsplit
    }
    return returndata

@app.route('/api', methods=['GET'])
def get_data_route():
    # 获取查询字符串中的所有参数
    query_string = request.query_string.decode()
    
    # 提取用户名，假设用户名是查询字符串中唯一的参数
    username = query_string.strip('&=?').replace('+', ' ')
    
    if not username:
        return jsonify({"error": "username parameter is required"}), 400  # 如果没有提供 username 参数，返回错误信息

    data = getdata(username)
    response = jsonify(data)
    
    # 允许特定域名访问
    origin = request.headers.get('Origin')  # 获取请求头中的 Origin 字段

    if origin in ['http://www.xiaoyu.ac.cn',  'http://ls.xiaoyu.ac.cn']:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        # 可以选择拒绝访问或者设置为其他值
        response.headers['Access-Control-Allow-Origin'] = 'https://www.xiaoyu.ac.cn'  # 默认值

    # 设置其他允许的请求头和方法
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST')
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
