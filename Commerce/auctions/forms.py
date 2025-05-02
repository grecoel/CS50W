from django import forms
from django.conf import settings


class AuctionListingForm(forms.Form):
    title = forms.CharField(
        label='Title',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-group',
            'placeholder': 'Give it a title'
        })
    )
    description = forms.CharField(
        label='Description',
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control form-group',
            'placeholder': 'Tell more about the product',
            'rows': '3'
        })
    )
    price = forms.DecimalField(
        label='Price',
        required=False,
        initial=0.00,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-group',
            'placeholder': 'Estimated price (optional)',
            'min': '0.01',
            'max': '999999999.99',
            'step': '0.01'
        })
    )
    starting_bid = forms.DecimalField(
        label='Starting Bid',
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-group',
            'placeholder': 'Starting bid',
            'min': '0.01',
            'max': '99999999999.99',
            'step': '0.01'
        })
    )
    category = forms.ChoiceField(
        label='Category',
        required=False,
        choices=[('', 'Select a category'), ('electronics', 'Electronics'), ('fashion', 'Fashion'), ('home', 'Home'), ('toys', 'Toys'), ('magic', 'Magic')],
        widget=forms.Select(attrs={
            'class': 'form-control form-group'
        })
    )
    image_url = forms.URLField(
        label='Image URL',
        required=False,
        initial=getattr(settings, 'DEFAULT_IMAGE_URL', 'https://example.com/default.png'),
        widget=forms.TextInput(attrs={
            'class': 'form-control form-group',
            'placeholder': 'Image URL (optional)',
        })
    )

    def clean_starting_bid(self):
        amount = self.cleaned_data.get('starting_bid')
        if amount <= 0:
            raise forms.ValidationError('Starting bid must be greater than zero!')
        return amount


class CommentForm(forms.Form):
    text = forms.CharField(
        label='Comment',
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control-md lead form-group',
            'rows': '3',
            'cols': '100',
            'placeholder': 'Write your comment here...'
        })
    )

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 5:
            raise forms.ValidationError('Comment must be at least 5 characters long.')
        return text
