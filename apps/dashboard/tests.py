from django.test import TestCase, Client
from django.urls import reverse
from apps.user.models import User
from apps.history.models import SoldHistory
from apps.product.models import Shop, Product

class DahboardTestCase(TestCase):
    def setUp(self):
        self.client = 