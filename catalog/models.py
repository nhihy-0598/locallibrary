import uuid
from django.db import models
from django.urls import reverse
from .constants import MAX_LENGTH_NAME, MAX_LENGTH_AUTHOR_NAME, MAX_LENGTH_SUMMARY, MAX_LENGTH_ISBN
from django.contrib.auth.models import User
from datetime import date
from django.conf import settings

class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        help_text='Enter a book genre (e.g. Science Fiction)'
    )

    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Language(models.Model):
    """Model representing a language"""
    name = models.CharField(max_length=MAX_LENGTH_NAME, help_text="Enter the book's natural language")

    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=MAX_LENGTH_NAME)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=MAX_LENGTH_SUMMARY, help_text='Enter a brief description of the book')
    isbn = models.CharField(
        'ISBN',
        max_length=MAX_LENGTH_ISBN,
        unique=True,
        help_text='13 Character ISBN number'
    )
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')

    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])

class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text='Unique ID for this particular book across whole library'
    )
    book = models.ForeignKey('Book', on_delete=models.RESTRICT)
    imprint = models.CharField(max_length=MAX_LENGTH_NAME)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )

    class Meta:
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})'
    
    @property
    def is_overdue(self):
        return bool(self.due_back and date.today() > self.due_back)

class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=MAX_LENGTH_AUTHOR_NAME)
    last_name = models.CharField(max_length=MAX_LENGTH_AUTHOR_NAME)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'
