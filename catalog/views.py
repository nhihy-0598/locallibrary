from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_instances_available = BookInstance.objects.filter(status__exact=BookInstance.LOAN_STATUS[2][0]).count()
    num_authors = Author.objects.count()
    
    context = {
    'num_books': num_books,
    'num_instances': num_instances,
    'num_instances_available': num_instances_available,
    'num_authors': num_authors,
    }
    
    return render(request, 'index.html', context=context)
