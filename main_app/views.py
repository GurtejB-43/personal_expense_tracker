from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm

# Create your views here.

def home(request):

    # Using prepared statement (raw SQL) for querying expenses records
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.id, e.amount, e.date, e.description, c.name 
            FROM main_app_expense e 
            JOIN main_app_category c ON e.category_id = c.id 
            ORDER BY e.date DESC
        """)
        expense_records = cursor.fetchall()
        expenses = [
            {
                'id': record[0],
                'amount': record[1],
                'date': record[2],
                'description': record[3],
                'category': record[4]
            } for record in expense_records
        ]
    
    # using ORM for categories as it's simpler
    categories = Category.objects.all()
    #can query expenses much more easily using this line:
    #expenses = Expense.objects.all().order_by('-date')
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            #create new expense record when the form is valid
            form.save()
            
            messages.success(request, 'Expense added successfully!')
            return redirect('main_app:home')
    else:
        form = ExpenseForm()
    
    return render(request, 'main_app/home.html', {
        'expenses': expenses,
        'form': form,
        'categories': categories
    })

def delete_expense(request, pk):
    #retrieve a single record 
    expense = get_object_or_404(Expense, pk=pk)

    #delete a single record
    expense.delete()
    messages.success(request, 'Expense deleted successfully!')
    return redirect('main_app:home')

def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('main_app:home')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'main_app/edit_expense.html', {'form': form})

