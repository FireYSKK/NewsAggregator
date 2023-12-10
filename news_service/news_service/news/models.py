from django.db import models


# Create your models here.
#Модель новостного заголовка
class Headline(models.Model):
    # Заголовок статьи
    title = models.CharField(max_length=200)
    # Краткое содержание статьи
    description = models.TextField()
    # Дата и время публикации
    pub_date = models.DateTimeField(null=True)
    # Ссылка на оригинальную запись новости
    url = models.TextField()
    # Первоисточник
    source = models.CharField(max_length=20)
    # Категория ("Политика", "Экономика" и т.д.)
    category = models.CharField(max_length=50, null=True)


class Transaction(models.Model):
    department = models.CharField(max_length=100)
    amount = models.FloatField()
    created_by = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.department} {self.amount}"
