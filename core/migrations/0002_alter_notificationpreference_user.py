from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationpreference',
            name='user',
            field=models.OneToOneField(
                on_delete=models.CASCADE,
                related_name='notification_preferences',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
