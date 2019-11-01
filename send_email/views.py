import os
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django.core.mail import EmailMessage
import requests
import json
import time
import smtplib
from Api.settings import file_directory
from send_email.models import UserInfo
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart  # Python 发送带附件的邮件
from email.header import Header  # 设置编码方式
from email.mime.application import MIMEApplication

'''
1.发件人只有一个是固定的
2.邮件的服务类型分为为QQ,163,阿里
3.收件人，主题，邮件正文作为参数
4.是否附带文件作为可传参数
    分几个类型：
    0 代表不带附件
    1 代表文本附件
    2 代表html附件
    3 代表其他附件
'''

url = 'http://192.168.1.69/viewvc/YZW/%E5%85%85%E7%94%B5%E6%A1%A9APP%E5%B9%B3%E5%8F%B0/source/trunk/Manage_Project/?view=log'

headers = {
    'Host': '192.168.1.69',
    'Authorization': 'Basic eWlucnVndW86V29zaGl5cmc2NjY =',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
}


class Emailview(APIView):
    def post(self, request, *args, **kwargs):
        # type分三种 QQ 163 ali
        msg_from = request._request.POST.get('msg_from')  # 发送者
        subject = request._request.POST.get('subject')  # 主题
        mail_msg = request._request.POST.get('count')  # 内容
        included = request._request.POST.get('included')  # 是否上传文件
        msg_to = request._request.POST.get(
            'msg_to').split(',')  # 以列表的形式  接受方,支持群发
        type = msg_from.split('@')[-1]
        if type == 'qq.com':
            # passwd = 'aawhjlgooxhcbiba'  # 授权码
            # server = 'smtp.qq.com'
            # server_port_number = 465
            user = UserInfo.objects.get(email=msg_from)
            passwd = user.passwd
            server = user.server
            server_port_number = user.server_port_number

        elif type == '163.com':
            #163邮箱会提示 发送的邮件内容包含了未被许可的信息，或被系统识别为垃圾邮件。请检查是否有用户发送病毒或者垃圾邮件；

            passwd = 'yrg123456'  #
            server = 'smtp.163.com'
            server_port_number = 465


            # user = UserInfo.objects.get(email=msg_from)
            # passwd = user.passwd
            # server = user.server
            # server_port_number = user.server_port_number


        elif type == 'cloudbaysystem.com':
            # passwd = 'Woshiyrg666'  # 密码
            # server = 'smtp.qiye.aliyun.com'
            # server_port_number = 465
            user = UserInfo.objects.get(email=msg_from)
            passwd = user.passwd
            server = user.server
            server_port_number = user.server_port_number


        if included == '0':
            # included=0 为不带附件
            # msg = MIMEText(mail_message, 'html', 'utf-8')  # 发送含HTML内容的邮件
            # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
            msg = MIMEText(mail_msg, 'plain', 'utf-8')  # 内容
            msg['Subject'] = Header(subject, 'utf-8')  # 主题
            msg['From'] = Header(msg_from, 'utf-8')  # 发送者
            msg['To'] = Header(','.join(msg_to), 'utf-8')  # 接收者
            try:
                s = smtplib.SMTP_SSL(server, server_port_number)  # 邮件服务器及端口号
                s.login(msg_from, passwd)  # 登录SMTP服务器
                s.sendmail(msg_from, msg_to, msg.as_string())
                return HttpResponse("邮件发送成功")
            except BaseException:
                return HttpResponse("邮件发送失败")
            finally:
                s.quit()
        elif included == '1':
            # included=1 为文本文件:
            # 第三方 SMTP 服务
            file = request.FILES.getlist('file')  # 文件
            msg = MIMEMultipart()  # 创建一个带附件的实例
            msg['Subject'] = Header(subject, 'utf-8')  # 主题
            msg['From'] = Header(msg_from, 'utf-8')  # 发送者
            msg['To'] = Header(','.join(msg_to), 'utf-8')  # 接收者
            # ---文字部分---
            part = MIMEText(mail_msg, 'utf-8')
            msg.attach(part)
            # ---附件部分---
            for i in file:
                destination = open(os.path.join(f"{file_directory}", str(time.strftime(
                    '%Y-%m-%d', time.localtime(time.time()))) + i.name), 'wb+')  # 打开特定的文件进行二进制的写操作
                for chunk in i.chunks():  # 分块写入文件
                    destination.write(chunk)
                destination.close()
                # time = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
                part = MIMEApplication(
                    open(
                        f"{file_directory}{str(time.strftime('%Y-%m-%d', time.localtime(time.time()))) + i.name}",
                        'rb').read())

                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=str(
                        time.strftime(
                            '%Y-%m-%d',
                            time.localtime(
                                time.time()))) +
                    i.name)
                msg.attach(part)

        elif included == '2':
            # 2代表html附件
            # 第三方 SMTP 服务
            file = request.FILES.getlist('file')  # 文件
            msg = MIMEMultipart()  # 创建一个带附件的实例
            msg['Subject'] = Header(subject, 'utf-8')  # 主题
            msg['From'] = Header(msg_from, 'utf-8')  # 发送者
            msg['To'] = Header(','.join(msg_to), 'utf-8')  # 接收者
            # ---文字部分---
            part = MIMEText(mail_msg, 'utf-8')
            msg.attach(part)
            # ---附件部分---
            for i in file:
                destination = open(os.path.join(f"{file_directory}", str(time.strftime(
                    '%Y-%m-%d', time.localtime(time.time()))) + i.name), 'wb+')  # 打开特定的文件进行二进制的写操作
                for chunk in i.chunks():  # 分块写入文件
                    destination.write(chunk)
                destination.close()
                part = MIMEApplication(
                    open(
                        f"{file_directory}{str(time.strftime('%Y-%m-%d', time.localtime(time.time()))) + i.name}",
                        'rb').read())

                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=str(
                        time.strftime(
                            '%Y-%m-%d',
                            time.localtime(
                                time.time()))) +
                    i.name)
                msg.attach(part)

        elif included == '3':
            # 3 代表其他附件
            # 第三方 SMTP 服务
            file = request.FILES.getlist('file')  # 文件
            msg = MIMEMultipart()  # 创建一个带附件的实例
            msg['Subject'] = Header(subject, 'utf-8')  # 主题
            msg['From'] = Header(msg_from, 'utf-8')  # 发送者
            msg['To'] = Header(','.join(msg_to), 'utf-8')  # 接收者
            # ---文字部分---
            part = MIMEText(mail_msg, 'utf-8')
            msg.attach(part)
            # ---附件部分---
            for i in file:
                destination = open(os.path.join(f"{file_directory}", str(time.strftime(
                    '%Y-%m-%d', time.localtime(time.time()))) + i.name), 'wb+')  # 打开特定的文件进行二进制的写操作
                for chunk in i.chunks():  # 分块写入文件
                    destination.write(chunk)
                destination.close()
                part = MIMEApplication(
                    open(
                        f"{file_directory}{str(time.strftime('%Y-%m-%d', time.localtime(time.time()))) + i.name}",
                        'rb').read())
                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=str(
                        time.strftime(
                            '%Y-%m-%d',
                            time.localtime(
                                time.time()))) +
                    i.name)
                msg.attach(part)

        try:
            s = smtplib.SMTP(server)  # 连接smtp邮件服务器,端口默认是25
            s.login(msg_from, passwd)  # 登陆服务器
            s.sendmail(msg_from, msg_to, msg.as_string())  # 发送邮件
            s.close()
            return HttpResponse("邮件发送成功!")
        except Exception as e:
            return HttpResponse(f"邮件发送失败,原因是:{e}")
