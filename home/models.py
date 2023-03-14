from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    total_ads = models.IntegerField()
    category_image = models.ImageField()

    def __str__(self):
        return str(self.name) + '(' + str(self.total_ads) + ')'


class Advertisement(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    state = models.CharField(max_length=20, default="Brand New")
    description = models.CharField(max_length=1000)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_on = models.DateField()
    negotiable = models.BooleanField(default=True)
    used_for = models.CharField(max_length=100)
    warranty = models.CharField(max_length=100)
    premium_ad = models.BooleanField()
    product_image = models.ImageField()
    price = models.FloatField()
    views = models.IntegerField(default=0)
    sold = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Comments(models.Model):
    product = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_on = models.DateField()
    description = models.CharField(max_length=1000)


class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    num_of_clicks = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        locked = self.rating == 5
        if not locked:
            if self.num_of_clicks >= 10:
                self.rating = 5
            elif 10 > self.num_of_clicks >= 8:
                self.rating = 4
            elif 8 > self.num_of_clicks >= 6:
                self.rating = 3
            elif 6 > self.num_of_clicks >= 3:
                self.rating = 2
            elif 3 > self.num_of_clicks >= 1:
                self.rating = 1
        super(UserRating, self).save(*args, **kwargs)


class Replies(models.Model):
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_on = models.DateField()
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
