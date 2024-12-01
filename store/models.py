from django.db import models

from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

from userauths import models as user_models


import shortuuid

STATUS = (
    ('Published', 'Published'),
    ('Draft', 'Draft'),
    ('Disabled', 'Disabled'),
)

PAYMENT_STATUS = (
    ('Paid', 'Paid'),
    ("Processing", 'Processing'),
    ('Failed', 'Failed'),
    
)

PAYMENT_METHOD = (
    ('Stripe', 'Stripe'),
    ('PayPal', 'PayPal'),
    ('Flutterwave', 'Flutterwave'),
    ('Paystack', 'Paystack'),
)

ORDER_STATUS = (
    ('Pending', 'Pending'),
    ('Processing', 'Processing'),
    ('Shipped', 'Shipped'),
    ('Fulfilled', 'Fulfilled'),
    ('Cancelled', 'Cancelled'),

)

SHIPPING_SERVERS = (
    ('Fedex', 'Fedex'),
    ('UPS', 'UPS'),
    ('DHL', 'DHL'),
    ('Amazon', 'Amazon'),
    ('Other', 'Other'),
)

RATING = (
    (1, '🌟⭐⭐⭐⭐'),
    (2, '🌟🌟⭐⭐⭐'),
    (3, '🌟🌟🌟⭐⭐'),
    (4, '🌟🌟🌟🌟⭐'),
    (5, '🌟🌟🌟🌟🌟'),
)




class Category(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="image/category", blank=True, null=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['title']


class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="images", blank=True, null=True, default="product.jpg")
    description = models.TextField("Text")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    regular_price = models.DecimalField(max_digits=12, decimal_places=2,default=0.00,null=True, blank=True)
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=50, default="Published")
    featured = models.BooleanField(default=False, verbose_name="Marketplace Featured")
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)
    sku = ShortUUIDField(unique=True, length=5, max_length=50, prefix = "Dev", alphabet="1234567890")
    slug = models.SlugField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-id']
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + '-' + str(shortuuid.uuid().lower()[:2])
        super().save(*args, **kwargs)


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=1000, verbose_name="Variant name", blank=True, null=True)

    def items(self):
        return VariantItem.objects.filter(variant=self)
    

class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="variant_items")
    title = models.CharField(max_length=1000, verbose_name="Item Title", blank=True,null=True)
    content = models.CharField(max_length=1000, verbose_name="Item Content", blank=True, null=True)

    def __str__(self):
        return self.variant.name

class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    image = models.FileField(upload_to='images', default='gallery.jpg')
    galley_id = ShortUUIDField(length=6, max_length=10, alphabet="1234567890")



    def __str__(self):
        return f"{self.product.name} - image"
    
    class Meta:
        verbose_name_plural = "Gallery"
    


class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(user_models.User, on_delete=models.CASCADE, null=True,blank=True)
    qty = models.PositiveIntegerField(default=0, null=True,blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00,blank=True, null=True)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, blank=True, null=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    card_id = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.card_id} - {self.product.name}"
    


class Coupon(models.Model):
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=100)
    discount = models.IntegerField(default=2)



    def __str__(self):
        return self.code
    

class Order(models.Model):
    vendors = models.ManyToManyField(user_models.User, blank=True)
    customer = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True, related_name="customer")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2,default=0.00)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    service_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="Processing")
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD, default=None, null=True, blank=True)
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default="Pending")
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0.00, help_text="Grand Total of all amount")
    saved = models.DecimalField(max_digits=12, decimal_places=2,default=0.00, null=True, blank=True, help_text="Amount to be saved")
    # address = models.ForeignKey("customer.Address", on_delete=models.SET_NULL, null=True, blank=True)
    coupons = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    order_id = ShortUUIDField(length=6, max_length=25, alphabet="1234567890")
    payment_id = models.CharField(null=True, blank=True, max_length=1000)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Order"
        ordering = ['-date']

    def __str__(self):
        return self.order_id
    

    def order_items(self):
        return OrderItem.objects.filter(order=self)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default='Pending')
    shipping_service = models.CharField(max_length=100, choices=SHIPPING_SERVERS, default=None, null=True, blank=True)
    tracking_id = models.CharField(max_length=100, default=None, null=True, blank=True)


    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(default=0)
    color = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Grand Total of all amount")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    applied_coupon = models.BooleanField(default=False)
    item_id = ShortUUIDField(length=6, max_length=25,alphabet="1234567890")
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, blank=True, null=True, related_name="vendor_order_items")
    date = models.DateTimeField(default=timezone.now)
    # order_id = ShortUUIDField(length=6, max_length=25, alphabet="1234567890")
    # payment_id = models.CharField(null=True, blank=True, max_length=1000)


    def order_id(self):
        return f"{self.order.order_id}"

    
    def __str__(self):
        return self.item_id

    class Meta:
        ordering = ('-date',)

class Review(models.Model):
    user = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True, related_name="reviews")
    review = models.TextField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)
    rating = models.IntegerField(choices=RATING, default=None)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} review on {self.product.name}"