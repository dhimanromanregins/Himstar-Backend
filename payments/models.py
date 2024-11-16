# from django.db import models
# from accounts.models import Register
# # Create your models here.
#
#
# class Account(models.Model):
#     user = models.OneToOneField(Register, on_delete=models.CASCADE, related_name="account")
#     account_number = models.CharField(max_length=20, unique=True)
#     bank_name = models.CharField(max_length=100)
#     branch_name = models.CharField(max_length=100, blank=True, null=True)
#     ifsc_code = models.CharField(max_length=11)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"{self.user.user.username}'s Account ({self.account_number})"
#
#
#
# class PaymentDetails(models.Model):
#     txn_id = models.CharField(max_length=255, unique=True)
#     mihpayid = models.CharField(max_length=255, null=True, blank=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     mode = models.CharField(max_length=50)
#     product_info = models.CharField(max_length=255)
#     firstname = models.CharField(max_length=255, null=True, blank=True)
#     email = models.EmailField()
#     phone = models.CharField(max_length=15)
#     status = models.CharField(max_length=50)
#     coupon = models.CharField(max_length=255, null=True, blank=True)
#     card_category = models.CharField(max_length=50, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Payment {self.txn_id} - {self.status}"