from django.core.management.base import LabelCommand, CommandError
import csv
from coopshop.models import Product

class Command(LabelCommand):
	help = "Update products in the database from a CSV file"

	def handle_label(self, label, **options):
		self.stdout.write("updating Products from %s\n" % label)
		Product.updateProducts(csv.DictReader(open(label)))
