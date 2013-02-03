from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template import RequestContext
from django.utils.http import urlquote
from django.core import serializers
from django.db.models import Sum,Q
from django import forms
try:
	from simplejson import json
except ImportError:
	import json
from coopshop import models
import decimal
import urllib
import re

TWOPLACES = decimal.Decimal(10) ** -2

#From http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def index(request):
	return redirect("/categories");

def get_footer():
	return models.Setting.objects.get(key="Footer Text").value
	
def user(request, user):
	if request.user.is_authenticated():
		if request.user.groups.filter(name="Admins") or request.user.id == user:
			try:
				user = User.objects.get(username = user)
			except ObjectDoesNotExist:
				raise Http404
			orders = models.Order.objects.filter(customer = user)
			return render_to_response(	"acct.html",
							{
								#"breadcrumbs": [product.category, product],
								"user": user,
								"orders": orders,
								"cycle": models.Cycle.getCurrentCycle(),
								"card": user.get_profile().get_card(),
								"footer": get_footer()
							},
							context_instance=RequestContext(request))
	raise Http404
def product(request, product):
	try:
		product = models.Product.objects.get(id = product, active=True)
	except ObjectDoesNotExist:
		raise Http404
	return render_to_response(	"product.html",
					{
						"breadcrumbs": [product.category, product],
						"product": product,
						"cycle": models.Cycle.getCurrentCycle(),
						"footer": get_footer()
					},
					context_instance=RequestContext(request))

def producer(request, producer):
	try:
		producer = models.Producer.objects.get(id = producer, active=True)
	except ObjectDoesNotExist:
		raise Http404
	product_list = models.Product.objects.filter(active=True, producer = producer, category__active = True)
	paginator = Paginator(product_list, 6)
	page = request.GET.get("page")
	try:
		products = paginator.page(page)
	except PageNotAnInteger:
		products = paginator.page(1)
	except EmptyPage:
		products = paginator.page(paginator.num_pages)
	return render_to_response(	"producer.html",
					{
						"breadcrumbs": [{"name": "Producers", "get_absolute_url": reverse(producers)}, producer],
						"producer": producer,
						"products": products,
						"cycle": models.Cycle.getCurrentCycle(),
						"footer": get_footer()
					},
					context_instance=RequestContext(request))

def categories(request):
	categories = models.Category.objects.filter(active = True)
	if categories == None:
		raise Http404
	return render_to_response(
					"categories.html",
					{
						"categories": categories,
						"cycle": models.Cycle.getCurrentCycle(),
						"footer": get_footer()
					},
					context_instance=RequestContext(request))
def producers(request):
	producers = models.Producer.objects.filter(active = True)
	if producers == None:
		raise Http404
	return render_to_response(
					"producers.html",
					{
						"producers": producers,
						"cycle": models.Cycle.getCurrentCycle(),
						"footer": get_footer()
					},
					context_instance=RequestContext(request))

def category(request, category):
	try:
		category = models.Category.objects.get(id = category, active=True)
	except ObjectDoesNotExist:
		raise Http404
	product_list = category.product_set.filter(active=True, producer__active = True).order_by("name")
	paginator = Paginator(product_list, 6)
	page = request.GET.get("page")
	try:
		products = paginator.page(page)
	except PageNotAnInteger:
		products = paginator.page(1)
	except EmptyPage:
		products = paginator.page(paginator.num_pages)

	return render_to_response(
					"category.html",
					{
						"breadcrumbs": [category],
						"products": products,
						"category": category,
						"cycle": models.Cycle.getCurrentCycle(),
						"footer": get_footer()
					},
					context_instance=RequestContext(request))

def search(request):
	query_string = ''
	products = None
	if ('q' in request.GET) and request.GET['q'].strip():
		query_string = request.GET['q']
        	entry_query = get_query(query_string, ['name', 'description'])
        	product_list = models.Product.objects.filter(entry_query)
        	paginator = Paginator(product_list,20)
		page = request.GET.get("page")
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			products = paginator.page(1)
		except EmptyPage:
			products = paginator.page(paginator.num_pages)
	return render_to_response(
					"search.html",
					{
						"breadcrumbs": [{"name": "search", "get_absolute_url": reverse(index)}],
						"products": products,
						"cycle": models.Cycle.getCurrentCycle(),
						"footer": get_footer(),
						"url": "%s?q=%s" % (request.path, urlquote(request.GET["q"])),
					},
					context_instance=RequestContext(request))

