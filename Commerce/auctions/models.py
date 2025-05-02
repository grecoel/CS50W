from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Track the count of items in the user's watchlist
    watchlist_counter = models.IntegerField(default=0, blank = True)
    watchlist = models.ManyToManyField('AuctionListing', related_name='watchlist', blank=True)
    pass

class AuctionListing(models.Model):
    #FK to USer model to associate each listing with a creator
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Title of the auction item
    title = models.CharField(max_length=100)  
    description = models.TextField() # Description of th auction item
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    starting_bid = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(default='https://user-images.githubusercontent.com/52632898/161646398-6d49eca9-267f-4eab-a5a7-6ba6069d21df.png')
    bid_counter = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    winner = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.title} by {self.user.username}'

class Bid(models.Model):
    # ForeignKey to User model for bidder
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Bid amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Timestamp for when the bid was created or updated
    created_at = models.DateTimeField(auto_now=True)
    # ForeignKey to the related AuctionListing
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.amount} on {self.auction.title} by {self.user.username}'

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE) #FK to User for comment author
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE) # FK to the related AuctionListing

    def __str__(self):
        return f'{self.user.username}: {self.text[:20]}'
