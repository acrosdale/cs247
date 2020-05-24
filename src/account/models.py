from django.db import models, transaction
from django.utils import timezone
from hashlib import blake2b
from hmac import compare_digest

ASSET_CHOICES = (
    (1, "bit"),
    (2, "ether"),
    (3, 'zcoin')
)


def known_h_func(secret):
    _hash = blake2b(digest_size=64, key=secret)
    _hash.update(b'this is a known value')
    return _hash.hexdigest().encode('utf-8')


def verify(secret, sig):
    good_sig = known_h_func(secret)
    return compare_digest(good_sig, sig)


class Wallet(models.Model):
    """
        This model will represent a wallet. A wallet will can multiple
        currency attached to it.
    """
    username = models.CharField(max_length=25)
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
    stores hashes of locked contract. the leader hashes
    """
    hash = models.CharField(max_length=256)
    paths = models.ManyToManyField('Path')
    locked = models.BooleanField(default=True)
    owner = models.CharField(max_length=25)


class Path(models.Model):
    src = models.CharField(max_length=25)
    route_len = models.SmallIntegerField(default=1)
    redeemed = models.BooleanField(default=False)


class Secrets(models.Model):
    """
        store the secrets of redeemed contracts
    """
    secret = models.CharField(max_length=256)


class Transact(models.Model):
    contracts = models.ManyToManyField('Contract')
    committed = models.BooleanField(default=False)


class Contract(models.Model):
    """
        the contract will facilitate all the restriction needed to transfer escrowed assets
        block.timestamp can be current time when we check the times
    """
    receiverP = models.IntegerField()
    senderP = models.IntegerField()
    escrow = models.OneToOneField(Escrow, on_delete=models.DO_NOTHING)
    hashes = models.ManyToManyField(Hash)
    secrets = models.ManyToManyField(Secrets)
    published = models.BooleanField(default=False)
    init_time = models.DateTimeField(auto_now_add=True)
    # the len of the entire graph
    diameter = models.SmallIntegerField()
    # delta could be in 1 hr intervals
    delta = models.IntegerField(default=1)

    def deploy(self, owner):
        if owner == self.senderP and not self.published:
            # substract escrow amount from sender.wallet and pub contract
            wallet = Wallet.objects.get(id=self.senderP)
            currency = wallet.currencies.filter(type=self.escrow.type).first()

            if currency and currency.amount >= self.escrow.amount:
                currency.amount -= self.escrow.amount
                currency.save()
                self.published = True
                self.save()
                return True
        return False

    def redeem_path(self, secret, sig, receiver):
        # keep the list of path when called test is if one of th
        # path to the leader is still good
        _hash = self.hashes.filter(hash=known_h_func(secret).decode()).first()
        now = timezone.now()
        ret = False

        if self.receiverP == receiver and verify(secret, sig) and _hash:
            paths = _hash.paths.all()
            # find a valid path
            for path in paths:
                path_time_in_hr = (self.diameter + path.route_len + 1) * self.delta
                if now < (self.init_time + timezone.timedelta(hours=path_time_in_hr)):
                    # the path is good and secret are valid
                    # reveal secret on the contract
                    _secret = Secrets(secret=secret.decode())
                    _secret.save()
                    self.secrets.add(_secret)
                    _hash.locked = False
                    _hash.save()
                    ret = True
                    break
        return ret

    def redeem_i(self, secret, receiver):
        # keep the list of path when called test is if one of th
        # path to the leader is still good
        _hash = Hash.objects.get(hash=known_h_func(secret).decode())
        now = timezone.now()
        ret = False

        if self.receiverP == receiver and _hash:

            paths = _hash.paths.all()

            # find a valid path
            for path in paths:
                path_time_in_hr = (self.diameter + path.route_len + 1) * self.delta
                if now < (self.init_time + timezone.timedelta(hours=path_time_in_hr)):
                    # the path is good and secret are valid
                    # reveal secret on the contract
                    _secret = Secrets(secret=secret.decode())
                    _secret.save()
                    self.secrets.add(_secret)
                    _hash.locked = False
                    _hash.save()
                    ret = True
                    break
        return ret

    def claim(self, receiver):

        if self.receiverP == receiver:

            all_unlocked = True
            for h in self.hashes.all():
                if h.locked:
                    all_unlocked = False

            if all_unlocked:
                wallet = Wallet.objects.get(id=self.receiverP)
                currency = wallet.currencies.get(type=self.escrow.type)
                currency.amount += self.escrow.amount
                currency.save()
                self.escrow.paid = True
                self.escrow.save()
        else:
            all_unlocked = False

        return all_unlocked

    def refund(self, sender):
        ret = False
        if self.senderP == sender and self.hashes.filter(locked=True).exists():
            now = timezone.now()
            max_len = 0

            for h in self.hashes.all():
                _path = h.paths.all().order_by('-route_len')

                if _path and max_len < _path[0].route_len:
                    max_len = _path[0].route_len

            path_time_in_hr = (self.diameter + max_len + 1) * self.delta

            if now >= (self.init_time + timezone.timedelta(hours=path_time_in_hr)):
                wallet = Wallet.objects.get(id=self.senderP)
                currency = wallet.currencies.get(type=self.escrow.type)
                currency.amount += self.escrow.amount
                currency.save()
                self.escrow.paid = True
                self.escrow.save()
                ret = True
        return ret
