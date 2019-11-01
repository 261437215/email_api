from django.db import models

# Create your models here.
class UserInfo(models.Model):
    email = models.CharField(max_length=32,unique=True)#unique=True 不允许重复
    type = models.CharField(max_length=32)  # 邮箱类型
    passwd = models.CharField(max_length=32) # 发送方邮箱的授权码
    server = models.CharField(max_length=32)  # SMTP服务器
    server_port_number = models.CharField(max_length=32)  # 端口一般是465
