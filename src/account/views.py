from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from account.utils import XChainWeb
from account.models import (
    Wallet,
    Currency,
    known_h_func,
    Transact,
    Contract
)


class GenTest(APIView):

    def get(self, request):

        response = Response(data={})
        nodes = ['A', 'B', 'C']
        edges = [('A', 'C'), ('B', 'C'), ('B', 'A'), ('C', 'B')]
        node_values = {
            'A->C': (2, 'bit'),
            'B->C': (1, 'bit'),
            'B->A': (1, 'zcoin'),
            'C->B': (2, 'ether')
        }
        secrets = {'A': b'secret1', 'B': b'secret2', 'C': b'secret3'}
        hashes = {
            'A': known_h_func(secrets['A']),
            'B': known_h_func(secrets['B']),
            'C': known_h_func(secrets['B'])
        }

        # create test wallets and add some test currency
        for user in ['A', 'B', 'C']:
            currency1 = Currency(amount=10, type='bit')
            currency2 = Currency(amount=10, type='ether')
            currency3 = Currency(amount=10, type='zcoin')

            currency1.save()
            currency2.save()
            currency3.save()

            wallet = Wallet(username=user)
            wallet.save()
            wallet.currencies.add(currency3, currency1, currency2)

        xc = XChainWeb(nodes=nodes, edges=edges, node_values=node_values, hashes=hashes, tranform_graph=True)
        xc.build_xchain_data()
        xc.build_xchain_contracts()

        # deploy contract
        # for contract in Contract.objects.all():
        #     contract.deploy(contract.senderP)

        response.data['msg'] = 'test data generated'
        return response


class TransactDetails(APIView):

    def get(self, request, transact_id):
        response = Response(data={})

        transact = Transact.objects.filter(id=transact_id).first()
        committed = True

        if transact:
            response.data['transact-id'] = transact_id
            response.data['committed'] = committed
            response.data['contracts_count'] = 0
            response.data['rep_sources'] = transact.rep_sources
            response.data['rep_sinks'] = transact.rep_sinks
            response.data['followers'] = transact.followers
            response.data['leaders'] = transact.leaders
            response.data['feedback_vs'] = transact.feedback_vs
            response.data['contracts'] = list()

            for contract in transact.contracts.all():

                if not contract.escrow.paid:
                    committed = False

                response.data['contracts'].append({
                    'id': contract.id,
                    'deployed': contract.published,
                    'claim': contract.escrow.paid,
                    'sender': contract.senderP,
                    'reciever': contract.receiverP,
                    'init_time': contract.init_time,
                    'escrow': {
                        'value': contract.escrow.amount,
                        'type': contract.escrow.type
                    },
                    'hashes': contract.hashes.all().values_list("hash", flat=True),
                    'secrets': contract.secrets.all().values_list("secret", flat=True)
                })
                response.data['contracts_count'] += 1

        response.data['committed'] = committed
        return response


class PublishedContract(APIView):

    def get(self, request, user_id, contract_id):
        response = Response(data={})
        status = "not deployed"

        if user_id and contract_id:
            contract = Contract.objects.filter(senderP=user_id, id=contract_id).first()

            if contract and contract.deploy(user_id):
                status = 'deployed'
                # update contract time to now. contract is officailly deployed
                contract.init_time = timezone.now()
                contract.save()

        response.data['msg'] = {
            'contract': contract_id,
            'status': status
        }

        return response


class RedeemContracts(APIView):

    """
        {
            "secret":"secret2",
            "receiver":3,
            "is_pseudo_sink" : 1
        }
    """

    def post(self, request):

        response = Response(data={})
        secret = request.data.get('secret', None)
        receiver = request.data.get('receiver', None)
        # this var is for when the rep sink gives secret to psuedo sink directly
        is_pseudo_sink = request.data.get('is_pseudo_sink', None)

        ret_dict = dict()

        if secret and receiver:
            contracts = Contract.objects.filter(receiverP=receiver)
            sig = known_h_func(secret.encode())
            secret = secret.encode()

            for contract in contracts:

                if is_pseudo_sink:
                    print('redeeming_i')
                    ret = contract.redeem_i(secret=secret, receiver=receiver)
                    ret_dict[contract.id] = ret
                else:
                    print('redeeming_path')
                    ret = contract.redeem_path(secret=secret, sig=sig, receiver=receiver)
                    ret_dict[contract.id] = ret

        response.data['contracts'] = ret_dict
        return response


class ClaimContracts(APIView):

    def get(self, request, user_id, contract_id):
        response = Response(data={})
        status = "not claimed"

        if user_id and contract_id:
            contract = Contract.objects.filter(receiverP=user_id, id=contract_id).first()

            if contract and contract.claim(user_id):
                status = 'claimed'

        response.data['msg'] = {
            'contract': contract_id,
            'status': status
        }

        return response


class RefundContracts(APIView):

    def get(self, request, user_id, contract_id):
        response = Response(data={})
        status = "not refund"

        if user_id and contract_id:
            contract = Contract.objects.filter(senderP=user_id, id=contract_id).first()

            if contract and contract.refund(user_id):
                status = 'refund'

        response.data['msg'] = {
            'contract': contract_id,
            'status': status
        }

        return response


