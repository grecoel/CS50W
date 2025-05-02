from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import AuctionListing, Bid, Comment, User
from .forms import AuctionListingForm, CommentForm
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404
from django.db.models import Max


def index(request):
    # Fetch active auctions where winner is None
    active_auctions = AuctionListing.objects.filter(winner=None)

    return render(request, 'auctions/index.html', {
        'listings': active_auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

###############################################

@login_required(login_url='auctions/login.html')
def create(request):
    """Render the form to create a new auction listing."""
    return render (request, "auctions/create.html",{
        'form': AuctionListingForm()
    })

@login_required(login_url='auctions/login.html')
def insert(request):
    """Handle the creation of a new auction listing."""
    form = AuctionListingForm(request.POST)
    if form.is_valid():
        auction = AuctionListing(user=request.user, **form.cleaned_data)
        if not auction.image_url:
            auction.image_url = 'https://user-images.githubusercontent.com/52632898/161646398-6d49eca9-267f-4eab-a5a7-6ba6069d21df.png'
        auction.save()

        # create initial bid
        starting_bid = auction.starting_bid
        bid = Bid(amount=starting_bid, user=request.user, auction=auction)
        bid.save()
        return HttpResponseRedirect(reverse('index'))
    else:
        # render the form with error msg
        return render(request, 'auction/create.html',{
            'form': form,
            'error': form.errors
        })


def listing(request, id):
    current = AuctionListing.objects.get(pk=id)

    # Get all bids associated with the auction
    bids = Bid.objects.filter(auction=current).order_by('-amount')  # Assuming you want the highest bid first

    # Get the highest bid, or None if no bids exist
    bid = bids.first() if bids.exists() else None

    comments = Comment.objects.filter(auction=current)
    print("here:" + AuctionListing.objects.get(pk=id).image_url)

    return render(request, 'auctions/listing.html', {
        'auction': current,
        'user': request.user,
        'bid': bid,
        'bids': bids,
        'comments': comments,
        'comment_form': CommentForm()
    })



@login_required(login_url='auctions/login.html')
def update_bid(request, id):
    """Update the bid for a specific auction listing."""
    amount = request.POST.get('bid')
    if amount:
        amount = float(amount)
        auction = get_object_or_404(AuctionListing, id=id)
        current_bid = auction.bid_set.latest('amount')  # Get the highest bid
        if amount > current_bid.amount:
            # Update the bid with the new highest bid
            new_bid = Bid(user=request.user, amount=amount, auction=auction)
            new_bid.save()
            auction.bid_counter += 1
            auction.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            raise ValidationError('Bid must be greater than the current bid value.')
    else:
        raise ValidationError('Bid amount cannot be empty.')

@login_required(login_url='auctions/login.html')
def close_bid(request, id):
    """Close the auction and mark the request user as the winner."""
    auction = get_object_or_404(AuctionListing, pk=id)
    auction.active = False
    auction.winner = request.user.username  
    auction.save()
    # Redirect to the index page after closing the auction
    return HttpResponseRedirect(reverse('index'))



@login_required(login_url='auctions/login.html')
def watchlist(request):
    """Display the user's watchlist."""
    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watchlist.all()
    })


@login_required(login_url='auctions/login.html')
def watch(request, id):
    """Add an auction listing to the user's watchlist."""
    auction = get_object_or_404(AuctionListing, id=id)
    request.user.watchlist.add(auction)
    request.user.watchlist_counter += 1
    request.user.save()
    return HttpResponseRedirect(reverse('index'))


@login_required(login_url='auctions/login.html')
def unwatch(request, id):
    """Remove an auction listing from the user's watchlist."""
    auction = get_object_or_404(AuctionListing, id=id)
    request.user.watchlist.remove(auction)
    request.user.watchlist_counter -= 1
    request.user.save()
    return HttpResponseRedirect(reverse('index'))

def categories(request):
    """Render the categories page."""
    return render(request,"auctions/categories.html")

def filter(request):
    """Filter auction listings by category."""
    q = request.GET.get('category', '').lower()
    listings = AuctionListing.objects.filter(category=q)
    return render(request, 'auctions/category.html', {
        'listings': listings
    })

def add_comment(request, id):
    """Add a comment to an auction listing."""
    if request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                user=request.user,
                auction=get_object_or_404(AuctionListing, id=id),
                **form.cleaned_data
            )
            comment.save()
            return HttpResponseRedirect(reverse('listing', kwargs={'id': id}))
    else:
        return render(request, 'auctions/login.html', {
            'message': 'Must be logged in to comment!'
        })
