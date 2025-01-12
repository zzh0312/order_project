from django.urls import path
from. import views
from.views import article_detail, custom_login
from.views import home, profile_view, logout_view, add_article, edit_article, delete_article
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from health_app.order_views import order_list, create_order, order_detail, update_order, delete_order,pre_upload_image
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('', home, name='home'),
    path('', order_list , name='order_list'),
    path('accounts/profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
    # path('articles/', views.article_list, name='article_list'),
    path('articles/<int:article_id>/', article_detail, name='article_detail'),
    path('add_article/', add_article, name='add_article'),
    path('edit_article/', edit_article, name='edit_article'),
    path('delete_article/', delete_article, name='delete_article'),
    
    path('orders/', order_list, name='order_list'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/create/', create_order, name='create_order'),
    path('orders/update/<int:order_id>/', update_order, name='update_order'),  # 注意这里<int:order_id>定义了参数接收方式
    path('orders/delete/<int:order_id>/', delete_order, name='delete_order'),
    path('pre_upload_image/', pre_upload_image, name='pre_upload_image'),  # 添加图片预上传的路由
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])