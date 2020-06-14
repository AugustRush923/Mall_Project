from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
# Create your views here.

from mall_project.libs.captcha.captcha import captcha
from . import constants


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