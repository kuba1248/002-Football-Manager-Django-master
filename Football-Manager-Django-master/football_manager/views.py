from django.shortcuts import render, redirect, HttpResponse
from .models import User, Club, Player, Transfer, Transfer_Archived
from django.contrib import messages
import bcrypt, requests, json, time


# this is the root page for register
def viewRegister(request):
    return render(request, 'register.html')


# register new user
def register(request):
    errors = User.objects.regValidator(request.POST)

    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/')
    else:
        hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        User.objects.create(first_name=request.POST['firstname'], last_name=request.POST['lastname'],
                            email=request.POST['email'], password=hashed_pw)
        print(hashed_pw)

        request.session['user_name'] = User.objects.last().first_name + ' ' + User.objects.last().last_name
        request.session['user_id'] = User.objects.last().id
        request.session['email'] = User.objects.last().email  # need this in updateUser method below
        # print(request.session['user_name'], request.session['user_id'])
        return redirect('/home')


# View login page
def viewLogin(request):
    return render(request, 'login.html')


def login(request):
    request.session.flush()  # logout existing user before login
    errors = User.objects.loginValidator(request.POST)
    # print("login erros:____")
    # print(errors)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/view_login')
    else:
        # username password check logic is in loginValidator method in models.py
        # get logged in user from db
        this_user = User.objects.get(email=request.POST['email'])
        request.session['user_name'] = this_user.first_name
        request.session['user_id'] = this_user.id
        request.session['email'] = this_user.email  # need this in updateUser method below
        # print("login successful, redirecting to home page")
        # print("THIS USER is ", request.session['user_name'], "id = ", request.session['user_id'])
        return redirect('/home')


def viewHome(request):
    # Check if request method was GET (!= POST), then redirect to root
    if request.method != "POST":
        # Check if user_name is not in session
        # this allows the user to directly go to '/home' if user is in session; if not, redirect to root
        if 'user_name' not in request.session:
            return redirect('/')
    # On successful log/registration, render the home page
    context = {
        "all_transfers": Transfer_Archived.objects.all(),
    }
    return render(request, 'home.html', context)


# Methods for Users
def viewUser(request, id):
    context = {
        "this_user": User.objects.get(id=id)
    }
    return render(request, 'user.html', context)


def editAccount(request):
    context = {
        "this_user": User.objects.get(id=request.session['user_id'])
    }
    return render(request, 'my_account.html', context)


def updateUser(request):
    errors = User.objects.updateValidator(request.POST, request.session['email'])
    # check for input errors
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/edit_account')
    else:
        # update the user info
        this_user = User.objects.get(id=request.session['user_id'])
        this_user.first_name = request.POST['firstname']
        this_user.last_name = request.POST['lastname']
        this_user.email = request.POST['email']
        this_user.save()
    return redirect('/home')


def logout(request):
    request.session.flush()
    return redirect('/view_login')


# Manager Center Pages

def managerCenter(request):
    this_user = User.objects.get(id=request.session['user_id'])
    print("Entered manager center method and stored user")
    print(this_user.first_name)

    # Using Try/Except to avoid RelatedObjectDoesNotExist Error
    try:
        # If the user is already associated with a club/team, render the manager center page
        if this_user.club:
            print(this_user.club)
            print(this_user.club.name)
            budget = (this_user.club.budget) / 1000000
            print(budget)
            context = {
                "team": this_user.club,
                "budget": budget,
            }
        return render(request, 'manager_center.html', context)
    # If no associated club is found, render the select team page
    except Club.DoesNotExist:
        print("User does not have any associated club")
        pass
    context = {
        "all_teams": Club.objects.filter(manager=None),
        "all_leagues": ["Premier League", "Ligue 1", "La Liga", "Bundesliga", "Seria A"]
    }
    return render(request, 'select_team.html', context)


def assignTeam(request):
    this_user = User.objects.get(id=request.session['user_id'])
    selected_club = Club.objects.get(name=request.POST['team_name'])
    selected_club.manager = this_user
    selected_club.save()

    return redirect('/manager_center')


