from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app
import logging


logger = logging.getLogger('django')


@celery_app.task(name="send_verify_mail")
def send_verify_mail(to_email, verify_url):
    """
        发送验证邮箱邮件
        :param to_email: 收件人邮箱
        :param verify_url: 验证链接
        :return: None
    """
    subject = "AR's 商城邮件验证"
    html_message = f"""
        <p>尊敬的用户您好！</p> 
        <p>感谢您使用美多商城。</p> 
        <p>您的邮箱为：{to_email} 。请点击此链接激活您的邮箱：</p> 
        <p><a href="{verify_url}">{verify_url}<a></p>
    """
    recipient_list = [to_email]
    send_mail(subject=subject, message="", from_email=settings.EMAIL_FROM, recipient_list=recipient_list,
              html_message=html_message)
    logger.info('验证邮件发送成功')
