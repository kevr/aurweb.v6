from django.test import TestCase, TransactionTestCase

from packages.models import *

class PackagesViewTest(TestCase):

  def test_index(self):
    response = self.client.get("/packages/")
    self.assertEqual(response.status_code, 200)

  def test_o(self):
    response = self.client.get("/packages/?O=0")
    self.assertEqual(response.status_code, 200)

# Create your tests here.