def viewSquad(request):
    this_user = User.objects.get(id=request.session['user_id'])
    club_players = this_user.club.players.all()
    context = {
        "club_players": club_players,
        "team": this_user.club,
    }
    return render(request, 'squad.html', context)


# def transferHub(request):
#     this_user = User.objects.get(id=request.session['user_id'])
#     # club_players = this_user.club.players.all()
#     print("TransferHub Method, storing club transfers")
#     club_transfers = []
#     #get selling transfers
#     selling = this_user.club.selling_transfers.all()
#     #get buying transfers
#     buying = this_user.club.buying_transfers.all()
#     club_transfers = selling | buying
#     #exclude denied transfer offers
#     club_transfers = club_transfers.exclude(approved=False)
#     context = {
#         # "club_players" : club_players,
#         "team" : this_user.club,
#         "club_transfers" : club_transfers,
#     }
#     return render (request, 'transfers.html', context)

def transferHub(request):
    this_user = User.objects.get(id=request.session['user_id'])
    print("TransferHub Method, storing club transfers")
    selling = Transfer_Archived.objects.filter(seller_club_name=this_user.club.name)
    buying = Transfer_Archived.objects.filter(buyer_club_name=this_user.club.name)
    club_transfers = selling | buying
    # exclude denied transfer offers
    club_transfers = club_transfers.exclude(approved=False)
    all_clubs = Club.objects.all()
    # exclude own club from search options
    all_clubs = all_clubs.exclude(id=this_user.club.id)
    context = {
        "team": this_user.club,
        "club_transfers": club_transfers,
        "all_clubs": all_clubs,
    }
    return render(request, 'transfers.html', context)


def searchPlayerByName(request):
    this_user = User.objects.get(id=request.session['user_id'])
    errors = Player.objects.playerSearchValidator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect('/transfer_hub')
    else:
        search_results_last = Player.objects.filter(last_name__contains=request.POST['name'])
        print(search_results_last)
        search_results_first = Player.objects.filter(first_name__contains=request.POST['name'])
        # combine first_name and last_name searches
        if search_results_first:
            search_results = search_results_first | search_results_last
        else:
            search_results = search_results_last
    # remove matching players from your own club
    search_results = search_results.exclude(team=this_user.club.id)
    context = {
        "search_results": search_results,
    }
    return render(request, 'search_results.html', context)


def searchPlayerByPosAge(request):
    this_user = User.objects.get(id=request.session['user_id'])
    if request.POST['min_age']:
        search_results = Player.objects.filter(age__gte=request.POST['min_age'], position=request.POST['position'])
        print(search_results)
    else:
        search_results = Player.objects.filter(position=request.POST['position'])
    # remove matching players from your own club
    search_results = search_results.exclude(team=this_user.club.id)
    context = {
        "search_results": search_results,
    }
    return render(request, 'search_results.html', context)


def searchPlayerByClub(request):
    search_results = Player.objects.filter(team=request.POST['club'])
    context = {
        "search_results": search_results,
    }
    return render(request, 'search_results.html', context)


def approachToBuy(request):
    if request.method == "POST":
        # TO DO: Need to add logic to check if transfer fee is within buyer club budget - display error message if amount is more than budget

        this_user = User.objects.get(id=request.session['user_id'])
        this_player = Player.objects.get(id=request.POST['player_id'])
        # Create the Transfer object.... Pending: Need to check for duplicate transfer object in db
        Transfer.objects.create(price=request.POST['offered_price'], player=this_player, buyer_club=this_user.club,
                                seller_club=this_player.team)
        # To display an acknowledgement message on transfer hub page after submitting the offer.
        ack = Transfer.objects.offerAck()
        messages.error(request, ack)
    return redirect('/transfer_hub')


def myOffers(request):
    this_user = User.objects.get(id=request.session['user_id'])
    buying_offers = this_user.club.buying_transfers.all().order_by("-created_at")
    print(buying_offers)
    selling_offers = this_user.club.selling_transfers.all().order_by("-created_at")
    # exclude denied (completed) offers
    selling_offers = selling_offers.exclude(completed=True)
    print(selling_offers)
    context = {
        "buying_offers": buying_offers,
        "selling_offers": selling_offers,
    }
    return render(request, 'offers.html', context)


