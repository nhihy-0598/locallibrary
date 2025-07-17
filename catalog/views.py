from django.shortcuts import render, get_object_or_404
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
from catalog.constants import (
    DEFAULT_PAGINATE_BY,
    BOOKINSTANCE_STATUS_AVAILABLE,
    BOOKINSTANCE_STATUS_MAINTENANCE,
    BOOKINSTANCE_STATUS_ON_LOAN,
    BOOKINSTANCE_STATUS_RESERVED,
)

# Create your views here.
class BookListView(generic.ListView):
    model = Book
    paginate_by = DEFAULT_PAGINATE_BY
    
class BookDetailView(generic.DetailView):
    model = Book

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bookinstances'] = self.object.bookinstance_set.all()
        from catalog.models import BookInstance
        context['status_choices'] = dict(BookInstance.LOAN_STATUS)
        context['STATUS_AVAILABLE'] = BOOKINSTANCE_STATUS_AVAILABLE
        context['STATUS_MAINTENANCE'] = BOOKINSTANCE_STATUS_MAINTENANCE
        context['STATUS_ON_LOAN'] = BOOKINSTANCE_STATUS_ON_LOAN
        context['STATUS_RESERVED'] = BOOKINSTANCE_STATUS_RESERVED
        return context

def book_detail_view(request, primary_key):
    book = get_object_or_404(Book, pk=primary_key)
    bookinstances = book.bookinstance_set.all()
    from catalog.models import BookInstance
    status_choices = dict(BookInstance.LOAN_STATUS)
    return render(request, 'catalog/book_detail.html', context={
        'book': book,
        'bookinstances': bookinstances,
        'status_choices': status_choices,
        'STATUS_AVAILABLE': BOOKINSTANCE_STATUS_AVAILABLE,
        'STATUS_MAINTENANCE': BOOKINSTANCE_STATUS_MAINTENANCE,
        'STATUS_ON_LOAN': BOOKINSTANCE_STATUS_ON_LOAN,
        'STATUS_RESERVED': BOOKINSTANCE_STATUS_RESERVED,
    })

def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_instances_available = BookInstance.objects.filter(status__exact=BookInstance.LOAN_STATUS[2][0]).count()
    num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits', 0) + 1
    request.session['num_visits'] = num_visits

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }
    
    return render(request, 'index.html', context=context)
