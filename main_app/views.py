from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection, models # Import models
from django.db.models import Sum, Avg, Count # Import aggregation functions
from django.http import Http404
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
            #create new expense record when the form is valid (ORM - insert new expense record)
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
    #we can retrieve a single record using the primary key (pk) ORM
    #expense = get_object_or_404(Expense, pk=pk)

    # Fetch and delete a single record using a prepared statement (raw SQL)
    with connection.cursor() as cursor:
        # Execute DELETE and check if any row was affected
        cursor.execute("DELETE FROM main_app_expense WHERE id = %s", [pk])
        # rowcount tells us if a row was actually deleted
        if cursor.rowcount == 0:
            # If no rows were deleted, the pk didn't exist, raise 404
            raise Http404("Expense matching query does not exist.")

    messages.success(request, 'Expense deleted successfully!')
    return redirect('main_app:home')

def edit_expense(request, pk):
    #update an existing expense record using the primary key (pk) ORM
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            ## Update the existing expense record using the ORM
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('main_app:home')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'main_app/edit_expense.html', {'form': form})

#return a report of expenses filtered by the user's criteria
def filtered_report(request):
    expenses = Expense.objects.select_related('category').none() 
    stats = {}
    # Populate the form with GET data if available 
    # (implicitly accesses the DB using ORM)
    form = ReportFilterForm(request.GET or None) 

    if form.is_valid():
        queryset = Expense.objects.select_related('category').all()

        #get the user's filter criteria
        category = form.cleaned_data.get('category')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        # Apply filters conditionally
        if category:
            queryset = queryset.filter(category=category)
        if start_date:
            #only show expenses from the start date onwards 
            queryset = queryset.filter(date__gte=start_date) 
        if end_date:
            #only show expenses up to and including the end date
            queryset = queryset.filter(date__lte=end_date)  

        # Order the results implicitly
        expenses = queryset.order_by('-date')

        # Calculate statistics on the filtered queryset (filtered report view)
        # executes a query using the ORM
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

