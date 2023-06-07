from django.db import models
from django.utils import timezone

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=255)
    zip = models.CharField(max_length=10, null=True, blank=True)
    role = models.CharField(max_length=20)
    is_signed_in = models.BooleanField(default=False)
    sign_in_time = models.DateTimeField(null=True, blank=True)
    sign_out_time = models.DateTimeField(null=True, blank=True)
    session_id = models.CharField(max_length=32, null=True, blank=True)

    def sign_in(self, session_id):
        self.is_signed_in = True
        self.sign_in_time = timezone.now()
        self.session_id = session_id
        self.save()

    def sign_out(self):
        self.is_signed_in = False
        self.sign_out_time = timezone.now()
        self.session_id = None
        self.save()

    def __str__(self):
        return self.username

class CategoryType(models.Model):
    name = models.CharField(max_length=255)

class CategoryItem(models.Model):
    name = models.CharField(max_length=255)
    type = models.ForeignKey(CategoryType, on_delete=models.CASCADE, default=1)
    ingredient = models.CharField(max_length=255)
    indication = models.CharField(max_length=255)
    contraindication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    side_effects = models.CharField(max_length=255)
    carefull = models.CharField(max_length=255)
    drug_interactions = models.CharField(max_length=255)
    preserve = models.CharField(max_length=255)
    supplier = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.IntegerField(default=100)
    photo = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    is_new = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Status(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    order_time = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def get_total_cost(self):
        total = sum(item.sub_total_cost for item in self.order_items.all())
        self.total_cost = total
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    category = models.ForeignKey(CategoryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    sub_total_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.quantity} x {self.category.name}'
    
    def get_subtotal_cost(self):
        sub_total = self.category.price * self.quantity
        self.sub_total_cost = sub_total
        self.save()