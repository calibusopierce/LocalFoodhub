from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(null=True, blank=True, upload_to='profile_pic/')
    stall_name = models.CharField(max_length=100, default=None, null=True, blank=True)
    fname = models.CharField(max_length=50, null=True, blank=True)
    lname = models.CharField(max_length=50, null=True, blank=True)
    bday = models.DateField(null=True, blank=True)
    brgy = models.CharField(max_length=50, null=True, blank=True)
    full_address = models.CharField(max_length=50, null=True, blank=True)
    delivery_address = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self) :
        return self.fname + " : " + self.lname 



class ProductList(models.Model):
    stall_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id  = models.CharField(max_length=50, blank=True, primary_key=True)
    product_image = models.ImageField(null=True, blank=True, upload_to='product_images/')
    product_name = models.CharField(max_length=50, null=True, blank=True)
    product_price = models.IntegerField()
    stocks = models.IntegerField()

    def __str__(self) :
        return str(self.stall_owner.customer.stall_name) + " : " + str(self.product_name) + " : " + str(self.product_price)


class AddedToCart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductList, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_of_items = models.IntegerField(default=0)
    is_pending = models.BooleanField(default=True)
    is_selected = models.BooleanField(default=False)
    is_ordered = models.BooleanField(default=False)
    date_added = models.DateTimeField()
    cart_id = models.CharField(primary_key= True, max_length=255, unique=True, default=None)
    order_id = models.CharField(max_length = 255, blank = True, null = True, default = None)

    def save(self, *args, **kwargs):
        self.total_items = self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return "Is-Pending : " + str(self.is_pending) + " : " + str(self.customer.fname) + " : " + str(self.product.product_name) + " : " + str(self.quantity)



class Orders(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shop_owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    total = models.IntegerField()
    total_orders = models.IntegerField(default=0)
    estimated_time = models.IntegerField()
    date_ordered = models.DateTimeField()
    order_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.customer.fname) + " : " + str(self.customer.delivery_address) + " : Total : " + str(self.total) + " : " + str(self.estimated_time)


class Logo(models.Model):
    logo = models.ImageField(null=True, blank = True, upload_to = "images/")

    def __str__(self):
        return str(self.logo)      