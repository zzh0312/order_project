from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required, login_required
from.order_models import Order  # 导入Order模型，确保路径正确
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
import os
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import uuid


def is_superuser(user):
    return user.is_superuser

# 订单列表视图，展示所有订单，支持搜索和分页功能
@login_required
# @user_passes_test(is_superuser)
def order_list(request):
    query = request.GET.get('q')
    if query:
        orders = Order.objects.filter(
            Q(order_number__icontains=query) |
            Q(thug__icontains=query) |  # 根据“打手”字段关联查询，可根据实际需求调整关联字段
            Q(single_number__icontains=query) |
            Q(boss__icontains=query)  # 根据老板用户名关联查询，可根据实际需求调整关联字段
        )
    else:
        orders = Order.objects.all()

    paginator = Paginator(orders, 10)  # 每页显示10条订单记录，可按需调整
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'user': request.user
    }
    return render(request, 'order_list.html', context)


# 订单详情视图，展示单个订单的详细信息
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # 构建图片的完整URL路径，以便在模板中正确显示图片（假设使用了MEDIA_URL等配置）
    if order.image:
        order.image_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, str(order.image)))
    else:
        order.image_url = None
    context = {
        'order': order
    }
    return render(request, 'order_detail.html', context)


# 图片预上传视图函数
def pre_upload_image(request):
    if request.method == 'POST':
        # 获取上传的图片文件
        image = request.FILES.get('image')
        if image:
            # 生成一个唯一的临时文件名（这里简单使用UUID，你也可以根据实际需求调整命名策略）
            temp_image_name = str(uuid.uuid4()) + os.path.splitext(image.name)[1]
            # 构建临时图片保存的路径，假设你的媒体文件根目录是MEDIA_ROOT，你可以根据实际配置调整
            temp_image_path = os.path.join('media', 'temp_images', temp_image_name)
            try:
                # 确保临时图片保存的目录存在，如果不存在则创建
                os.makedirs(os.path.dirname(temp_image_path), exist_ok=True)
                with open(temp_image_path, 'wb') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
                # 返回成功的响应，包含临时图片的标识（这里以临时文件名作为标识示例）
                return JsonResponse({
                   'success': True,
                    'temp_image_id': temp_image_name
                })
            except Exception as e:
                # 如果保存过程出现错误，返回错误响应
                return JsonResponse({
                   'success': False,
                    'error_message': f'图片保存失败: {str(e)}'
                })
        return JsonResponse({
           'success': False,
            'error_message': '没有接收到有效的图片文件'
        })
    return HttpResponse(status=405)  # 如果不是POST请求，返回方法不允许的状态码


# 创建订单视图，需要用户登录
@login_required
def create_order(request):
    if request.method == 'POST':
        user = request.user
        order_date = datetime.datetime.now()  # 获取当前时间作为订单创建时间，可根据实际情况调整

        thug = request.POST.get('thug')
        date = request.POST.get('date')
        single_number = request.POST.get('single_number')
        boss = request.POST.get('boss')
        if len(boss) < 2 or len(boss) > 50:
            messages.error(request, '老板信息长度需在2 - 50个字符之间，请重新输入')
            return redirect('create_order')
        unit_price = request.POST.get('unit_price')
        # 获取上传的图片文件，如果存在的话
        image = request.FILES.get('image') if 'image' in request.FILES else None
        if image:
            # 验证图片格式，这里简单示例只允许常见的几种图片格式，可根据实际需求扩展
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = os.path.splitext(image.name)[1].lower()
            if file_extension not in allowed_extensions:
                messages.error(request, '请上传正确格式的图片（支持jpg、jpeg、png、gif）')
                return redirect('create_order')
        original_price = request.POST.get('original_price')
        is_received = request.POST.get('is_received')
        is_closed = request.POST.get('is_closed')
        profit = request.POST.get('profit')
        manual_status = request.POST.get('manual_status')
        audit_status = request.POST.get('audit_status')

        # 创建订单对象并保存到数据库
        order = Order(
            user=user,
            order_date=order_date,
            thug=thug,
            date=date,
            single_number=single_number,
            boss=boss,
            unit_price=unit_price,
            image=image,
            original_price=original_price,
            is_received=is_received,
            is_closed=is_closed,
            profit=profit,
            manual_status=manual_status,
            audit_status=audit_status,
        )
        order.save()
        messages.success(request, '订单创建成功')
        return redirect('create_order')
    return render(request, 'create_order.html')


# 更新订单视图，需要有相应权限（此处假设权限名为 'update_order'，你需根据实际情况配置）
# @permission_required('health_app.update_order')
@login_required
def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        # 获取前端传来的临时图片标识
        temp_image_id = request.POST.get('temp_image_id')
        if temp_image_id:
            # 构建临时图片在服务器上的完整路径，同样基于前面假设的媒体文件相关配置
            temp_image_path = os.path.join('media', 'temp_images', temp_image_id)
            if os.path.exists(temp_image_path):
                # 如果临时图片存在，将其移动到正式的订单图片保存位置（这里假设订单图片保存路径在media/orders下，你可按需调整）
                new_image_path = os.path.join('media', 'orders', temp_image_id)
                os.rename(temp_image_path, new_image_path)
                # 将订单对象的image字段设置为新的图片路径（这里只是简单示例，实际可能需要根据模型的具体设置调整，比如使用ImageField的相关方法）
                order.image = os.path.join('orders', temp_image_id)
            else:
                messages.error(request, '预上传的图片不存在，请重新上传')
                return redirect('update_order', order_id=order_id)
        # 其他订单字段更新逻辑保持不变，以下是省略的部分代码示例
        order.thug = request.POST.get('thug')
        order.date = request.POST.get('date')
        order.single_number = request.POST.get('single_number')
        order.boss = request.POST.get('boss')
        order.unit_price = request.POST.get('unit_price')
        order.original_price = request.POST.get('original_price')
        order.is_received = request.POST.get('is_received')
        order.is_closed = request.POST.get('is_closed')
        order.profit = request.POST.get('profit')
        order.manual_status = request.POST.get('manual_status')
        order.audit_status = request.POST.get('audit_status')

        order.save()
        messages.success(request, '订单更新成功')
        return redirect('order_list')
    context = {
        'order': order
    }
    return render(request, 'update_order.html', context)


# 删除订单视图，需要有相应权限（此处假设权限名为 'delete_order'，你需根据实际情况配置）
# @permission_required('health_app.delete_order')
@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'GET':
        # 删除订单时，同时删除对应的图片文件（如果存在的话）
        if order.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(order.image))
            if os.path.exists(image_path):
                os.remove(image_path)
        order.delete()
        messages.success(request, '订单已删除')
        return redirect('order_list')
    context = {
        'order': order
    }
    return render(request, 'delete_order.html', context)