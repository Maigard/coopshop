# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cycle'
        db.create_table('coopshop_cycle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('delivery', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('coopshop', ['Cycle'])

        # Adding model 'Producer'
        db.create_table('coopshop_producer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('about', self.gf('django.db.models.fields.TextField')()),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2)),
            ('phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
            ('markup', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=3, blank=True)),
            ('leadTime', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('coopshop', ['Producer'])

        # Adding model 'Category'
        db.create_table('coopshop_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
        ))
        db.send_create_signal('coopshop', ['Category'])

        # Adding model 'ProductCycle'
        db.create_table('coopshop_productcycle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coopshop.Product'])),
            ('cycle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coopshop.Cycle'])),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('coopshop', ['ProductCycle'])

        # Adding model 'Unit'
        db.create_table('coopshop_unit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
        ))
        db.send_create_signal('coopshop', ['Unit'])

        # Adding model 'Product'
        db.create_table('coopshop_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('size', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=3, blank=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coopshop.Unit'])),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coopshop.Category'])),
            ('producer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coopshop.Producer'])),
            ('membershipPayment', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('membershipExtension', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('taxable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('wholesalePrice', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('markup', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=3, blank=True)),
            ('minimumPrice', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('leadTime', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('unlimitedQuantity', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('coopshop', ['Product'])

        # Adding model 'Order'
        db.create_table('coopshop_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('subtotal', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2, blank=True)),
            ('tax', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2, blank=True)),
            ('total', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2, blank=True)),
            ('cycle', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coopshop.Cycle'])),
            ('paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('delivered', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('paymentId', self.gf('django.db.models.fields.CharField')(default=False, max_length=32, null=True)),
            ('nonmemberFee', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2, blank=True)),
            ('deliveryFee', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2, blank=True)),
            ('processingFee', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('coopshop', ['Order'])

        # Adding model 'OrderItem'
        db.create_table('coopshop_orderitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coopshop.Product'])),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coopshop.Order'])),
            ('quantity', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
            ('wholesalePrice', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2, blank=True)),
        ))
        db.send_create_signal('coopshop', ['OrderItem'])

        # Adding model 'UserProfile'
        db.create_table('coopshop_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('phone', self.gf('django.contrib.localflavor.us.models.PhoneNumberField')(max_length=20)),
            ('address1', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('address2', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('state', self.gf('django.contrib.localflavor.us.models.USStateField')(max_length=2)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('membershipExpires', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('lifetimeMember', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('membershipBalance', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('producer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coopshop.Producer'], null=True, blank=True)),
            ('stripeId', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal('coopshop', ['UserProfile'])

        # Adding model 'Message'
        db.create_table('coopshop_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('coopshop', ['Message'])

        # Adding model 'Setting'
        db.create_table('coopshop_setting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('coopshop', ['Setting'])

        # Adding model 'AboutPage'
        db.create_table('coopshop_aboutpage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('defaultPage', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('coopshop', ['AboutPage'])

        # Adding model 'AboutImage'
        db.create_table('coopshop_aboutimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['coopshop.AboutPage'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
        ))
        db.send_create_signal('coopshop', ['AboutImage'])


    def backwards(self, orm):
        # Deleting model 'Cycle'
        db.delete_table('coopshop_cycle')

        # Deleting model 'Producer'
        db.delete_table('coopshop_producer')

        # Deleting model 'Category'
        db.delete_table('coopshop_category')

        # Deleting model 'ProductCycle'
        db.delete_table('coopshop_productcycle')

        # Deleting model 'Unit'
        db.delete_table('coopshop_unit')

        # Deleting model 'Product'
        db.delete_table('coopshop_product')

        # Deleting model 'Order'
        db.delete_table('coopshop_order')

        # Deleting model 'OrderItem'
        db.delete_table('coopshop_orderitem')

        # Deleting model 'UserProfile'
        db.delete_table('coopshop_userprofile')

        # Deleting model 'Message'
        db.delete_table('coopshop_message')

        # Deleting model 'Setting'
        db.delete_table('coopshop_setting')

        # Deleting model 'AboutPage'
        db.delete_table('coopshop_aboutpage')

        # Deleting model 'AboutImage'
        db.delete_table('coopshop_aboutimage')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'coopshop.aboutimage': {
            'Meta': {'object_name': 'AboutImage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coopshop.AboutPage']"})
        },
        'coopshop.aboutpage': {
            'Meta': {'object_name': 'AboutPage'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'defaultPage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'coopshop.category': {
            'Meta': {'ordering': "['name']", 'object_name': 'Category'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'coopshop.cycle': {
            'Meta': {'ordering': "['date']", 'object_name': 'Cycle'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'delivery': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'coopshop.message': {
            'Meta': {'ordering': "['date']", 'object_name': 'Message'},
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'coopshop.order': {
            'Meta': {'object_name': 'Order'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'cycle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coopshop.Cycle']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delivered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deliveryFee': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nonmemberFee': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'paymentId': ('django.db.models.fields.CharField', [], {'default': 'False', 'max_length': '32', 'null': 'True'}),
            'processingFee': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['coopshop.Product']", 'through': "orm['coopshop.OrderItem']", 'symmetrical': 'False'}),
            'subtotal': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        'coopshop.orderitem': {
            'Meta': {'object_name': 'OrderItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coopshop.Order']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coopshop.Product']"}),
            'quantity': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'wholesalePrice': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        'coopshop.producer': {
            'Meta': {'object_name': 'Producer'},
            'about': ('django.db.models.fields.TextField', [], {}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'leadTime': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'markup': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '3', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'coopshop.product': {
            'Meta': {'ordering': "['name']", 'object_name': 'Product'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coopshop.Category']"}),
            'cycles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['coopshop.Cycle']", 'through': "orm['coopshop.ProductCycle']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'leadTime': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'markup': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '3', 'blank': 'True'}),
            'membershipExtension': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'membershipPayment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minimumPrice': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'producer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coopshop.Producer']"}),
            'size': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '3', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coopshop.Unit']"}),
            'unlimitedQuantity': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wholesalePrice': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        'coopshop.productcycle': {
            'Meta': {'object_name': 'ProductCycle'},
            'cycle': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coopshop.Cycle']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coopshop.Product']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {})
        },
        'coopshop.setting': {
            'Meta': {'object_name': 'Setting'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'coopshop.unit': {
            'Meta': {'object_name': 'Unit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'coopshop.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lifetimeMember': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'membershipBalance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'membershipExpires': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {'max_length': '20'}),
            'producer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coopshop.Producer']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'stripeId': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['coopshop']