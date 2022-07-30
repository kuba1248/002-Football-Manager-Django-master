from django.urls import path
from . import views

urlpatterns = [
    path('', views.viewRegister),
    path('register', views.register),
    path('view_login', views.viewLogin),
    path('login', views.login),
    path('home', views.viewHome),
    # path('post_quote', views.postQuote), #post quote
    # path('post_like', views.postLike), #post a like
    # path('delete_quote', views.deleteQuote), #delete a quote
    path('user/<int:id>', views.viewUser),
    path('edit_account', views.editAccount),
    path('update_user', views.updateUser),
    path('logout', views.logout),

    path('manager_center', views.managerCenter),
    path('search_team', views.assignTeam),
    path('squad', views.viewSquad),
    path('transfer_hub', views.transferHub),
    path('search_player_name', views.searchPlayerByName),
    path('search_player_position_age', views.searchPlayerByPosAge),
    path('search_player_club', views.searchPlayerByClub),
    path('approach_to_buy', views.approachToBuy),
    path('offers', views.myOffers),
    path('approve', views.approveOffer),
    path('deny', views.denyOffer),

    path('leave_job', views.leaveJob),

    path('admin', views.adminPage),
    path('pull_teams_data', views.pullTeamsData),
    path('pull_players_data', views.pullPlayersData),
]