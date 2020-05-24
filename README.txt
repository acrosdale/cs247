run -- directory which contains runtime data, like static files, sockets, etc..
doc -- folder to keep documentation
log -- all loggers should write to files in this folder
env -- env
src -- django root


setup environments
    goto root level;
    python3 -m venv env;
    source env/bin/activate;
    pip install --upgrade pip;
    pip install -r /path/to/requirements.txt;

DB setup for site
https://www.digitalocean.com/community/tutorials/how-to-create-a-django-app-and-connect-it-to-a-database
PYTHON 3.7 and up


usable endpoints on http://127.0.0.1:8000/ [setup endpoint first. used setup environments instruction]

    'test/'  # generate test data with transaction

    # view transaction ie all contract in a transaction. after calling test endpoint use transact_id = 1 to see detail
    'transact/details/<int:transact_id>/

    # contract function
    'contracts/redeem/'  # POST sample  {'secret': string, 'receiver': string, 'is_pseudo_sink': bool}
    'contract/claim/<int:receiver>/<int:contract_id>/   # all info can be found on the transact detail above, for testing
    'contract/refund/<int:sender>/<int:contract_id>/' # all info can be found on the transact detail above, for testing
    'contract/deploy/<int:sender>/<int:contract_id>/' # all info can be found on the transact detail above, for testing
