from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.contrib.localflavor.us.models import PhoneNumberField,USStateField
from sorl.thumbnail import ImageField
from decimal import *
import datetime
import stripe

TWOPLACES=Decimal(10) ** -2

class CycleException(Exception):
	pass

class Cycle(models.Model):
	date	 	= models.DateField()
	delivery 	= models.DateField()

	class Meta:
		ordering = ["date"]

	@classmethod
	def getCurrentCycle(cls):
		try:
			return cls.objects.filter(date__gte = datetime.date.today()).order_by("date")[0]
		except IndexError:
			raise CycleException()

	def __unicode__(self):
		return str(self.date)

class Producer(models.Model):
	name		= models.CharField(max_length=128)
	contact		= models.ForeignKey(User)
	#Product types
	about		= models.TextField(help_text="Html and <a href='http://en.wikipedia.org/wiki/Markdown'>markdown</a> are allowed")
	address		= models.CharField(max_length=128)
	city		= models.CharField(max_length=64)
	zip		= models.CharField(max_length=10)
	state		= USStateField()
	phone		= PhoneNumberField()
	email		= models.EmailField()
	website		= models.URLField()
	active		= models.BooleanField(default=True)
	image		= ImageField(upload_to="producers")
	markup		= models.DecimalField(max_digits=10,decimal_places=3, blank=True, null=True)
	leadTime	= models.IntegerField(default=0)

	@models.permalink
	def get_absolute_url(self):
		return ('coopshop.views.producer', [str(self.id)])

	def __unicode__(self):
		return self.name

class Category(models.Model):
	name		= models.CharField(max_length=64)
	active		= models.BooleanField(default=True)
	image		= ImageField(upload_to="categories")

	@models.permalink
	def get_absolute_url(self):
		return ('coopshop.views.category', [str(self.id)])

	class Meta:
		verbose_name_plural = "Categories"
		ordering = ["name"]

	def __unicode__(self):
		return self.name


class ProductCycle(models.Model):
	product		= models.ForeignKey('Product')
	cycle		= models.ForeignKey('Cycle')
	quantity	= models.IntegerField()

class Unit(models.Model):
	name		= models.CharField(max_length=32, unique=True)

	def __unicode__(self):
		return self.name

