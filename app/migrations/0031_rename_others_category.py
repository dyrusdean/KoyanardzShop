# Generated migration to rename 'Others' category to '2nd Hand'

from django.db import migrations


def rename_others_to_2nd_hand(apps, schema_editor):
    Category = apps.get_model('app', 'Category')
    try:
        category = Category.objects.get(category_name='Others')
        category.category_name = '2nd Hand'
        category.save()
    except Category.DoesNotExist:
        pass


def reverse_rename(apps, schema_editor):
    Category = apps.get_model('app', 'Category')
    try:
        category = Category.objects.get(category_name='2nd Hand')
        category.category_name = 'Others'
        category.save()
    except Category.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_product_created_at_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.RunPython(rename_others_to_2nd_hand, reverse_rename),
    ]
