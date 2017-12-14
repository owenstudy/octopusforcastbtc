#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 17-12-12 下午10:55
# @Author  : Owen_study
# @Email   : owen_study@126.com
# @File    : emails.py
# @Software: PyCharm
# ===============================================
import smtplib
from email.mime.text import MIMEText
from email.header import Header
# QQ sekvracqqedgbgci
# 126 Windows2000
sender = '25129049@qq.com'
receivers = ['owen_study@126.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

# 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
message = MIMEText('Owen你好，\nLTC_BTC当前的价格已经上升4%，需要你赶紧行动起来了', 'plain', 'utf-8')
message['from'] = Header("OwenQQ<25129049@qq.com>", 'utf-8')
message['to'] = Header("Owen<owen_study@126.com>", 'utf-8')

subject = 'LTC_BTC价格已经到达4%,买入检查起来'
message['Subject'] = Header(subject, 'utf-8')

try:
    smtpObj = smtplib.SMTP_SSL(timeout=20)
    smtpObj.connect("smtp.qq.com",465)
    smtpObj.set_debuglevel(1)
    smtpObj.login(sender, 'sekvracqqedgbgci')
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功")
except smtplib.SMTPException:
    print("Error: 无法发送邮件")
if __name__ == '__main__':
    pass