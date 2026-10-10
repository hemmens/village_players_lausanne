update_mapping = {
    'productions': {
        'value': {'venue': 'venue', 'author': 'author', 'festival': 'festival'},
        'date': {'open': 'open_date', 'close': 'close_date'},
        'entry_lambda': lambda x: x['title']
    },
    'castcrew': {
        'value': {'role-name': 'role_name'},
        'date': [],
        'entry_lambda': lambda productions, people, x:
                            f"{productions.find_one({'_id': x['production']})['title']}"
                            f" / {people.find_one({'_id': x['person']})['surname']}"
                            f" / {x['role']}"
    },
    'festivals': {
        'value': {'venue': 'venue'},
        'date': {'open': 'open_date', 'close': 'close_date'},
        'entry_lambda': lambda x: x['title']
    },
    'people': {
        'value': {
            'address': 'address', 'postcode': 'postcode', 'address-private': 'address_private',
            'home-phone': 'home_phone', 'home-phone-private': 'home_phone_private',
            'mobile': 'mobile', 'mobile-private': 'mobile_private', 'email': 'email',
            'email-private': 'email_private', 'gender': 'gender',
            'committee-email': 'committee_email'
        },
        'date': {'gdpr': 'gdpr'},
    },
    'committee': {
        'value': {},
        'date': {},
    },
    'balance': {
        'value': {'amount': 'balance'},
        'date': [],
        'entry_lambda': lambda x: x['date'].strftime("%B %Y")
    },
}