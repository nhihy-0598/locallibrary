from django.shortcuts import render, get_object_or_404
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from catalog.forms import RenewBookModelForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import datetime
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

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = DEFAULT_PAGINATE_BY

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact=BOOKINSTANCE_STATUS_ON_LOAN)
            .order_by('due_back')
        )
@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if request.method == 'POST':
        form = RenewBookModelForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={'renewal_date': proposed_renewal_date})
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'catalog/book_renew_librarian.html', context)

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def all_borrowed_books(request):
    bookinstance_list = BookInstance.objects.filter(status=BOOKINSTANCE_STATUS_ON_LOAN).order_by('due_back')
    context = {'bookinstance_list': bookinstance_list}
    return render(request, 'catalog/all_borrowed_books.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    permission_required = 'catalog.add_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )

class AuthorDetailView(generic.DetailView):
    model = Author
