from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender='order_management.User')
def set_role(sender, instance, **kwargs):
   
    username = instance.username
    while username[-1].isdigit():
        username = username[:-1]
    role = username

    instance.role = role