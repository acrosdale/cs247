from django.urls import path, include
from django.contrib import admin
from account.views import (
    GenTest,
    TransactDetails,
    PublishedContract,
    RedeemContracts,
    ClaimContracts,
    RefundContracts
)

urlpatterns = [
    path(r'test/', GenTest.as_view()),
    path(r'transact/details/<int:transact_id>/', TransactDetails.as_view()),
    # contract function
    path(r'contracts/redeem/', RedeemContracts.as_view()),
    path(r'contract/claim/<int:user_id>/<int:contract_id>/', ClaimContracts.as_view()),
    path(r'contract/refund/<int:user_id>/<int:contract_id>/', RefundContracts.as_view()),
    path(r'contract/deploy/<int:user_id>/<int:contract_id>/', PublishedContract.as_view()),

]
