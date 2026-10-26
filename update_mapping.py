grey_out = {
    "backgroundColor": "#e9ecef",
    "color": "#6c757d",
    # "border": "1px solid #ced4da",
}

update_mapping = {
    'productions': {
        'value': {'venue': 'venue', 'author': 'author', 'festival': 'festival'},
        'date': {'open': 'open_date', 'close': 'close_date'},
    },
    'castcrew': {
        'value': {'role-name': 'role_name'},
        'date': {},
    },
    'festivals': {
        'value': {'venue': 'venue'},
        'date': {'open': 'open_date', 'close': 'close_date'},
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
