# Generated migration for adding model_3d field to Product

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='model_3d',
            field=models.FileField(blank=True, help_text='Upload a GLB or GLTF 3D model file', null=True, upload_to='3d_models/'),
        ),
    ]
