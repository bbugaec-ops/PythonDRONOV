from django.db import models
from django.utils.safestring import mark_safe


class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name='Назва')

    def __str__(self):
        return self.name


class Bd(models.Model):
    title = models.CharField(max_length=50, verbose_name='Товар')
    content = models.TextField(null=True, blank=True, verbose_name='Опис')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Ціна')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Стара ціна')
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубліковано')
    rubric = models.ForeignKey(Rubric, null=True, on_delete=models.PROTECT, verbose_name='Рубрика')
    image = models.ImageField(upload_to='photos/%Y/%m/%d/', verbose_name='Фото', null=True, blank=True)
    is_available = models.BooleanField(default=True, verbose_name="В наявності")
    stock = models.PositiveIntegerField(default=1, verbose_name="Кількість на складі")

    # --- ДОДАНО: АВТОМАТИКА СКЛАДУ ---
    def save(self, *args, **kwargs):
        # Якщо кількість 0, автоматично знімаємо галочку "В наявності"
        if self.stock == 0:
            self.is_available = False
        else:
            self.is_available = True
        super().save(*args, **kwargs)

    # --- ДОДАНО: КОЛЬОРОВИЙ СТАТУС ДЛЯ АДМІНКИ ---
    def stock_status(self):
        if self.stock == 0:
            return mark_safe('<b style="color: red;">❌ Немає</b>')
        elif self.stock <= 5:
            return mark_safe(f'<b style="color: orange;">⚠️ Мало ({self.stock})</b>')
        return mark_safe(f'<b style="color: green;">✅ Достатньо ({self.stock})</b>')

    stock_status.short_description = 'Залишок'

    def img_preview(self):
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" width="60" style="border-radius: 5px; shadow: 2px 2px 5px rgba(0,0,0,0.2);">')
        return "Немає фото"

    img_preview.short_description = 'Прев’ю'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Оголошення'
        verbose_name = 'Оголошення'
        ordering = ['-published']


class Order(models.Model):
    DELIVERY_CHOICES = [('NP', 'Нова Пошта'), ('UP', 'Укрпошта')]
    TYPE_CHOICES = [('branch', 'відділення'), ('poshtomat', 'поштомат'), ('courier', "кур'єром")]
    STATUS_CHOICES = [
        ('new', '🆕 Нове замовлення'),
        ('request', '📦 Запит постачальнику'),
        ('wait', '⏳ Очікує оплати'),
        ('sent', '🚚 Відправлено'),
        ('done', '✅ Завершено'),
        ('cancel', '❌ Скасовано'),
    ]

    last_name = models.CharField(max_length=50, verbose_name='Прізвище')
    first_name = models.CharField(max_length=50, verbose_name="Ім'я")
    middle_name = models.CharField(max_length=50, verbose_name="По батькові")
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    region = models.CharField(max_length=100, verbose_name='Область')
    city = models.CharField(max_length=100, verbose_name='Місто')
    street = models.CharField(max_length=100, verbose_name='Вулиця', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")
    delivery_service = models.CharField(max_length=2, choices=DELIVERY_CHOICES, default='NP',
                                        verbose_name='Служба доставки')
    delivery_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='branch',
                                     verbose_name='Спосіб доставки')
    department = models.CharField(max_length=100, verbose_name='Номер відділення')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус замовлення')
    items = models.TextField(verbose_name='Товари', blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сума', default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')

    def __str__(self):
        return f"Замовлення №{self.pk} - {self.last_name}"

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created_at']