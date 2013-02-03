from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from sorl.thumbnail.admin import AdminImageMixin
import models

class ProducerAdmin(AdminImageMixin, admin.ModelAdmin):
	list_display = ('name', 'contact', 'phone', 'email', 'website', 'active');
	search_fields = ('name', 'phone', 'email', 'website')
	list_filter = ('active',)

	def queryset(self, request):
 		groups = [i.name for i in request.user.groups.all()]
 		if "Producers" in groups:
			return models.Producer.objects.filter(id = request.user.get_profile().producer.id)
		else:
			return models.Producer.objects.all()

	def get_form(self, request, obj=None, **kwargs):
		self.exclude = []	
 		groups = [i.name for i in request.user.groups.all()]
 		if "Producers" in groups and "Admin" not in groups:
			self.exclude.append('markup')
		return super(ProducerAdmin, self).get_form(request, obj, **kwargs)

admin.site.register(models.Producer, ProducerAdmin)

class MessageAdmin(admin.ModelAdmin):
	list_display = ('user', 'date');
	list_filter = ('user',)
	search_fields = ('user', 'text')
admin.site.register(models.Message, MessageAdmin)

class CategoryAdmin(AdminImageMixin, admin.ModelAdmin):
	list_display = ('name', 'active');
	list_filter = ('active',)
	search_fields = ('name',)
admin.site.register(models.Category, CategoryAdmin)

