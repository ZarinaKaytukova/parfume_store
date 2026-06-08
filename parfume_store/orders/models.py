from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('male', 'Мужской парфюм'),
        ('female', 'Женский парфюм'),
    ]
    VOLUME_CHOICES = [
        ('small', '50 мл.'),
        ('large', '100 мл.')
    ]
    
    article = models.CharField(max_length=100, unique=True, verbose_name='Артикул')
    name = models.CharField(max_length=100, verbose_name='Наименование')
    unit = models.CharField(max_length=100, default='Флакон', verbose_name='Единица измерения')
    volume = models.CharField(max_length=50, choices=VOLUME_CHOICES, verbose_name="Объем (мл.)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена') 
    supplier = models.CharField(max_length=100, verbose_name='Поставщик')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, verbose_name='Категория продукта')
    discount = models.IntegerField(default=0, verbose_name='Действующая скидка (%)')
    stock = models.IntegerField(verbose_name='Количество на складе')
    description = models.TextField(blank=True, verbose_name='Описание продукта')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Изображение продукта')

    def get_final_price(self):
        if self.discount:
            return round(self.price / 100 * (100 - self.discount), 2)
        return self.price
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Валидация в модели"""
        from django.core.exceptions import ValidationError
        if self.price and self.price < 0:
            raise ValidationError({'price': 'Цена не может быть отрицательной.'})
        if self.stock is not None and self.stock < 0:
            raise ValidationError({'stock': 'Количество на складе не может быть отрицательным.'})
        if self.discount and not(0 < self.discount < 100):
            raise ValidationError({'discount': 'Скидка должна быть от 1 до 99% включительно.'})
    
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'


class PickupPoint(models.Model):
    address = models.CharField(max_length=200, verbose_name='Адрес пункта выдачи')
    
    def __str__(self):
        return self.address
    
    class Meta:
        verbose_name = 'Пункт выдачи'
        verbose_name_plural = 'Пункты выдачи'


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('completed', 'Завершён'),
    ]
    
    order_number = models.CharField(max_length=100, unique=True, verbose_name='Номер заказа')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Клиент')
    order_date = models.DateField(verbose_name='Дата заказа')
    delivery_date = models.DateField(verbose_name='Дата доставки')
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.CASCADE, verbose_name='Пункт выдачи')
    pickup_code = models.IntegerField(verbose_name='Код для получения')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='new', verbose_name='Статус заказа')
    
    def __str__(self):
        return f"Заказ {self.order_number} - {self.user.get_full_name()}"
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


# Модель для позиций заказа (для нормализации артикулов и количеств)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт')
    quantity = models.IntegerField(verbose_name='Количество')
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'
        unique_together = ('order', 'product')