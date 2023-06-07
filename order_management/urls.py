from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'categorytypes', views.CategoryTypeViewSet, basename='categorytypes')
router.register(r'categoryitems', views.CategoryItemViewSet, basename='categoryitems')
router.register(r'status', views.StatusViewSet, basename='status')
router.register(r'orders', views.OrderViewSet, basename='orders')
router.register(r'orderitems', views.OrderItemViewSet, basename='orderitems')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),


    path('', views.localhost, name='localhost'),
    path('accounts/login/', views.signin, name='signin'),
    path('page/<str:username>/', views.homepage, name='homepage'),
    path('page/<str:username>/addlink/', views.supplier_add, name='addlink'),
    path('page/<str:username>/manlink/', views.manager, name='manlink'),
    path('page/<str:username>/accept/<int:order_id>/<int:status_id>/', views.accept, name='accept'),
    path('page/<str:username>/viewlink/<str:range>/', views.supplier_view, name='viewlink'),
    path('page/<str:username>/logout/', views.signout, name='signout'),
    path('page/<str:username>/profile/', views.profile, name='profile'),
    path('page/<str:username>/cart/', views.cart, name='cart'),
    path('page/<str:username>/payment/', views.payment, name='payment'),
    path('page/<str:username>/product/<int:item_id>/', views.product, name='product'),
    path('page/<str:username>/<int:item_id>/<int:quantity>/', views.additem, name='additem'),
    path('page/<str:username>/delete/<int:item_id>/', views.deleteitem, name='deleteitem'),
    path('page/<str:username>/deleteorder/', views.deleteorder, name='deleteorder'),
    path('page/<str:username>/update/<int:item_id>/<int:quantity>/', views.updateitem, name='updateitem'),
]