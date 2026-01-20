# Generated migration to add user field to Favorite model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0052_alter_otptoken_otp_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='favorite',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together={('user', 'favorite_product')},
        ),
    ]
