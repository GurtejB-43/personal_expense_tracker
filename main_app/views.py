from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection, models # Import models
from django.db.models import Sum, Avg, Count # Import aggregation functions
from .models import Expense, Category
from .forms import ExpenseForm, CategoryForm, ReportFilterForm

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

#return a report of expenses filtered by the user's criteria
def filtered_report(request):
    expenses = Expense.objects.select_related('category').none() # Start with an empty queryset
    stats = {}
    form = ReportFilterForm(request.GET or None) # Populate with GET data if available

    if form.is_valid():
        # Start with all expenses, efficiently fetching related category
        queryset = Expense.objects.select_related('category').all()

        category = form.cleaned_data.get('category')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        # Apply filters conditionally using the ORM
        if category:
            queryset = queryset.filter(category=category)
        if start_date:
            queryset = queryset.filter(date__gte=start_date) # gte = greater than or equal
        if end_date:
            queryset = queryset.filter(date__lte=end_date)   # lte = less than or equal

        # Order the results
        expenses = queryset.order_by('-date')

        # Calculate statistics on the filtered queryset
        stats = expenses.aggregate(
            total_amount=Sum('amount', default=0),
            average_amount=Avg('amount', default=0),
            count=Count('id')
        )
        # Ensure values are 0 if no expenses match
        stats['total_amount'] = stats['total_amount'] or 0
        stats['average_amount'] = stats['average_amount'] or 0


    # If the form is invalid or not submitted, 'expenses' will be empty
    # and 'stats' will be empty.

    return render(request, 'main_app/report.html', {
        'form': form,
        'expenses': expenses,
        'stats': stats
    })