def signup(request):
	errors = []
	fields = {}
	if request.method == "POST":
		for i in ["firstName", "lastName", "email", "address1", "city", "state", "zip", "phone", "password", "verifyPassword"]:
			if request.POST[i] == "":
				errors.append("Must fill in the %s field" % i)
			else:
				fields[i] = request.POST[i]
		fields["address2"] = request.POST["address2"]
		if fields["password"] != fields["verifyPassword"]:
			errors.append("Passwords don't match")
		if not re.match("[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}", fields["email"], re.I):
			errors.append("%s is not a valid email address" % fields["email"])
		if errors == []:
			try:
				user = User.objects.create_user(fields["email"], fields["email"], fields["password"])
				user.first_name		= fields["firstName"]
				user.last_name		= fields["lastName"]
				user.profile		= models.UserProfile(user=user)
				user.profile.address1	= fields["address1"]
				user.profile.address2	= fields["address2"]
				user.profile.city	= fields["city"]
				user.profile.state	= fields["state"]
				user.profile.zip	= fields["zip"]
				user.profile.phone	= fields["phone"]
				user.profile.membershipBalance	= 0
				user.profile.save()
				user.save()
				login(request, authenticate(username=fields["email"], password=fields["password"]))
			except Exception, e:
				errors.append("Error saving new user to the database: %s" % e)
		if errors == []:
			return redirect(index)
	return render_to_response(
					"signup.html",
					{
						"errors": errors,
						"fields": fields,
						"cycle": models.Cycle.getCurrentCycle(),
						"footer": get_footer()
				 	},
					context_instance=RequestContext(request))

def cart(request):
	cart = {}
	try:
		cart = request.session["cart"]
	except KeyError:
		cart = request.session["cart"] = {"items": {}, "subtotal": 0, "tax": 0, "nonmemberFee": 0, "total": 0}

	if request.method == "POST":
		if request.POST["action"] == "setOrderItem":
			try:
				prod = models.Product.objects.get(id = int(request.POST["productId"]), active = True)
			except ObjectDoesNotExist:
				raise Http404
			if prod.unlimitedQuantity:
				quantity = decimal.Decimal(request.POST["quantity"])
			else:
				quantity = min(decimal.Decimal(request.POST["quantity"]), prod.get_remaining())
			price = prod.get_price()
			cart["items"][prod.id] = {}
			cart["items"][prod.id]["description"] = prod.name
			cart["items"][prod.id]["quantity"] = quantity
			cart["items"][prod.id]["price"] = (price * quantity).quantize(TWOPLACES)
			cart["items"][prod.id]["taxable"] = prod.taxable
			cart["items"][prod.id]["unit"] = prod.unit

			cart["subtotal"] = sum([item["price"] for (key, item) in cart["items"].iteritems()])
			if not request.user.is_authenticated() or (not request.user.get_profile().is_member() and models.Product.objects.filter(id__in = [id for id in cart["items"] if cart["items"][id]["quantity"] > 0], membershipPayment=True).count() == 0):
				cart["nonmemberFee"] = decimal.Decimal(models.Setting.objects.get(key="Nonmember Fee").value).quantize(TWOPLACES)
			else:
				cart["nonmemberFee"] = 0
			taxable = sum([item["price"] for (key, item) in cart["items"].iteritems() if item["taxable"] == True])
			cart["tax"] = (decimal.Decimal(models.Setting.objects.get(key = "tax").value) * taxable).quantize(TWOPLACES)
			cart["total"] = cart["subtotal"] + cart["tax"] + cart["nonmemberFee"]

			cartItem = {	"item":		{"prodId": int(prod.id),
							"description": cart["items"][prod.id]["description"],
							"price": float(cart["items"][prod.id]["price"]),
							"quantity": float(cart["items"][prod.id]["quantity"])},
					"subtotal":	float(cart["subtotal"]),
					"tax":		float(cart["tax"]),
					"nonmemberFee":	float(cart["nonmemberFee"]),
					"total":	float(cart["total"])}
			return HttpResponse(json.dumps(cartItem))
		else:
			raise HttpResponseBadRequest
	elif request.method == "GET":
		if request.user.is_authenticated():
			return render_to_response(
							"cart.html",
							{
								"cart": cart,
								"cycle": models.Cycle.getCurrentCycle(),
								"footer": get_footer()
							},
							context_instance=RequestContext(request))
		else:
			return render_to_response("registration/login.html", {"next": request.path}, context_instance=RequestContext(request))

