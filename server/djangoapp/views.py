# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provided credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName": "", "status": "Logged Out"}
    return JsonResponse(data)

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    context = {}

    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)
        
# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    try:
        dealerships = initiate.get_dealerships()
        return render(request, 'index.html', {"dealerships": dealerships})
    except Exception as e:
        logger.error(f"Error fetching dealerships: {e}")
        return HttpResponse("Error fetching dealerships", status=500)

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    try:
        reviews = initiate.get_dealer_reviews(dealer_id)
        return JsonResponse(reviews, safe=False)
    except Exception as e:
        logger.error(f"Error fetching dealer reviews: {e}")
        return JsonResponse({"status": "Error", "message": "Error fetching dealer reviews"})

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    try:
        dealer_details = initiate.get_dealer_details(dealer_id)
        return JsonResponse(dealer_details, safe=False)
    except Exception as e:
        logger.error(f"Error fetching dealer details: {e}")
        return JsonResponse({"status": "Error", "message": "Error fetching dealer details"})

# Create an `add_review` view to submit a review
@csrf_exempt
def add_review(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            review = data['review']
            dealer_id = data['dealerId']
            response = initiate.add_review(dealer_id, review)
            return JsonResponse({"status": "Success", "message": "Review submitted successfully", "response": response})
        except Exception as e:
            logger.error(f"Error submitting review: {e}")
            return JsonResponse({"status": "Error", "message": "Error submitting review"})
    return JsonResponse({"status": "Error", "message": "Invalid request method"})
