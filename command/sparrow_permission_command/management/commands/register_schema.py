import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.utils.module_loading import import_string
from rest_framework.settings import api_settings
import requests


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
            self.register(schema,auth_centre,upd=True)

        else:  # pragma: no cover
            raise ValueError("unknown format %s" % format)

    def get_schema_generator(self, generator_class_name, api_name, api_version):
        generator_class = "command.sparrow_permission_command.generators.OpenAPISchemaGenerator"
        #if generator_class_name:
        generator_class = import_string(generator_class)

        return generator_class(
            name=api_name,
            version=api_version
        )

    def get_schema(self, generator, request, public):
        return generator.get_schema(request=request, public=public)

    def handle(self, auth_centre, *args, **kwargs):
        # disable logs of WARNING and below
        logging.disable(logging.WARNING)



        format = 'json'
        request = None
        generator_class_name = None
        generator = self.get_schema_generator(generator_class_name, "API","1.0")
        schema = self.get_schema(generator, request, True)

        self.write_schema(schema, auth_centre, self.stdout,format)
