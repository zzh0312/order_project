from django.db import models
from django.contrib.auth.models import User  # 导入用户模型，用于关联相关用户（可根据实际情况调整，比如使用自定义用户模型）
import random
import string
from django.utils import timezone


class Order(models.Model):
    """
    订单模型类，用于记录订单相关的核心信息
    """
    # 关联下单用户，一个用户可以有多个订单，当用户被删除时（on_delete=models.CASCADE），对应的订单也会被删除
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    """
    用户字段，关联到系统中的用户，代表下单用户，方便后续从用户角度查询其所有订单，例如 user.orders.all()。
    """
    # 自动生成订单编号，重写 save 方法来实现根据日期自动生成唯一编号的逻辑
    order_number = models.CharField(max_length=50, unique=True)
    """
    订单编号，具有唯一性的字符串，用于唯一标识每个订单，通过重写 save 方法按照一定规则自动生成，
    这里设置最大长度为50，格式大致为 'YYYYMMDD_随机字符串'。
    """
    order_date = models.DateTimeField(auto_now_add=True)
    """
    订单创建时间，auto_now_add=True 表示在订单创建时自动记录当前时间，用于记录订单生成的准确时间点。
    """
    thug = models.CharField(max_length=100, blank=True, null=True)
    """
    “打手”字段，可用于记录与订单相关的打手信息，设为可为空（blank=True, null=True），因为可能某些订单不需要该信息。
    """
    date = models.DateField(blank=True, null=True)
    """
    “日期”字段，可用于记录与订单相关的特定日期信息，设为可为空，以适应不同订单的情况。
    """
    single_number = models.CharField(max_length=50, blank=True, null=True)
    """
    “单号”字段，可用于记录额外的单号相关信息，设为可为空，方便在业务中有特殊单号需求时使用。
    """
    boss = models.CharField(max_length=100, blank=True, null=True)
    """
    “老板”字段，用于记录订单对应的老板相关信息（如姓名等），设为可为空，因为可能存在不需要明确老板或老板信息不全的订单情况。
    """
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    """
    “单价”字段，可用于记录商品或服务的单价情况，设为可为空，以适应不同订单的计价模式。
    """
    image = models.ImageField(upload_to='orders/', blank=True, null=True)
    """
    “图片”字段，可用于上传和存储与订单相关的图片文件，如商品图片、服务凭证图片等。
    upload_to='orders/' 表示图片将上传到项目设置的媒体文件存储路径下的 'orders/' 子目录中，设为可为空，因为不是所有订单都一定有图片。
    """
    # 新增“原价”字段，用于记录商品或服务原本的价格，使用DecimalField精确存储小数金额
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    """
    “原价”字段，可用于对比单价等情况，分析价格变动等业务逻辑，设为可为空，以适应不同业务场景需求。
    """
    # 新增“是否收货”字段，使用BooleanField来表示是否已经收到货物，默认值设为False
    RECEIVED_CHOICES = [
        ('yes', '是'),
        ('no', '否'),
    ]
    is_received = models.CharField(max_length=3, choices=RECEIVED_CHOICES, default='no')

    """
    “是否收货”字段，用于跟踪订单对应的货物是否已被接收，初始值为False，表示默认未收货，后续可根据实际收货情况更新该值。
    """
    # 新增“是否结单”字段，同样使用BooleanField，用于表示订单是否已经完结，默认值设为False
    CLOSED_CHOICES = [
        ('yes', '是'),
        ('no', '否'),
    ]
    is_closed = models.CharField(max_length=3, choices=CLOSED_CHOICES, default='no')

    """
    “是否结单”字段，用于标识订单是否已完成所有流程处于完结状态，初始值为False，当订单相关的支付、发货、收货等流程都结束后可更新为True。
    """
    # 新增“利润”字段，用DecimalField存储利润数值，可根据实际业务设置其精度等参数
    profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    """
    “利润”字段，用于记录该订单产生的利润情况，设为可为空，因为可能在某些情况下利润计算还未完成或者不适用。
    """
    # 新增“手动状态”字段，可用于记录订单是否处于手动干预等特殊状态，使用BooleanField，默认值设为False
    manual_status = models.CharField(max_length=100, blank=True, null=True)
    """
    “手动状态”字段，用于标记订单是否有需要人工手动处理的特殊情况，初始值为False，若有相关情况可更新为True，便于后续业务逻辑对这类订单进行特殊处理。
    """
    # 新增“审核状态”字段，通过choices参数定义不同的审核状态选项，方便业务流程中对订单审核情况进行管理
    audit_status = models.CharField(max_length=20, choices=[
        ('pending', '待审核'),
        ('approved', '已审核通过'),
        ('rejected', '已审核拒绝'),
    ], default='pending')
    """
    “审核状态”字段，用于跟踪订单在审核环节的状态，初始状态设为 'pending'（待审核），会根据实际审核结果更新为相应的状态值。
    """

    def generate_order_number(self):
        """
        生成订单编号的方法，根据当前日期和随机字符串生成唯一的订单编号
        """
        # 获取当前日期，格式化为 'YYYYMMDD'
        current_date = timezone.now().date().strftime('%Y%m%d')
        # 生成一个随机的字符串部分，这里示例生成6位包含字母和数字的随机字符串
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        return f"{current_date}_{random_part}"

    def save(self, *args, **kwargs):
        """
        重写 save 方法，在保存订单实例前自动生成订单编号（如果还未生成的话）
        """
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-order_date']
        """
        设置模型在管理后台显示的中文名称，以及按照订单创建时间倒序排列的默认排序方式，
        使最新的订单会排在前面，方便查看和管理。
        """