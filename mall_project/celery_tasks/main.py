from celery import Celery
import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall_project.settings.dev_settings'

# 创建celery应用
celery_app = Celery('mall')

# 导入配置
celery_app.config_from_object('celery_tasks.config')

# 导入任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.send_email', 'celery_tasks.html'])
