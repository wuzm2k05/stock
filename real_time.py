import requests
import pandas as pd
import time

def em_us_real():
    """
    东方财富-美股-实时行情
    http://quote.eastmoney.com/center/gridlist.html#us_stocks
    :return: 美股-实时行情; 延迟 15 min
    "f1": "_",
    "f2": "最新价",
    "f3": "涨跌幅",
    "f4": "涨跌额",
    "f5": "成交量",
    "f6": "成交额",
    "f7": "振幅",
    "f8": "换手率",
    "f9": "-",
    "f10": "_",
    "f11": "_",
    "f12": "简称",
    "f13": "编码",
    "f14": "名称",
    "f15": "最高价",
    "f16": "最低价",
    "f17": "开盘价",
    "f18": "昨收价",
    "f20": "总市值",
    "f21": "_",
    "f22": "_",
    "f23": "_",
    "f24": "_",
    "f25": "_",
    "f26": "_",
    "f33": "_",
    "f62": "_",
    "f115": "市盈率",
    "f124": "时间戳",
    "f128": "_",
    "f140": "_",
    "f141": "_",
    "f136": "_",
    "f152": "_",
    """
    url = "http://72.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "20000",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:105,m:106,m:107",
        "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,"
                  "f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f124,f152",
        "_": str(int(time.time() * 1000)),
    }
    res = requests.get(url, params=params)
    if res.status_code != 200:
        print(f"em_us_real/status_code:{res.status_code}/text:{res.text}")
        return []
    else:
        try:
            data_json = res.json()
        except Exception as e:
            print(f"em_us_real/error: res.json()/detail:{e.__str__()}")
            return []
        if "data" in data_json and "diff" in data_json["data"] and data_json["data"]["diff"]:
            res = []
            for d in data_json["data"]["diff"]:
                #_datetime = mystriptime(d["f124"])
                res.append({"stock_code": d["f12"],
                            "name": d["f14"],
                            "eng_name": d["f12"],
                            #"date": _datetime.strftime("%Y-%m-%d"),
                            #"time": _datetime.strftime("%H:%M:%M"),
                            "now": pd.to_numeric(d["f2"], errors="coerce"),
                            "open": pd.to_numeric(d["f17"], errors="coerce"),
                            "close": pd.to_numeric(d["f18"], errors="coerce"),
                            "high": pd.to_numeric(d["f15"], errors="coerce"),
                            "low": pd.to_numeric(d["f16"], errors="coerce"),
                            "volume": pd.to_numeric(d["f6"], errors="coerce"),
                            "turnover": pd.to_numeric(d["f5"], errors="coerce"),
                            "buy": pd.to_numeric(d["f2"], errors="coerce"),
                            "sell": pd.to_numeric(d["f2"], errors="coerce"),
                            "change": pd.to_numeric(d["f4"], errors="coerce"),
                            "change_rate": pd.to_numeric(d["f3"], errors="coerce"),
                            "stock_type": "us"})
            return res
        else:
            return []


hk_sina_stock_list_url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHKStockData"
hk_sina_stock_dict_payload = {
    "page": "1",
    "num": "3000",
    "sort": "symbol",
    "asc": "1",
    "node": "qbgg_hk",
    "_s_r_a": "page"
}
def sina_hk_real():
    """
    新浪财经-港股的所有港股的实时行情数据
    http://vip.stock.finance.sina.com.cn/mkt/#qbgg_hk
    :return: 实时行情数据
    :rtype: []
    """
    res = requests.get(hk_sina_stock_list_url, params=hk_sina_stock_dict_payload)
    if res.status_code != 200:
        print(f"sina_hk_real/status_code:{res.status_code}/text:{res.text}")
        return []
    else:
        try:
            data_json = res.json()
            """
            {'symbol': '00021',  # 港股代码
            'name': '大中华地产控股',  # 中文名称
            'engname': 'GREAT CHI PPT',  # 英文名称
            'tradetype': 'EQTY',  # 交易类型
            'lasttrade': '0.000',  # 最新价
            'prevclose': '0.118',  # 前一个交易日收盘价
            'open': '0.000',  # 开盘价
            'high': '0.000',  # 最高价
            'low': '0.000',  # 最低价
            'volume': '0',  # 成交量(万)
            'currentvolume': '0',  # 每手股数
            'amount': '0',  # 成交额(万)
            'ticktime': '2022-04-08 10:54:17',  # 当前数据时间戳
            'buy': '0.115',  # 买一
            'sell': '0.120',  # 卖一
            'high_52week': '0.247',  # 52周最高价
            'low_52week': '0.110',  # 52周最低价
            'eps': '-0.003',   # 每股收益
            'dividend': None,   # 股息
            'stocks_sum': '3975233406', 
            'pricechange': '0.000',  # 涨跌额
            'changepercent': '0.0000000',  # 涨跌幅
            'market_value': '0.000',  # 港股市值
            'pe_ratio': '0.0000000'
            }
            """
        except Exception as e:
            print(f"sina_hk_real/error: res.json()/detail:{e.__str__()}")
            return []
        res = [
            {"stock_code": d["symbol"],
             "name": d["name"],
             "eng_name": d["engname"],
             "date": d["ticktime"][:10],
             "time": d["ticktime"][11:],
             "now": float(d["lasttrade"]),
             "open": float(d["open"]),
             "close": float(d["prevclose"]),
             "high": float(d["high"]),
             "low": float(d["low"]),
             "volume": float(d["amount"]) * 10000,
             "turnover": float(d["volume"]) * 10000,
             "buy": float(d["buy"]),
             "sell": float(d["sell"]),
             "change": float(d["pricechange"]),
             "change_rate": float(d["changepercent"]),
             "stock_type": "hk"}
            for d in data_json
        ]
    return res

data = em_us_real()
for stock in data:
  if "海底捞" in stock["name"]:
    print(stock)
#print(sina_hk_real())