import random
import logging
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
# Create your views here.
from mall_project.libs.captcha.captcha import captcha
from celery_tasks.sms.tasks import send_sms_code
from users.models import User
from .serializers import ImageCodeCheckSerializer
from . import constants

logger = logging.getLogger('django')


class ImageCodeView(APIView):

    def get(self, request, image_code_id):
        '''
        生成验证码图片
        '''
        text, image = captcha.generate_captcha()

        # 连接redis
        redis_conn = get_redis_connection('captcha')
        # 设置图片过期时间
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type="images/jpg")


# url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(GenericAPIView):
    """
    短信验证码
    传入参数：
        mobile, image_code_id, text
    """
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):
        # 检验参数
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成验证码
        sms_code = '%06d' % random.randint(0, 999999)

        # 保存验证码
        redis_conn = get_redis_connection('captcha')
        # redis_conn.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # redis_conn.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # redis管道
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 通知redis管道执行命令
        pl.execute()

        # # 发送短信
        # try:
        #     ccp = CCP()
        #     expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        #     ret = ccp.send_template_sms(mobile, [sms_code, expires], constants.SMS_CODE_TEMP_ID)
        #     print(ret)
        # except Exception as e:
        #     logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
        #     return Response({'message': 'failed'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        # else:
        #     if ret == 0:
        #         logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        #         return Response({'message': 'OK'})
        #     else:
        #         logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
        #         return Response({'message': 'failed'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 使用celery发送验证码
        send_sms_code.delay(mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES, constants.SMS_CODE_TEMP_ID)
        # 返回
        return Response({'message': 'OK'})


class UsernameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data)


class UserView(CreateAPIView):
    """
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    """
    pass
