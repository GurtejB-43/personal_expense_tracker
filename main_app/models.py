from django.db import models
from django.utils import timezone

## django automatically creates an id (primary key) for each model

## table 1: Category (name)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

## table 2: Expense (amount, category, date, description)
class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    ## foreign key to Category table is a 1 to many relationship
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.amount} for {self.category} on {self.date}"
