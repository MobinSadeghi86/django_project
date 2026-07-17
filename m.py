from django.db import models
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
class Villa(models.Model):
    villa_id = models.AutoField(primary_key=True)
    host_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    address = models.TextField()
    price_per_night = models.IntegerField()
    capacity = models.IntegerField()
    amenities = models.JSONField()
class Availability(models.Model):
    availability_id = models.AutoField(primary_key=True)
    villa_id = models.ForeignKey(Villa, on_delete=models.CASCADE)
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    class Meta:
        unique_together = ('villa_id', 'date')
class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    guest_id = models.ForeignKey(User, on_delete=models.CASCADE)
    villa_id = models.ForeignKey(Villa, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.IntegerField()
    status = models.CharField(max_length=20, default='pending_payment')
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    reservation_id = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    amount = models.IntegerField()
    status = models.CharField(max_length=20, default='pending')
    gateway_ref = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
class Token(models.Model):
    token_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)