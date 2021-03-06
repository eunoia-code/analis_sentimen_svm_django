# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DataLat(models.Model):
    review = models.TextField()
    kelas = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'data_lat'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class KataBaku(models.Model):
    no = models.AutoField(primary_key=True)
    tidakbaku = models.CharField(max_length=30)
    baku = models.CharField(max_length=30)

    def __str__(self):
        return self.tidakbaku+" -> "+self.baku

    class Meta:
        managed = False
        db_table = 'kata_baku'


class TbKatadasar(models.Model):
    id_ktdasar = models.AutoField(primary_key=True)
    katadasar = models.CharField(max_length=20)
    tipe_katadasar = models.CharField(max_length=20)

    def __str__(self):
        return self.katadasar

    class Meta:
        managed = False
        db_table = 'tb_katadasar'


class TbNormalisasi(models.Model):
    kata_dasar = models.CharField(max_length=50)

    def __str__(self):
        return self.kata_dasar

    class Meta:
        managed = False
        db_table = 'tb_normalisasi'


class TbPreprocessing(models.Model):
    review = models.TextField()
    kelas = models.CharField(max_length=20)
    indexing = models.TextField()

    class Meta:
        managed = False
        db_table = 'tb_preprocessing'


class TbData(models.Model):
    review = models.TextField()
    normalisation = models.TextField()
    choices = (
        ('1', 'Positif'),
        ('0', 'Negatif')
    )
    label = models.CharField(max_length=1, choices=choices)
    index_number = models.CharField(max_length=3)

    class Meta:
        managed = False
        db_table = 'tb_data'


class TbSentimen(models.Model):
    kata = models.CharField(max_length=30)
    sentimen = models.CharField(max_length=30)

    def __str__(self):
        return self.kata

    class Meta:
        managed = False
        db_table = 'tb_sentimen'

class TbProduct(models.Model):
    nama_product = models.CharField(max_length=100)
    url = models.TextField()
    kategori = models.CharField(max_length=50)

    def __str__(self):
        return self.nama_product

    class Meta:
        managed = False
        ordering = ('nama_product',)
        db_table = 'tb_product'
