from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

from verification import constants
from mall_project.utils.models import BaseModel
from areas.models import Area
# Create your models here.


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    email_active = models.BooleanField(default=False, verbose_name="邮箱验证状态")
    default_address = models.ForeignKey('Address', related_name="users", null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name="默认收货地址")

    class Meta:
        db_table = 'tb_users'
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def generate_verify_email_url(self):
        """
        生成验证邮箱的url
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        data = {'user_id': self.id, 'email': self.email}
        print(data)
        token = serializer.dumps(data).decode()
        print(token)
        verify_url = 'http://www.mall.site:8080/success_verify_email.html?token=' + token
        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
            print(data)
            user_id = data.get('user_id')
            email = data.get('email')
            user = User.objects.get(email=email)
        except BadData:
            return
        except User.DoesNotExist:
            return
        else:
            return user


class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address', verbose_name="用户")
    title = models.CharField(max_length=20, verbose_name="地址名称")
    receiver = models.CharField(max_length=20, verbose_name="收货人")
    province = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="province_address", verbose_name="省")
    city = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="city_address", verbose_name="市")
    district = models.ForeignKey(Area, on_delete=models.PROTECT, related_name="district_address", verbose_name="区")
    place = models.CharField(max_length=50, verbose_name="地址")
    mobile = models.CharField(max_length=11, verbose_name="手机号")
    tel = models.CharField(max_length=20, blank=True, null=True, default='', verbose_name="座机号码")
    email = models.EmailField(null=True, blank=True, default='', verbose_name="邮箱")
    is_delete = models.BooleanField(default=False, verbose_name="逻辑删除")
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    class Meta:
        db_table = "tb_address"
        verbose_name_plural = verbose_name = "用户地址"
        ordering = ['-is_default', '-update_time']