class Product(models.Model):
	name		= models.CharField(max_length=64)
	size		= models.DecimalField(max_digits=10,decimal_places=3, blank=True, null=True)
	#unit		= models.CharField(max_length=32, blank=True, null=True, choices = (
	#										("pound", "pound"),
	#										("gallon", "gallon"),
	#										("dozen", "dozen"),
	#										("half dozen", "half dozen"),
	#										("each", "each"),
	#										("bundles", "bundles"),
	#										("box", "box"),
	#										("carton", "carton"),
	#										("bag", "bag"),
	#										("ounces", "ounces"),
	#										("liters", "liters"),
	#										("","")))
	unit		= models.ForeignKey(Unit)
	description	= models.TextField(help_text="Html and <a href='http://en.wikipedia.org/wiki/Markdown'>markdown</a> are allowed")
	image		= ImageField(upload_to="products", blank=True, null=True, help_text="If an image is not provided, the category image will be used in its place")
	category	= models.ForeignKey(Category)
	producer	= models.ForeignKey(Producer)
	membershipPayment = models.BooleanField(verbose_name="Membership Payment", help_text="If selected, the item price is applied toward a membership")
	membershipExtension = models.IntegerField(blank=True, null=True, verbose_name="Membership Extension", help_text="If this item is a membership Item, the number of days this item extends the user's membership")
	taxable		= models.BooleanField()
	active		= models.BooleanField(default=True)
	wholesalePrice	= models.DecimalField(verbose_name="Wholesale Price", max_digits=10,decimal_places=2, help_text="Wholesale price the Coop pays to the producer")
	markup		= models.DecimalField(max_digits=10,decimal_places=3, blank=True, null=True, help_text="Markup to apply to the wholesale price. If this isn't set, the producer markup is used")
	minimumPrice 	= models.DecimalField(verbose_name="Minimum Price", max_digits=10,decimal_places=2, blank=True, null=True, help_text="Minimum price that the product will be sold for")
	leadTime	= models.IntegerField(verbose_name="Lead Time", blank=True, null=True, help_text="Number of days before the end of the cycle that the product will become unavailable")
	unlimitedQuantity = models.BooleanField(verbose_name="Unlimited Quantity", help_text="Item doesn't run out of stock")
	cycles	 	= models.ManyToManyField(Cycle, through=ProductCycle)
	
	class Meta:
		ordering = ["name"]

	def get_image(self):
		if self.image:
			return self.image
		else:
			return self.category.image

	def get_leadTime(self):
		leadTime = self.leadTime
		if leadTime == None:
			leadTime =  self.producer.leadTime
		return leadTime

	def get_orderByDate(self):
		cycle = Cycle.getCurrentCycle()
		return cycle.date - datetime.timedelta(self.get_leadTime())

	def get_price(self):
		markup = self.markup
		if markup == None:
			markup = self.producer.markup
		if markup == None:
			markup = Decimal(Setting.objects.get(key = "markup").value)
		price = (self.wholesalePrice * (markup + 1)).quantize(TWOPLACES)
		if self.minimumPrice != False and price < self.minimumPrice:
			return self.minimumPrice
		else:
			return price

	def get_quantity(self, date = None): #todo get quantity at a future date
		if date == None:
			cycle = Cycle.getCurrentCycle()
		
		if cycle.date - datetime.timedelta(self.get_leadTime()) < datetime.date.today():
			return 0
		else:
			try:
				return ProductCycle.objects.get(cycle = cycle, product = self).quantity
			except:
				return 0
	def get_remaining(self):
		startingQuantity = self.get_quantity()
		numOrdered = OrderItem.objects.filter(order__cycle = Cycle.getCurrentCycle(), product = self).aggregate(models.Sum("quantity"))["quantity__sum"]
		try:
			return startingQuantity - numOrdered
		except TypeError:
			return startingQuantity

	@models.permalink
	def get_absolute_url(self):
		return ('coopshop.views.product', [str(self.id)])

	def __unicode__(self):
		return "%s (%s)" % (self.name, self.producer.name)

class ChargeError(Exception):
	pass

