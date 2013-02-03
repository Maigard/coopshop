from django import template

register=template.Library()

@register.filter
def in_group(user, group):
	"""Returns True/False if the user is in the given group(s).
	Usage::
		{% if user|in_group:"Friends" %}
		or
		{% if user|in_group:"Friends,Enemies" %}
		...
		{% endif %}
	You can specify a single group or comma-delimited list.
	No white space allowed.
	"""
	import re
	group_list = group.split(',')
	user_groups = [str(i.name) for i in user.groups.all()]
	for i in group_list:
		if i in user_groups:
			return True
	return False
