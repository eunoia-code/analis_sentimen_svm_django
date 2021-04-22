from django.contrib import admin
from .models import DataLat, KataBaku, TbKatadasar, TbNormalisasi, TbPreprocessing, TbSentimen, TbProduct
from import_export.admin import ImportExportActionModelAdmin

# Register your models here.

class DataLatClass(admin.ModelAdmin):
    pass
admin.site.register(DataLat, DataLatClass)

class KataBakuClass(admin.ModelAdmin):
    pass
admin.site.register(KataBaku, KataBakuClass)

class TbKatadasarClass(admin.ModelAdmin):
    pass
admin.site.register(TbKatadasar, TbKatadasarClass)

class TbNormalisasiClass(admin.ModelAdmin):
    pass
admin.site.register(TbNormalisasi, TbNormalisasiClass)

class TbPreprocessingClass(admin.ModelAdmin):
    pass
admin.site.register(TbPreprocessing, TbPreprocessingClass)

class TbSentimenClass(admin.ModelAdmin):
    pass
admin.site.register(TbSentimen, TbSentimenClass)

class TbProductClass(ImportExportActionModelAdmin):
    search_fields = ('nama_product', )
    pass
admin.site.register(TbProduct, TbProductClass)
