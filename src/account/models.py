from django.db import models
from django.contrib.auth.models import User
import uuid

ASSET_CHOICES = (
    (1, "bitcoin"),
    (2, "etherium"),
    (3, 'z-coin')
)


class Wallet(models.Model):
    """
        This model will represent a wallet. A wallet will can multiple
        currency attached to it.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currencies = models.ManyToManyField('Currency')


class Currency(models.Model):
    """
        This model represent all type of support currencies that can exist in a wallet.
    """
    amount = models.FloatField(default=0.0)
    type = models.CharField(choices=ASSET_CHOICES, max_length=25)


class Escrow(models.Model):
    """
        This model will hold assets that are 'escrowed'
    """
    amount = models.FloatField(default=0.0)
    type = models.CharField(choices=ASSET_CHOICES, max_length=25)
    date_created = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)


class Hash(models.Model):
    """
    stores hashes of locked contract
    """
    hash = models.CharField(max_length=256)


class Secrets(models.Model):
    """
        store the secrets of redeemed contracts
    """

    secret = models.CharField(max_length=256)


class Contract(models.Model):
    """
        the contract will facilitate all the restriction needed to transfer escrowed assets
        block.timestamp can be current time when we check the times
    """
    receiverP = models.IntegerField()
    senderP = models.IntegerField()
    escrow = models.ForeignKey(Escrow, on_delete=models.DO_NOTHING)
    hashes = models.ManyToManyField(Hash)
    secrets = models.ManyToManyField(Secrets)
    locked = models.BooleanField(default=False)

    date_init = models.DateTimeField(auto_now_add=True)
    diameter = models.IntegerField()
    delta = models.IntegerField()

    class Meta:
        unique_together = ('receiverP', 'senderP',)

    def redeem(self, your_secret, your_hash):
        pass

    def claim(self, sender):
        assert isinstance(sender, User), 'expected a User obj'

    def refund(self, sender):
        assert isinstance(sender, User), 'expected a User obj'
