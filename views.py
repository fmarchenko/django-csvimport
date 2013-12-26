from django.http.response import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import importlib
import uuid
import os
import json
import unicodecsv

@csrf_exempt
def csvimport(request, label):
    if not request.POST: 
        raise Http404
    mod_name, form_name = settings.CSV_FORMS[label].rsplit('.',1)
    mod = importlib.import_module(mod_name)
    form = getattr(mod, form_name)()
    headers = map( lambda x: x.upper(), form.fields.keys())
    path_dir = os.path.join( settings.MEDIA_ROOT, 'csvimport')
    if not os.path.exists(path_dir):
        os.mkdir(path_dir)
    file_id = str(uuid.uuid4())
    file_name = os.path.join( path_dir, file_id)
    stream = open(file_name, 'w')
    for chunk in request.FILES['file'].chunks():
        stream.write(chunk)
    stream.close()
    answ = { 'headers': [], 'rows': [], 'file': file_id }
    with open(file_name, 'r') as stream:
        csv = unicodecsv.reader(stream, encoding='utf-8', delimiter=getattr(settings, 'CSV_DELIMITER', ';'))
        for n, row in enumerate( csv ):
            if n > 4: break
            if n == 0: 
                for col, item in enumerate( row ):
                    if  item.upper() in headers:
                        answ['headers'].append( (col, item.lower()) )
            else: answ['rows'].append(row)
    return HttpResponse( json.dumps( answ ) )


@csrf_exempt
def csvdump(request, label):
    if not request.POST.has_key('file') or not request.POST.has_key('data') : 
        return HttpResponse( json.dumps({'critical': "Not file id" }) )
    file_id = request.POST['file']
    data = request.POST['data'].split(',')
    path_dir = os.path.join( settings.MEDIA_ROOT, 'csvimport')
    file_name = os.path.join( path_dir, file_id)
    if not os.path.exists(file_name): return HttpResponse( json.dumps({'critical': "Not file" }) )
    
    mod_name, form_name = settings.CSV_FORMS[label].rsplit('.',1)
    mod = importlib.import_module(mod_name)
    form = getattr(mod, form_name)
    mapping = {}
    for key in form().fields.keys():
        try: mapping[data.index(key)] = key 
        except ValueError: pass
    
    components = []
    with open(file_name, 'r') as stream:
        csv = unicodecsv.reader(stream, encoding='utf-8', delimiter=getattr(settings, 'CSV_DELIMITER', ';'))
        for n, row in enumerate( csv ):
            if n == 0:continue
            obj = {}
            for ind, i in enumerate(row):
                try:  obj[ mapping[ind] ] = i
                except KeyError: pass
            form_obj = form(obj)
            print form_obj.is_valid() 
            components.append(obj)
                    
                    
    #mod_name, func_name = settings.CSV_DELEGATE.rsplit('.',1)
    #mod = importlib.import_module(mod_name)
    #func = getattr(mod, func_name)
    #func( components )
    return HttpResponse( '' )
    