class ProductCycleInline(admin.TabularInline):
	extra = 1
	model = models.ProductCycle

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "product" and "Producers" in [i.name for i in request.user.groups.all()]:
			groupNames = [i.name for i in request.user.groups.all()]
			if "Producers" in groupNames and "Admins" not in groupNames:
				kwargs["queryset"] = models.Product.objects.filter(producer=request.user.get_profile().producer, active=True)
        	return super(ProductCycleInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

	def queryset(self, request):
 		groups = [i.name for i in request.user.groups.all()]
 		if "Producers" in groups and "Admins" not in groups:
			return models.ProductCycle.objects.filter(product__producer = request.user.get_profile().producer).order_by("cycle__date")
		else:
			return models.ProductCycle.objects.all().order_by("cycle__date")

class UnitAdmin(admin.ModelAdmin):
	pass
admin.site.register(models.Unit, UnitAdmin)

class ProductAdmin(AdminImageMixin, admin.ModelAdmin):
	list_display = ('name', 'category', 'producer', 'wholesalePrice', 'site_price', 'taxable', 'active')
	search_fields = ["name", "category__name"]
	list_filter = ('category', 'producer', 'taxable', 'active')
	ordering = ("name",)
	actions = ("activate", "deactivate")
	inlines = (ProductCycleInline,)


	def site_price(self, instance):
		return instance.get_price()

#	def get_readonly_fields(self, request, obj=None):
#		if "Producers" in [i.name for i in request.user.groups.all()]:
#			return ('producer',)

	def activate(self, request, queryset):
		rows_updated = queryset.update(active=True)
		if rows_updated == 1:
			message_bit = "1 product"
		else:
			message_bit = "%s products" % rows_updated
		self.message_user(request, "%s successfully activated." % message_bit)
	activate.short_description = "Mark selected products as activated"
	
	def deactivate(self, request, queryset):
		rows_updated = queryset.update(active=False)
		if rows_updated == 1:
			message_bit = "1 product"
		else:
			message_bit = "%s products" % rows_updated
		self.message_user(request, "%s successfully deactivated." % message_bit)
	deactivate.short_description = "Mark selected products as deactivated"
	
	def get_form(self, request, obj=None, **kwargs):
		self.exclude = []	
 		groups = [i.name for i in request.user.groups.all()]
 		if "Producers" in groups and "Admins" not in groups:
			self.exclude.append('markup')
		if "Admins" not in groups:
			self.exclude.append('membershipExtension')
			self.exclude.append('membershipPayment')
			self.fieldsets = [ ("Basic Info", {"fields": ( "name", "description", "image", "category", "producer")}),
				      ("Additional Info", {"fields": ( "size", "unit", "active", "leadTime", "unlimitedQuantity")}),
				      ("Pricing", {"fields": ( "taxable", "wholesalePrice", "minimumPrice")})]
		else:
			self.fieldsets = [ ("Basic Info", {"fields": ( "name", "description", "image", "category", "producer")}),
					("Additional Info", {"fields": ( "size", "unit", "active", "leadTime", "unlimitedQuantity")}),
					("Pricing", {"fields": ( "taxable", "wholesalePrice", "markup", "minimumPrice")}),
					("Membership", {"fields": ( "membershipPayment", "membershipExtension"), "classes": ["collapse"]})]
		return super(ProductAdmin, self).get_form(request, obj, **kwargs)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "producer" and "Producers" in [i.name for i in request.user.groups.all()]:
			kwargs["queryset"] = models.Producer.objects.filter(userprofile=request.user.get_profile())
        	return super(ProductAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

	def queryset(self, request):
 		groups = [i.name for i in request.user.groups.all()]
 		if "Producers" in groups:
			return models.Product.objects.filter(producer = request.user.get_profile().producer)
		else:
			return models.Product.objects.all()

admin.site.register(models.Product, ProductAdmin)

class CycleAdmin(admin.ModelAdmin):
	inlines = (ProductCycleInline,)
	list_fields=('date',)
	ordering = ('date',)

	def get_readonly_fields(self, request, obj=None):
		groupNames = [i.name for i in request.user.groups.all()]
		if "Admins" not in groupNames and "Producers" in groupNames:
			return ("date", "delivery")
		else:
			return tuple()

admin.site.register(models.Cycle, CycleAdmin)

class OrderItemInlineFormSet(forms.models.BaseInlineFormSet):
	def clean(self):
		prices = [item.quantity * item.price for item in models.OrderItem.objects.filter(order = self.instance.id)]
		oldtotal = sum(prices)
		newtotal = sum([item["quantity"] * item["price"] for item in self.cleaned_data if "DELETE" in item and item["DELETE"] == False])
		if self.instance.paid == True and newtotal > oldtotal:
			raise ValidationError("Can not add to an already charged order. Create a new order")
		return super(OrderItemInlineFormSet, self).clean()

class OrderItemInline(admin.TabularInline):
	model = models.OrderItem	
	#formset = OrderItemInlineFormSet
	extra = 1

class OrderAdminForm(forms.ModelForm):
	class Meta:
		model = models.Order

	def clean(self):
		oldtotal = self.instance.total
		self.instance.update_totals()
		newtotal = self.instance.total
		if self.instance.paid == True and newtotal > oldtotal:
			raise ValidationError("Can not add to an already charged order. Create a new order")
		return super(OrderAdminForm, self).clean()

class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'customer', 'date', 'total', 'paid', 'delivered')
	readonly_fields = ('subtotal', 'tax', 'total', 'processingFee', 'paymentId', 'paid')
	inlines = (OrderItemInline,)
	list_filter = ('date', 'paid', 'delivered')
	actions = ("delivered", "refund", "charge")
	#form = OrderAdminForm

	def get_actions(self, request):
		actions = super(OrderAdmin, self).get_actions(request)
 		groups = [i.name for i in request.user.groups.all()]
		if "Admin" in groups:
			if 'charge' in actions:
				del actions['charge']
			if 'refund' in actions:
				del actions['refund']
		return actions

	def delivered(self, request, queryset):
		rows_updated = queryset.update(delivered=True)
		if rows_updated == 1:
			message_bit = "1 order"
		else:
			message_bit = "%s orders " % rows_updated
		self.message_user(request, "%s successfully delivered." % message_bit)
	delivered.short_description = "Mark selected orders as delivered"

	def refund(self, request, queryset):
		errors = 0
		for order in queryset:
			try:
				order.fullRefund()
			except models.ChargeError:
				errors += 1
		if errors > 0:
			self.message_user(request, "Error refunding %s orders" % errors)
		else:
			self.message_user(request, "Succesfully refunded all orders")
	refund.short_description = "Refund selected orders"

	def charge(self, request, queryset):
		errors = 0
		for order in queryset:
			try:
				order.charge()
			except:
				errors += 1
		if errors > 0:
			self.message_user(request, "Error charging %s orders" % errors)
		else:
			self.message_user(request, "Succesfully charged all orders")
	charge.short_description = "Charge selected orders"

admin.site.register(models.Order, OrderAdmin)

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
 
admin.site.unregister(User)
 
class UserProfileInline(admin.StackedInline):
	model = models.UserProfile
 
class UserProfileAdmin(UserAdmin):
	list_display = ('username',"first_name", "last_name", "is_staff", "producer", "is_member")
	inlines = [UserProfileInline]
	exclude = ["user_permissions", "is_superuser"]
	list_filter = ('is_staff', 'is_active', 'producer')

	def is_member(self, instance):
		return instance.get_profile().is_member()
	is_member.boolean = True

	def producer(self, instance):
		return instance.get_profile().producer

	def get_form(self, request, obj=None, **kwargs):
		fieldsets = super(UserProfileAdmin, self).fieldsets
		for i in fieldsets:
			i[1]["fields"] = [field for field in i[1]["fields"] if field not in self.exclude]
		return super(UserProfileAdmin, self).get_form(request, obj, **kwargs)
 
admin.site.register(User, UserProfileAdmin)

class SettingAdmin(admin.ModelAdmin):
	list_display = ('key', 'value')
	search_fields = ('key', 'value')
admin.site.register(models.Setting,SettingAdmin)

class AboutImageInline(AdminImageMixin, admin.StackedInline):
	model = models.AboutImage
	extra = 1

class AboutPageAdmin(admin.ModelAdmin):
	inlines = [AboutImageInline]
	prepopulated_fields = {"slug": ("title",)}
	list_display = ("title", "defaultPage")
	search_fields = ('title', 'content')

admin.site.register(models.AboutPage, AboutPageAdmin)