def charge(request):
	if request.method == "GET":
		return render_to_response(	"charge.html",
						{
							"profile": request.user.get_profile(),
							"prevCard": request.user.get_profile().get_card(),
							"stripe_key": models.Setting.objects.get(key="Stripe Public Key").value,
							"cycle": models.Cycle.getCurrentCycle(),
							"footer": get_footer()
						},
						context_instance=RequestContext(request))
	elif request.method == "POST":
		try:
			cart = request.session["cart"]
		except KeyError:
			raise Http404 #TODO this shouldn't be a 404

		order = models.Order(customer=request.user, cycle=models.Cycle.getCurrentCycle())
		order.save()

		items = []
		for i in cart["items"]:
			product = models.Product.objects.get(id = i)
			if not product.unlimitedQuantity:
				remaining = product.get_remaining()
				if cart["items"][i]["quantity"] > remaining:
					#TODO return Error
					cart["items"][i]["quantity"] = remaining
			if cart["items"][i]["quantity"] > 0:
				orderItem = models.OrderItem(product=product, order=order, quantity=cart["items"][i]["quantity"], wholesalePrice = product.wholesalePrice, price=product.get_price())
				orderItem.save()
				items.append(orderItem)
		try:
			if "card" in request.POST:
				if request.POST["card"] == "newCard":
					request.user.get_profile().update_card(request.POST["stripeToken"])
			else:
				request.user.get_profile().create_charge_account(request.POST["stripeToken"])
			order.charge()
			del(request.session["cart"])
			return render_to_response(	"order.html",
							{
								"message": "<h1>Thank You</h1>Your order has been received.  You order will arrive on " + str(order.cycle.delivery),
								"cycle": models.Cycle.getCurrentCycle(),
								"order": order,
								"items": models.OrderItem.objects.filter(order=order.id),
								"footer": get_footer()
							},
							context_instance=RequestContext(request))
		except:
			order.delete()
			return render_to_response(	"charge.html",
							{
								"profile": request.user.get_profile(),
								"stripe_key": models.Setting.objects.get(key="Stripe Public Key").value,
								"cycle": models.Cycle.getCurrentCycle(),
								"footer": get_footer(),
								"error": "Error Charging Card"
							},
							context_instance=RequestContext(request))

class OrderReportForm(forms.Form):
	cycle = forms.ModelChoiceField(queryset=models.Cycle.objects.all().order_by("-date"), required=False)

def orderReport(request):
	if not request.user.groups.filter(name__in=["Producers", "Admins"]):
		raise Http404
	data = []
	if request.method == "POST":
		form = OrderReportForm(request.POST)
		if form.is_valid():
			filters = {}
			if form.cleaned_data["cycle"] == None:
				cycle = models.Cycle.getCurrentCycle()
			else:
				cycle = form.cleaned_data["cycle"]
			orders = models.Order.objects.filter(cycle=cycle)
	else:
		form = OrderReportForm()
		orders = models.Order.objects.filter(cycle=models.Cycle.getCurrentCycle())

	return render_to_response(	"orderreport.html",
					{
						"queryForm": form,
						"cycle": models.Cycle.getCurrentCycle(),
						"orders": orders
					},
					context_instance=RequestContext(request))
class ProducerReportForm(forms.Form):
	cycle = forms.ModelChoiceField(queryset=models.Cycle.objects.all().order_by("-date"), required=False)
	def __init__(self, groups, *args):
		super(forms.Form,self).__init__(*args)
		if "Admins" in groups:
			self.fields["producer"] = forms.ModelChoiceField(queryset=models.Producer.objects.all(), required=False)
		

def producerReport(request):
	groups = [g.name for g in request.user.groups.filter(name__in=["Producers", "Admins"])]
	if not groups:
		raise Http404
	if request.method == "POST":
		form = ProducerReportForm(groups, request.POST)
		if form.is_valid():
			sections = []
			filters = {}
			if "Admins" not in groups:
				form.cleaned_data["producer"] = request.user.get_profile().producer
			if form.cleaned_data["cycle"] == None:
				filters["cycle"] = models.Cycle.getCurrentCycle()
			else:
				filters["cycle"] = form.cleaned_data["cycle"]
			orders = models.Order.objects.filter(**filters)
			products = {}
			totals = {}
			totalcost = 0
			columnHeaders = ["Quantity", "Product"]
			for order in orders:
				if form.cleaned_data["producer"] in [product.producer for product in order.products.all()]:
					profile = order.customer.get_profile()
					sectionHeader = [order.customer.get_full_name(), profile.address1]
					if profile.address2:
						sectionHeader.append(profile.address2)
					sectionHeader.append("%s, %s, %s" % (profile.city, profile.state, profile.zip))
					entries = [[orderItem.quantity, orderItem.product.name] for orderItem in models.OrderItem.objects.filter(order = order, product__producer = form.cleaned_data["producer"])]
					sections.append({"sectionHeader": sectionHeader, "columnHeaders": columnHeaders, "entries": entries})
			items = models.OrderItem.objects.filter(order__cycle = form.cleaned_data["cycle"], product__producer = form.cleaned_data["producer"]).values("product").annotate(quantity=Sum("quantity"))
			sections.append({"sectionHeader": ["Totals"], "columnHeaders": columnHeaders, "entries": [[i["quantity"], models.Product.objects.get(id=i["product"]).name] for i in items]})
	else:
		form = ProducerReportForm(groups)
		sections = None

	return render_to_response(	"sectionreport.html",
					{
						"queryForm": form,
						"cycle": models.Cycle.getCurrentCycle(),
						"sections": sections
					},
					context_instance=RequestContext(request))
	
