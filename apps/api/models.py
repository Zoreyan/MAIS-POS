from django.db import models

class Payment(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='payments/', null=True, blank=True)
    accepted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.created}. {self.user.shop.name}'