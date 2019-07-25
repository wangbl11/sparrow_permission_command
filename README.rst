==========================
sparrow_permission_command
==========================

sparrow_permission_command提供了一个命令(command),用来把注册API到权限中心。

Quick start
-----------

1. Add "sparrow_permission_command" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'sparrow_permission_command',
    ]

2. Add next parameters in settings.py::

    SPARROW_PERMISSION_CENTRE = "https://backend5.dongyouliang.com"

3. Run `python manage.py inspect_schema` to register APIs into permission center
   or Write this command in dockfile to run automatically before rebuild every time in K8s