class Order(models.Model):
	date		= models.DateTimeField(auto_now_add=True)
	customer	= models.ForeignKey(User)
	products	= models.ManyToManyField(Product, through="OrderItem")
	subtotal	= models.DecimalField(max_digits=10,decimal_places=2,blank=True)
	tax		= models.DecimalField(max_digits=10,decimal_places=2,blank=True)
	total		= models.DecimalField(max_digits=10,decimal_places=2,blank=True)
	cycle		= models.ForeignKey(Cycle)
	paid		= models.BooleanField(default=False)
	delivered	= models.BooleanField(default=False)
	paymentId	= models.CharField(max_length=32,default=False, null=True)
	nonmemberFee	= models.DecimalField(verbose_name="Nonmember Fee", max_digits=10,decimal_places=2,blank=True)
	deliveryFee	= models.DecimalField(verbose_name="Delivery Fee", max_digits=10,decimal_places=2,blank=True)
	processingFee	= models.DecimalField(verbose_name="Processing Fee", max_digits=10,decimal_places=2,blank=True,default=0)

	def charge(self):
		if self.paid == True:
			raise ValidationError("Can't charge and order more than once")

		self.update_totals()
		stripe.api_key = Setting.objects.get(key="Stripe Secret Key").value
		profile = self.customer.get_profile()
        	customer = profile.stripeId
		try:
			charge = stripe.Charge.create(	amount=int(self.total*100),
							currency="usd",
							customer=customer)
		except Esception, e:
			raise ChargeError(e)
		if charge:
			memberItems = OrderItem.objects.filter(order = self.id, product__membershipPayment = True)
			if len(memberItems) > 0:
				profile = self.customer.get_profile()
				profile.membershipBalance += sum([orderItem.price * orderItem.quantity for orderItem in memberItems])
				try:
					profile.membershipExpires += datetime.timedelta(days=sum([orderItem.product.membershipExtension * orderItem.quantity for orderItem in memberItems]))
				except TypeError:
					profile.membershipExpires = datetime.date.today() + datetime.timedelta(days=int(sum([orderItem.product.membershipExtension * orderItem.quantity for orderItem in memberItems])))
				profile.save()
			self.paid = True
			self.paymentId = charge["id"]
			self.processingFee = (Decimal(charge["fee"])/100).quantize(TWOPLACES)
		self.save()

	def fullRefund(self):
		if not self.paid or self.paymentId == None:
			raise ValidationError("Can't refund an order that hasn't been paid")

		stripe.api_key = Setting.objects.get(key="Stripe Secret Key").value

		try:
			charge = stripe.Charge.retrieve(self.paymentId)
			charge.refund()
			self.paid = False
			memberItems = OrderItem.objects.filter(order = self.id, product__membershipPayment = True)
			if len(memberItems) > 0:
				profile = self.customer.get_profile()
				profile.membershipBalance -= sum([orderItem.price * orderItem.quantity for orderItem in memberItems])
				profile.membershipExpires -= datetime.timedelta(days=sum([orderItem.product.membershipExtension * orderItem.quantity for orderItem in memberItems]))
				profile.save()
		except Exception, e:
			raise ChargeError(e)
		self.save()

	def refundDifference(self):
		if not self.paid or self.paymentId == None:
			raise ValidationError("Can't refund an order that hasn't been paid")

		stripe.api_key = Setting.objects.get(key="Stripe Secret Key").value
		try:
			charge = stripe.Charge.retrieve(self.paymentId)
			refundAmount = charge["amount"] - charge["amount_refunded"] - int(self.total * 100)
			if refundAmount > 0:
				charge.refund(amount = refundAmount)
		except Exception, e:
			raise ChargeError(e)

	def update_totals(self):
		if not self.customer.get_profile().is_member() and OrderItem.objects.filter(order = self.id, product__membershipPayment = True).count() > 0:
			self.nonmemberFee = Decimal(Setting.objects.get(key="Nonmember Fee").value).quantize(TWOPLACES)
		else:
			self.nonmemberFee = 0
		self.deliveryFee = 0
		self.subtotal = sum([(product.price * product.quantity).quantize(TWOPLACES) for product in OrderItem.objects.filter(order = self.id)])
		tax = Decimal(Setting.objects.get(key = "tax").value)
		self.tax = sum([(product.price * product.quantity * tax).quantize(TWOPLACES) for product in OrderItem.objects.filter(order = self.id, product__taxable = True)])
		self.total = self.subtotal + self.tax + self.deliveryFee + self.nonmemberFee

	def save(self):
		self.update_totals()
		if self.paid == True:
			dbtotal = Order.objects.get(id=self.id).total
			if self.total < dbtotal:
				self.refundDifference()
			elif self.total > dbtotal:
				raise ValidationError("Can not add to an already charged order.  Create a new order")
		super(Order, self).save()

	def delete(self):
		if self.paid == True:
			self.fullRefund()
		super(Order, self).delete()

	@models.permalink
	def get_absolute_url(self):
		return ('coopshop.views.order', [str(self.id)])

class OrderItem(models.Model):
	product		= models.ForeignKey(Product)
	order		= models.ForeignKey(Order)
	quantity	= models.DecimalField(max_digits=10,decimal_places=2)
	wholesalePrice	= models.DecimalField(max_digits=10,decimal_places=2,blank=True)
	price		= models.DecimalField(max_digits=10,decimal_places=2,blank=True)

	def save(self):
		if self.wholesalePrice == None:
			self.wholesalePrice = self.product.wholesalePrice

		if self.price == None:
			self.price = self.product.get_price()

		if self.order.paid == True:
			dbtotal = OrderItem.objects.get(id=self.id).price
			if self.price > dbtotal:
				raise ValidationError("Can not add to an already charged order.  Create a new order")
		super(OrderItem, self).save()
		self.order.save()

	def delete(self):
		order = self.order
		super(OrderItem, self).delete()
		order.save()

