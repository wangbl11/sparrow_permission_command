import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string
from rest_framework.settings import api_settings
import requests

from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings
from drf_yasg.codecs import OpenAPICodecJson, OpenAPICodecYaml

class Command(BaseCommand):
    help = '实时注册APIs到认证中心'

    def add_arguments(self, parser):
        parser.add_argument(
            'auth_centre', metavar='auth-centre',
            nargs='?',
            default='',
            type=str,
            help='认证中心提供的注册接口地址'
        )

    def get_api_name(self,_paths,path,_method):
        # 获得权限的名字，从description中取前60个字符
        _api = _paths[path][_method]
        _name = _api["description"]
        if len(_name) == 0:
            _name = _api["operationId"]
        else:
            _name = _name[0:60]
        return _name

    # def refresh_db(self, schema, upd):
    #     _ret = []
    #     _basepath = schema['basePath']
    #     # print(_basepath)
    #     _path = schema['paths']
    #     _keys = _path.keys()
    #
    #
    #     _existing_paths=set(Permission.objects.filter(path__contains=_basepath).values_list("path",flat=True).distinct())
    #     _schema_paths=[]
    #     for one in _keys:
    #         _schema_paths.append(_basepath+one)
    #     _schema_paths=set(_schema_paths)
    #
    #     # 删除数据库中已经不在当前schema中的所有path
    #     _to_delete=_existing_paths-_schema_paths
    #     print(len(_to_delete))
    #     if _to_delete:
    #         Permission.objects.filter(path__in=_to_delete).delete()
    #
    #     basepath_len=len(_basepath)
    #     # 处理新的path
    #     _to_add=_schema_paths-_existing_paths
    #     print(len(_to_add))
    #     for _key in _to_add:
    #         _perm=_key[basepath_len:]
    #         _methods = _path[_perm].keys()
    #         for one in _methods:
    #             if one != "parameters":
    #                 # 获得权限的名字，从description中取前60个字符
    #                 _api = _path[_key[basepath_len:]][one]
    #                 _name = self.get_api_name(_path,_perm,one)
    #                 _permission = Permission()
    #                 _permission.name = _name
    #                 _permission.path = _key
    #                 _permission.methods = one.upper()
    #                 _permission.save()
    #                 print('插入新的%s %s'% (_name, _key))
    #                 _ret.append({
    #                     "path": _key,
    #                     "method": _permission.methods,
    #                     "name":_name
    #                 })
    #
    #     # 修改已有的path，里面可能有new，delete或update的methods
    #     _to_update=_existing_paths & _schema_paths
    #     print(len(_to_update))
    #     for _full_path in _to_update:
    #         _perm = _full_path[basepath_len:]
    #         _methods = _path[_perm].keys()
    #         _args = []
    #         for one in _methods:
    #             if one != "parameters":
    #                 _args.append(one.upper())
    #         _args = set(_args)
    #         _existing = set(Permission.objects.filter(path__exact=_full_path).values_list("methods", flat=True))
    #
    #         # 要删除的
    #         _deleted = _existing - _args
    #         if _deleted:
    #             Permission.objects.filter(path__exact=_perm, methods__in=_deleted).delete()
    #
    #         # 新的
    #         _new = _args - _existing
    #         if _new:
    #             for _method in _args:
    #                 _name = self.get_api_name(_path, _perm, _method.lower())
    #                 _permission = Permission()
    #                 _permission.name = _name
    #                 _permission.path = _full_path
    #                 _permission.methods = _method
    #                 _permission.save()
    #                 #print('插入新的%s %s', (_key, _method))
    #                 _ret.append({
    #                     "path": _full_path,
    #                     "method": _method,
    #                     "name":_name
    #                 })
    #         if upd:
    #             # 旧的
    #             _old = _existing & _args
    #             if _old:
    #                 for _method in _old:
    #                     _permission = Permission.objects.get(path__exact=_full_path, methods__exact=_method)
    #                     if _permission:
    #                         _name = self.get_api_name(_path, _perm, _method.lower())
    #                         if _permission.name != _name:
    #                             _permission.name = _name
    #                             _permission.save()

    def register(self,schema,auth_centre,upd):
        try:

            if auth_centre:
                r = requests.post(auth_centre,data={
                    "schema":schema,
                    "upd":upd
                })
                if r.status_code==200:
                   print("注册API成功")
                else:
                   print("注册API失败")
            else:
                print("未指定AUTH_CENTRE")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("issue")
    def write_schema(self, schema, auth_centre, stream,format):
        if format == 'json':
            codec = OpenAPICodecJson(validators=[], pretty=True)
            swagger_json = codec.encode(schema).decode('utf-8')
            self.register(swagger_json,auth_centre,upd=True)
            stream.write(swagger_json)
        else:  # pragma: no cover
            raise ValueError("unknown format %s" % format)

    def get_schema_generator(self, generator_class_name, api_info, api_version, api_url):
        generator_class = swagger_settings.DEFAULT_GENERATOR_CLASS
        if generator_class_name:
            generator_class = import_string(generator_class_name)

        return generator_class(
            info=api_info,
            version=api_version,
            url=api_url,
        )

    def get_schema(self, generator, request, public):
        return generator.get_schema(request=request, public=public)

    def handle(self, auth_centre, *args, **kwargs):
        # disable logs of WARNING and below
        logging.disable(logging.WARNING)

        info = getattr(swagger_settings, 'DEFAULT_INFO', None)
        print(info)
        api_info = openapi.Info(
            title=info['title'],
            default_version=info['default_version']
        )
        if not auth_centre:
            auth_centre = settings.AUTH_CENTRE
            print(auth_centre)

        if not auth_centre:
            raise Exception("未指定认证中心地址，也没有默认指定")

        if not isinstance(api_info, openapi.Info):
            raise ImproperlyConfigured(
                'settings.SWAGGER_SETTINGS["DEFAULT_INFO"] should be an '
                'import string pointing to an openapi.Info object'
            )

        format = 'json'
        request = None
        generator_class_name = None
        private = False
        api_url = swagger_settings.DEFAULT_API_URL
        print(api_url)
        api_version = api_settings.DEFAULT_VERSION
        print(api_version)
        generator = self.get_schema_generator(generator_class_name, api_info, api_version, api_url)
        schema = self.get_schema(generator, request, not private)

        self.write_schema(schema, auth_centre, self.stdout,format)
