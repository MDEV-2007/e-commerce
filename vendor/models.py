from django.db import models

from shortuuid.django_fields import ShortUUIDField
from userauths.models import User
from django.utils.text import slugify

# from store.models import OrderItem


NOTIFICATION_TYPE = (
    ('New Order', 'New Order'),
    ('New Review', 'New Review'),
    
)
PAYOUT_METHOD = (
    ('PayPal', 'PayPal'),
    ('Stripe', 'Stripe'),
    ('Bank Transfer', 'Bank Transfer'),
    ('Uzbekistan Bank Account', 'Uzbekistan Bank Account'),
    ('Korean Bank Account', 'Korean Bank Account'),
    ('Western Union', 'Western Union'),
    ('American Express', 'American Express'),
)

TYPE = (
    ('New Order', 'New Order'),
    ("Item Shipped", 'Item Shipped'),
    ("Item Delivered", 'Item Delivered'),
)

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name='vendor')
    image = models.ImageField(upload_to='vendor', default='shop-image.jpg', blank=True, null=True)
    store_name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True,null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    vendor_id = ShortUUIDField(unique=True, length=6, max_length=20, alphabet="1234567890")
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True, null=True)


    def __str__(self):
        return str(self.store_name)
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.store_name)
        super(Vendor, self).save(*args, **kwargs)

class Payout(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey("store.OrderItem", on_delete=models.SET_NULL,null=True, related_name="item")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payout_id = ShortUUIDField(unique=True, max_length=6,length=6, alphabet="1234567890")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.vendor)
    
    class Meta:
        ordering = ('-date',)

class BankAccount(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.SET_NULL, null=True)
    account_type = models.CharField(max_length=100, choices=PAYOUT_METHOD,blank=True, null=True)
    bank_name = models.CharField(max_length=500)
    account_number = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=100, null=True, blank=True)

    stripe_id = models.CharField(max_length=100, null=True, blank=True)
    paypal_address = models.CharField(max_length=100, null=True,blank=True)

    class Meta:
        verbose_name = "Bank Account"

    def __str__(self):
        return self.bank_name
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='vendor_notifications')
    type = models.CharField(max_length=100, choices=TYPE, default=None)
    order = models.ForeignKey('store.OrderItem', on_delete=models.CASCADE, null=True, blank=True)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return self.type
        