from django import template
import importlib
from django.conf import settings
import json
from sekizai.context import SekizaiContext
register = template.Library()

@register.inclusion_tag('csvimport/csvform.html', takes_context=True)
def csvform(context, label):
    mod_name, form_name = settings.CSV_FORMS[label].rsplit('.', 1)
    mod = importlib.import_module(mod_name)
    form = getattr(mod, form_name)
    required_fields = []
    
    for name, obj in form().fields.items():
        if obj.required and not obj.widget.is_hidden: required_fields.append(name)
    context.update({
        'required_fields': json.dumps(required_fields),
        'headers': [(name, f) for name, f in form().fields.items() if not f.widget.is_hidden],
        'label': label,
    })
    return context