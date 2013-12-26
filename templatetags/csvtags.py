from django import template
import importlib
from django.conf import settings
import json;
register = template.Library()

@register.inclusion_tag('csvimport/csvform.html', takes_context=True)
def csvform(context, label):
    mod_name, form_name = settings.CSV_FORMS[label].rsplit('.',1)
    mod = importlib.import_module(mod_name)
    form = getattr(mod, form_name)
    required_fields = []
    for name, obj in form().fields.items():
        if obj.required: required_fields.append(name)
    return {
        'required_fields': json.dumps(required_fields),
        'headers': form().fields.items(),
        'col_nums': range( len(settings.CSV_HEADERS.keys()) ),
        'label': label,
    }