def approveOffer(request):
    if request.method == "POST":
        this_transfer = Transfer.objects.get(id=request.POST['transfer_id'])
        this_transfer.approved = True
        this_transfer.completed = True
        this_transfer.save()

        # Copy this record to Transfer_Archived table
        # This table is used to display transfer updates on home page.
        print("Approved the offer.. copying record to archived table")
        print(this_transfer.buyer_club.name)
        Transfer_Archived.objects.create(price=this_transfer.price, approved=True,
                                         player_first_name=this_transfer.player.first_name,
                                         player_last_name=this_transfer.player.last_name,
                                         buyer_club_name=this_transfer.buyer_club.name,
                                         seller_club_name=this_transfer.seller_club.name)
        # Adjust transfer fees balances
        this_transfer.buyer_club.budget -= this_transfer.price
        this_transfer.buyer_club.save()
        this_transfer.seller_club.budget += this_transfer.price
        this_transfer.seller_club.save()
        # Change Player's team
        player = this_transfer.player
        player.team = this_transfer.buyer_club
        player.save()
    return redirect('/offers')


def denyOffer(request):
    if request.method == "POST":
        this_transfer = Transfer.objects.get(id=request.POST['transfer_id'])
        this_transfer.approved = False
        this_transfer.completed = True
        this_transfer.save()
    # This record is not being copied to Transfer_Archived table
    return redirect('/offers')


def leaveJob(request):
    if request.method == "POST":
        this_user = User.objects.get(id=request.session['user_id'])
        # this_user.club = None
        this_club = this_user.club
        this_club.manager = None
        this_club.save()
        return redirect('/manager_center')


# --------------------------------------------------------------------ADMIN----------------------------------------------------------

# Admin Page
def adminPage(request):
    return render(request, 'admin.html')


# Pull Teams Data from Rapid API
def pullTeamsData(request):
    headers = {
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
        'x-rapidapi-key': "cff47e86b4mshe952fe170d5f906p120c80jsn4e28711e6a7b"
    }
    # Pull Teams/Clubs data for season 2020 (top 5 leagues)
    league_ids = {
        "Premier League": 2790,
        "Ligue 1": 2664,
        "La Liga": 2833,
        "Bundesliga": 2755,
        "Seria A": 2857,
    }

    for lid in league_ids:
        url = "https://api-football-v1.p.rapidapi.com/v2/teams/league/" + str(league_ids[lid])  # API URL
        response = requests.request("GET", url, headers=headers)  # API GET Call
        # print(response.text)
        teams = json.loads(response.text)

        # print teams pulled for debug
        for t in teams['api']['teams']:
            # print(t['name'])
            if not Club.objects.filter(name=t['name']):  # Check if club already exists in the DB
                Club.objects.create(name=t['name'], league=lid, api_id=t['team_id'])
    print("Fresh pull from Rapid API was successful")
    return redirect('/admin')


# Pull Players Data from Rapid API
def pullPlayersData(request):
    headers = {
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
        'x-rapidapi-key': "cff47e86b4mshe952fe170d5f906p120c80jsn4e28711e6a7b"
    }
    # team ids in db:
    # Premier League: 1-20
    # League 1: 21-40
    # La Liga: 41-60
    # Bundesliga: 61-78
    # Seria A: 79-98
    all_teams = Club.objects.filter(id__range=[44, 60])
    print(all_teams)

    for team in all_teams:
        url = f"https://api-football-v1.p.rapidapi.com/v2/players/squad/{team.api_id}/2020-2021"
        time.sleep(1)  # allow 1 sec for API server to respond
        print(url)
        response = requests.request("GET", url, headers=headers)  # API GET Call
        # print(response.text)
        players = json.loads(response.text)

        for p in players['api']['players']:
            # print(t['name'])
            # if not Player.objects.filter(first_name=p['firstname'], last_name=p['lastname']):    #Check if player already exists in the DB
            Player.objects.create(first_name=p['firstname'], last_name=p['lastname'], age=p['age'],
                                  position=p['position'], country=p['nationality'], team=team)
            print(f"player for team id {team.api_id} added to DB")
    print("Fresh pull from Rapid API was successful")
    return redirect('/admin')
