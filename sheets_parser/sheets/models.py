from django.db import models


class Sheet(models.Model):
    num = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Порядковый номер',
    )
    reservation = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Номер заказа',
    )
    price_usd = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Цена в долларах',
    )
    price_rub = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Цена в рублях',
    )
    delivery_date = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Дата поставки',
    )

    class Meta:
        verbose_name = 'Таблица'
        verbose_name_plural = 'Таблицы'
