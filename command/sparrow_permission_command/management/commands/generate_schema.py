import json
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
        parser.add_argument(
            '-d', '--django', dest='dj_ver',
            default="2", choices=["1", "2"],
            help='指定django的版本，可选值为1或2。如果django版本>=1.11,请选择2'
        )

    def get_api_name(self, _paths, path, _method):
        # 获得权限的名字，从description中取前60个字符
        _api = _paths[path][_method]
        _name = _api["description"]
        if len(_name) == 0:
            _name = _api["operationId"]
        else:
            _name = _name[0:60]
        return _name

    def register(self, schema, auth_centre, upd):
        try:
            #print(schema)
            if auth_centre:
                r = requests.post(auth_centre, data={
                    "schema": json.dumps(schema),
                    "upd": upd
                })
                if r.status_code == 200:
                    print("注册API成功")
                else:
                    print("注册API失败")
            else:
                print("未指定AUTH_CENTRE")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("issue")


    def get_schema_generator(self, generator_class_name, api_name, api_version):
        generator_class = import_string(generator_class_name)
        return generator_class(
            name=api_name,
            version=api_version
        )

    def get_schema(self, generator, request, public):
        return generator.get_schema(request=request, public=public)

    def handle(self, auth_centre, dj_ver, *args, **kwargs):
        # disable logs of WARNING and below
        logging.disable(logging.WARNING)

        if dj_ver == "2":
            generator = self.get_schema_generator("sparrow_permission_command.generators.OpenAPISchemaGenerator", "API",
                                                  "1.0")
        else:
            generator = self.get_schema_generator("sparrow_permission_command.generatorsForOne.SchemaGenerator", "API",
                                                  "1.0")
        schema = self.get_schema(generator, None, True)
        if not auth_centre:
            auth_centre=settings.AUTH_CENTRE
        self.register(schema, auth_centre, upd=True)
