from django.contrib import admin

from provetrina.profiles import models

admin.site.register([models.User, models.Profile])
