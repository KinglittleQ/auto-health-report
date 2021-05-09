import requests
import os
import os.path as osp
import socket
import ssl
import smtplib
from email.mime.text import MIMEText

ROOT = osp.dirname(__file__)


def cookie_is_valid(cookie: str):
    return "eai-sess=" in cookie


def report(cookie: str):
    url = "https://healthreport.zju.edu.cn/ncov/wap/default/save"

    headers = {
        "authority": "healthreport.zju.edu.cn",
        "method": "POST",
        "path": "/ncov/wap/default/save",
        "scheme": "https",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": cookie,
        "origin": "https://healthreport.zju.edu.cn",
        "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    geo_api_info = '{"type":"complete","info":"SUCCESS","status":1,"$Da":"jsonp_610294_","position":{"Q":30.30923,"R":120.08402000000001,"lng":120.08402,"lat":30.30923},"message":"Get ipLocation success.Get address success.","location_type":"ip","accuracy":null,"isConverted":true,"addressComponent":{"citycode":"0571","adcode":"330106","businessAreas":[],"neighborhoodType":"","neighborhood":"","building":"","buildingType":"","street":"紫荆花北路","streetNumber":"888号","country":"中国","province":"浙江省","city":"杭州市","district":"西湖区","township":"三墩镇"},"formattedAddress":"浙江省杭州市西湖区三墩镇丹阳3舍","roads":[],"crosses":[],"pois":[]}'

    payload = {
        "sfymqjczrj": "0",
        "zjdfgj": "",
        "sfyrjjh": "0",
        "cfgj": "",
        "tjgj": "",
        "nrjrq": "0",
        "rjka": "",
        "jnmddsheng": "",
        "jnmddshi": "",
        "jnmddqu": "",
        "jnmddxiangxi": "",
        "rjjtfs": "",
        "rjjtfs1": "",
        "rjjtgjbc": "",
        "jnjtfs": "",
        "jnjtfs1": "",
        "jnjtgjbc": "",
        "sfqrxxss": "1",
        "sfqtyyqjwdg": "0",
        "sffrqjwdg": "0",
        "sfhsjc": "",
        "zgfx14rfh": "0",
        "zgfx14rfhdd": "",
        "sfyxjzxgym": "1",
        "sfbyjzrq": "5",
        "jzxgymqk": "1",
        "tw": "0",
        "sfcxtz": "0",
        "sfjcbh": "0",
        "sfcxzysx": "0",
        "qksm": "",
        "sfyyjc": "0",
        "jcjgqr": "0",
        "remark": "",
        "address": "浙江省杭州市西湖区三墩镇丹阳3舍",
        "geo_api_info": geo_api_info,
        "area": "浙江省 杭州市 西湖区",
        "province": "浙江省",
        "city": "杭州市",
        "sfzx": "1",
        "sfjcwhry": "0",
        "sfjchbry": "0",
        "sfcyglq": "0",
        "gllx": "",
        "glksrq": "",
        "jcbhlx": "",
        "jcbhrq": "",
        "ismoved": "0",
        "bztcyy": "",
        "sftjhb": "0",
        "sftjwh": "0",
        "sfjcqz": "0",
        "jcqzrq": "",
        "jrsfqzys": "0",
        "jrsfqzfy": "0",
        "sfyqjzgc": "0",
        "sfsqhzjkk": "1",
        "sqhzjkkys": "1",
        "gwszgzcs": "",
        "szgj": "",
        "szgjcs": "",
        "fxyy": "",
        "jcjg": "",
        "zgfx14rfhsj": "",
    }

    r = requests.post(url, data=payload, headers=headers)
    return r.json()


def send_email(profile, email, ret):
    msg = MIMEText(f"""
敬爱的先生/女士：
    您的每日自动上报（{profile}）出现了一些小问题，可能需要联系管理员确认一切正常。
    报错信息是：{ret}
    
    祝 科研顺利！

    每日自动上报bot
""")

    with open(osp.join(ROOT, ".emailpassword"), "r") as f:
        me, password = f.read().split('\n')[:2]
        me = me.strip()

    msg['Subject'] = "每日自动上报警告"
    msg['From'] = me
    msg['To'] = email

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.qq.com", 465, context=context) as server:
        server.login(me, password)
        server.sendmail(
            me, email, msg.as_string()
        )


def report_all():
    path = osp.join(ROOT, "registers")
    registers = os.listdir(path)
    for i in registers:
        f = open(osp.join(path, i), "r")
        content = f.read()
        f.close()
        lines = content.split('\n')[:2]
        if len(lines) < 2:
            print(f"[WARN] skip profile {i}")
        else:
            email, cookie = lines
            if not cookie_is_valid(cookie):
                print(f"[WARN] {i}'s cookie is not valid")
                continue
            ret = report(cookie)
            if ret["e"] != 0:
                print(f"[WARN] {i}: {ret}")
                if ret["e"] != 1:
                    send_email(i, email, ret)
            else:
                print(f"[INFO] {i} reports successfully")


if __name__ == "__main__":
    report_all()
