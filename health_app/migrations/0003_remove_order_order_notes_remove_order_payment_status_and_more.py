# Generated by Django 4.2.17 on 2025-01-10 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('health_app', '0002_alter_article_options_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_notes',
        ),
        migrations.RemoveField(
            model_name='order',
            name='payment_status',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_status',
        ),
        migrations.RemoveField(
            model_name='order',
            name='total_amount',
        ),
    ]
