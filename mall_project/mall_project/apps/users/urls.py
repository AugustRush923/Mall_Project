from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers
from . import views

urlpatterns = [
    url(r'^users/$', views.UserView.as_view()),
    url(r'^user/$', views.UserDetailView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^email/$', views.EmailUpdateView.as_view()),
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
    url(r'^addresses/$', views.AddressViewSet.as_view({'get': "list", 'post': 'create'})),
    url(r'^addresses/(?P<pk>\d+)/$', views.AddressViewSet.as_view({"delete": "destroy"})),
    url(r'^addresses/(?P<pk>\d+)/status/$', views.AddressViewSet.as_view({"put": "status"})),
    url(r'^addresses/(?P<pk>\d+)/title/$', views.AddressViewSet.as_view({"put": "title"})),
]

# router = routers.DefaultRouter()
# router.register(r'addresses', views.AddressViewSet, base_name='addresses')
#
# urlpatterns += router.urls
# POST /addresses/ 新建  -> create
# PUT /addresses/<pk>/ 修改  -> update
# GET /addresses/  查询  -> list
# DELETE /addresses/<pk>/  删除 -> destroy
# PUT /addresses/<pk>/status/ 设置默认 -> status
# PUT /addresses/<pk>/title/  设置标题 -> title
