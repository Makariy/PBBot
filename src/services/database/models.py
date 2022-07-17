from tortoise import models, fields


class OFModel(models.Model):
    name = fields.CharField(max_length=64, null=False, default="", description="Model's name")


class Image(models.Model):
    file = fields.TextField(null=False)


class Card(models.Model):
    model = fields.ForeignKeyField('models.OFModel')
    images = fields.ManyToManyField('models.Image')
    real_link = fields.TextField(null=False)
    preview_image = fields.TextField(null=False)
    views_count = fields.IntField(null=False)
    photos_count = fields.IntField(null=False)
