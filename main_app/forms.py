from django import forms
from .models import Expense, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

##form to capture user's filter criteria for reports
class ReportFilterForm(forms.Form):
    #model choice field dynamically fetches categories from the database
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), 
        required=False, 
        #allows user to select all categories (not filter)
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

