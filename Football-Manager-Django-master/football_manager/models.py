from django.db import models
import re, bcrypt


class UserManager(models.Manager):
    def regValidator(self, postData):
        errors = {}
        # input validations
        if len(postData['firstname']) < 2:
            errors['firstname'] = "First Name should atleast be 2 charecters"
        if len(postData['lastname']) < 2:
            errors['lastname'] = "Last Name should atleast be 2 charecters"
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):  # test whether a field matches the pattern
            errors['email'] = "Invalid email address!"
        # check if entered email is unique
        if User.objects.filter(email=postData['email']):
            errors['email_unq'] = "This email is already registered!"
        if len(postData['password'] or postData['password_conf']) < 8:
            errors['password_len'] = "Password should atleast be 8 charecters"
        if postData['password'] != postData['password_conf']:
            errors['password_match'] = "Passwords do not match"
        return errors

    def loginValidator(self, postData):
        errors = {}
        this_user = User.objects.filter(email=postData['email'])
        # check if the user exists (based on email)
        if (this_user):
            this_user = this_user[
                0]  # above 'filter' method returns a list of ONE object. So we reassign the var to the first element in the list.
            # compare hashed passwords
            if bcrypt.checkpw(postData['password'].encode(), this_user.password.encode()):
                print("LOGIN SUCCESSFUL")
                return errors
        else:
            errors['login'] = "Login failed! Check email and password"
        return errors

    def updateValidator(self, postData, current_user_email):
        errors = {}
        # input validations
        if len(postData['firstname']) < 2:
            errors['firstname'] = "First Name should atleast be 2 charecters"
        if len(postData['lastname']) < 2:
            errors['lastname'] = "Last Name should atleast be 2 charecters"
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):  # test whether a field matches the pattern
            errors['email'] = "Invalid email address!"
        # prevent the user from providing an email already registered with other user, but also allow to submit their same email again
        if postData['email'] != current_user_email:
            # now check if email is unique
            if User.objects.filter(email=postData['email']):
                errors['email_unq'] = "This email is already registered to another user!"
        return errors

        # def teamSelector(self, postData):
    #     errors = {}


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()


class Club(models.Model):
    name = models.CharField(max_length=255)
    budget = models.IntegerField(default=80000000)
    rating = models.IntegerField(default=75)
    league = models.CharField(max_length=20, null=True)
    logo = models.ImageField()
    api_id = models.IntegerField()  # team_id from API-Football
    manager = models.OneToOneField(User, related_name="club", on_delete=models.PROTECT, null=True)  # one-to-one
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PlayerManager(models.Manager):
    def playerSearchValidator(self, postData):
        errors = {}
        # input validations for search by name only
        if len(postData['name']) < 2:
            errors['name'] = "Name should atleast be 2 charecters"
            print(errors)
        return errors


class Player(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()
    position = models.CharField(max_length=3)
    price = models.IntegerField(default=20000000)
    contract_length = models.IntegerField(default=36)  # months
    rating = models.IntegerField(default=70)
    country = models.CharField(max_length=20, default="Unknown")
    on_loan = models.BooleanField(default=False)
    team = models.ForeignKey(Club, related_name="players", on_delete=models.PROTECT)  # one to many
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PlayerManager()


class TransferManager(models.Manager):
    def offerAck(self):
        ack = "Offer Sent to Player's Club"
        return ack


class Transfer(models.Model):
    price = models.IntegerField()
    approved = models.BooleanField(default=False)
    transaction = models.CharField(choices=(("Loan", "Loan"), ("Sell", "Sell")), max_length=20, default="Sell")
    completed = models.BooleanField(default=False)
    # buyer_club = models.ManyToManyField(Club, related_name="buying_transfers") #many to many
    # seller_club = models.ManyToManyField(Club, related_name="selling_transfers") #many to many
    buyer_club = models.ForeignKey(Club, related_name="buying_transfers", on_delete=models.CASCADE)  # one to many
    seller_club = models.ForeignKey(Club, related_name="selling_transfers", on_delete=models.CASCADE)  # one to many
    player = models.ForeignKey(Player, related_name="transfers", on_delete=models.CASCADE)  # one to many
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TransferManager()


# No relationships in this model as it breaks existing db.
class Transfer_Archived(models.Model):
    price = models.IntegerField()
    approved = models.BooleanField()
    player_first_name = models.CharField(max_length=255)
    player_last_name = models.CharField(max_length=255)
    transaction = models.CharField(choices=(("Loan", "Loan"), ("Sell", "Sell")), max_length=20, default="Sell")
    buyer_club_name = models.CharField(max_length=255, null=True)
    seller_club_name = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
