from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_alter_category_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='popularity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