class SalesReportForm(forms.Form):
	cycle = forms.ModelChoiceField(queryset=models.Cycle.objects.all(), required=False)

def salesReport(request):
	if not request.user.groups.filter(name__in=["Admins"]):
		raise Http404
	if request.method == "POST":
		form = SalesReportForm(request.POST)
		if form.is_valid():
			if form.cleaned_data["cycle"] == None:
				cycle = models.Cycle.getCurrentCycle()
			else:
				cycle = form.cleaned_data["cycle"]
			
		section = {"columnHeaders": ["Id", "Name", "Gross", "Nonmember Fee", "Delivery Fee", "tax", "Expense", "Processing Fee", "Net"], "entries": []}
		totals = [0] * 7
		for order in models.Order.objects.filter(cycle = cycle):
			wholesale = sum([item.quantity * item.wholesalePrice for item in models.OrderItem.objects.filter(order = order)])
			entryAmounts = [order.total.quantize(TWOPLACES),
					order.nonmemberFee.quantize(TWOPLACES),
					order.deliveryFee.quantize(TWOPLACES),
					order.tax.quantize(TWOPLACES),
					wholesale.quantize(TWOPLACES),
					order.processingFee.quantize(TWOPLACES),
					(order.subtotal - wholesale - order.processingFee).quantize(TWOPLACES)]
			totals = [i[0] + i[1] for i in  zip(entryAmounts, totals)]
			section["entries"].append([order.id, order.customer.get_full_name()] + entryAmounts)
		section["entries"].append(["", "Totals"] + totals)
		section = [section]
	else:
		form = SalesReportForm()
		section = []

	return render_to_response(	"sectionreport.html",
					{
						"queryForm": form,
						"cycle": models.Cycle.getCurrentCycle(),
						"sections": section
					},
					context_instance=RequestContext(request))
def message(request):
	if not request.user.is_authenticated():
		return render_to_response("registration/login.html", {"next": request.path}, context_instance=RequestContext(request))

	if request.method == 'POST':
		models.Message(user = request.user, text = request.POST["message"]).save()
		return HttpResponseRedirect('messageThanks')

	return render_to_response('message.html', {
		"cycle": models.Cycle.getCurrentCycle(),
		"footer": get_footer()
	},
	context_instance=RequestContext(request))

def messageThanks(request):
	return render_to_response('messageThanks.html', {
		"cycle": models.Cycle.getCurrentCycle(),
		"footer": get_footer()
	},
	context_instance=RequestContext(request))

def order(request, order=None, message=None):
	try:
		order = models.Order.objects.get(id = order)
		items = models.OrderItem.objects.filter(order = order)
	except ObjectDoesNotExist:
		raise Http404

	return render_to_response(	"order.html",
					{
						"order": order,
						"items": items,
						"cycle": models.Cycle.getCurrentCycle(),
						"footer": get_footer()
					},
					context_instance=RequestContext(request))

def clearsession(request):
	try:
		del(request.session["cart"])
	except:
		pass
	return redirect(categories)

def logoutView(request):
	logout(request)
	return redirect(index)
	
def about(request, page):
	try:
		if page == "":
			page = models.AboutPage.objects.get(defaultPage = True)
		else:
			page = models.AboutPage.objects.get(slug = page)
		page.content += "\n\n" + "\n".join(["[%s]: %s" % (image.name, image.image.url) for image in models.AboutImage.objects.filter(page = page)])
	except ObjectDoesNotExist:
		raise Http404
	return render_to_response( "about.html", {
							"page": page,
							"pages": models.AboutPage.objects.all(),
							"cycle": models.Cycle.getCurrentCycle(),
							"footer":get_footer()},
							 context_instance=RequestContext(request))
	
urls = patterns('',
	url (r'^about/(.*)', about),
	url(r'^product/(.*)', product),
	url(r'^user/(.*)', user),
	url(r'^producer/(.*)', producer),
	url(r'^category/(.*)', category),
	url(r'^categories$', categories),
	url(r'^producers$', producers),
	url(r'^signup$', signup),
	url(r'^search$', search),
	url(r'^order/(.*)', order),
	url(r'^cart', cart, name="cart"),
	url(r'^charge', charge),
	url(r'^message$', message),
	url(r'^messageThanks$', messageThanks),
	url(r'^reports/producer', producerReport),
	url(r'^reports/order', orderReport),
	url(r'^reports/sales', salesReport),
	url(r'^clearsession', clearsession),
	url(r'^logout', logoutView),
	url(r'^$', index)
)