class UserProfile(models.Model):
	user		= models.ForeignKey(User, unique=True)
	phone		= PhoneNumberField()
	address1	= models.CharField(max_length=128)
	address2	= models.CharField(max_length=128, null=True, blank=True)
	city		= models.CharField(max_length=128)
	state		= USStateField()
	zip		= models.CharField(max_length=10)
	membershipExpires = models.DateField(verbose_name="Membership Expires", null=True, blank=True, help_text="When this user's membership expires")
	lifetimeMember	= models.BooleanField(default=False, help_text="If set, this user will always be a member")
	membershipBalance = models.DecimalField(verbose_name="Membership Balance", max_digits=10, decimal_places=2, default=0, help_text="The amount this user has contributed to the Co-op")
	producer	= models.ForeignKey(Producer, null=True, blank=True)
	stripeId	= models.CharField(max_length=32, null=True, blank=True)

	def is_member(self):
		if self.lifetimeMember:
			return True
		else:
			try:
				return self.membershipExpires >= datetime.date.today()
			except TypeError:
				return False

	def update_card(self, stripeToken):
		stripe.api_key = Setting.objects.get(key="Stripe Secret Key").value
		if self.stripeId:
		        try:
				customer = stripe.Customer.retrieve(profile.stripeId)
				customer.card = stripeToken
				customer.save()
		        except:
		                self.create_charge_account(stripeToken)
		else:
	                self.create_charge_account(stripeToken)

	def get_card(self):
		stripe.api_key = Setting.objects.get(key="Stripe Secret Key").value
		if self.stripeId:
		        try:
				customer = stripe.Customer.retrieve(profile.stripeId)
				return customer.card
		        except:
		                return None

	def create_charge_account(self, stripeToken):
		stripe.api_key = Setting.objects.get(key="Stripe Secret Key").value
		customer = stripe.Customer.create(      card=stripeToken,
		                                        description = self.user.email,
		                                        email = self.user.email)
		self.stripeId = customer["id"]
		self.save()

	def get_card(self):
		stripe.api_key = Setting.objects.get(key="Stripe Secret Key").value
		if self.stripeId: 
			try:
				return stripe.Customer.retrieve(self.stripeId)["active_card"]
			except:
				return None
		else:
			return None
		
	def save(self):
		if self.membershipBalance > Decimal(Setting.objects.get(key = "Lifetime Membership Cost").value):
			self.lifetimeMember = True
		super(UserProfile, self).save()

class MessageCategory(models.Model):
	name		= models.CharField(max_length=64)
	contact		= models.ForeignKey(User, null=True, blank=True)

	class Meta:
		verbose_name_plural = "Message Categories"
		ordering = ["name"]
	
	def __unicode__(self):
		return self.name

class Message(models.Model):
	user		= models.ForeignKey(User)
	category	= models.ForeignKey(MessageCategory)
	date	 	= models.DateField(default=datetime.date.today)
	responded	= models.BooleanField(default=False)
	text		= models.TextField()

	class Meta:
		ordering = ["date"]

	def send_message(self):
		send_mail(self.category.name, "Message from: %s\n%s" % (self.user.email, self.text), "website@atomiccoop.org", [self.category.contact.email])

	def save(self):
		if self.id:
			oldMessage = Messaage.objects.filter(id = self.id)
			if self.category != oldMessage.category or text.category != oldMessage.category:
				self.send_message()
		else:
			self.send_message()
		super(Message, self).save()

class Setting(models.Model):
	key		= models.CharField(max_length=128)
	value		= models.TextField()

	def __unicode__(self):
		return self.key

class AboutPage(models.Model):
	title		= models.CharField(max_length=128)
	slug		= models.SlugField()
	content		= models.TextField(help_text="Page contents.  Html and <a target='_blank' href='http://en.wikipedia.org/wiki/Markdown'>markdown</a> are allowed<br/>To insert an image, attach it to the page and put a reference to it in the page with the following format: ![Alt text][Name] where Alt text is a simple description of the image and Name is the name of the image")
	defaultPage	= models.BooleanField()

	def __unicode__(self):
		return self.title

	@models.permalink
	def get_absolute_url(self):
		return ('coopshop.views.about', [self.title])

	def save(self):
		if self.defaultPage:
			try:
				temp = AboutPage.objects.get(defaultPage=True)
				if self != temp:
					temp.defaultPage = False
					temp.save()
			except DoesNotExist:
				pass
		super(AboutPage, self).save()

class AboutImage(models.Model):
	page		= models.ForeignKey(AboutPage)
	name		= models.CharField(max_length=32)
	image		= ImageField(upload_to="about")
