from .models import User, CategoryType, CategoryItem, Order, Status, OrderItem
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'name', 'phone', 'email', 'address', 'zip', 'role', 'is_signed_in', 'sign_in_time', 'sign_out_time', 'session_id')

class CategoryTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CategoryType
        fields = ('id', 'name')

class CategoryItemSerializer(serializers.HyperlinkedModelSerializer):
    type = CategoryTypeSerializer() 
    supplier = UserSerializer()

    class Meta:
        model = CategoryItem
        fields = ('id', 'name', 'type', 'ingredient', 'indication', 'contraindication', 'dosage', 'side_effects', 'carefull', 'drug_interactions', 'preserve', 'supplier', 'price', 'quantity', 'photo', 'is_available', 'is_new')

class StatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Status
        fields = ('id', 'name')

class OrderSerializer(serializers.HyperlinkedModelSerializer):
    customer = UserSerializer()
    status = StatusSerializer()

    class Meta:
        model = Order
        fields = ('id', 'customer', 'order_time', 'status', 'is_paid', 'total_cost')

class OrderItemSerializer(serializers.HyperlinkedModelSerializer):
    order = OrderSerializer()
    category = CategoryItemSerializer()

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'category', 'quantity', 'sub_total_cost')