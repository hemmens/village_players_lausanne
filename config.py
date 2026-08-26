MEMBER_TYPES = [
    'Full',
    'Honorary',
    'Sep-Nov',
    'Dec-Feb',
    'Mar-May',    
]
ROLE_TYPES = [
    'Director',
    'Stage Manager',
    'Lights',
    'Sound',
    'Front of House',
    'Cast',
    'Props',
    'Costumes',
    'Make-up',
]
TRANS_TYPES = [
    'Membership Subscription',
    'Production',
    "Entr'Acts",
    'Storage',
    'Materials',
    'Subscriptions',
    'Bank Charges',
    'Other',
]
SEASONS = [
    '2026-27',
    '2025-26',
    '2024-25',
]
GENDERS = [
    'Male',
    'Female',
    'Non-Binary',
    'Prefer not to say',
]
BANK_CHARGE=-5
NOT_OK = 'waiting'
OK = 'SUBMIT'
PASSWORD = "vpslausannedb00"
SEASON = int(SEASONS[-1][-2:])
STORAGE_COST = -370
STORAGE_OWNER = 'Procimmo Real Estate'
URI = f"mongodb+srv://chrishemmens:{PASSWORD}@vps-00.lk81a.mongodb.net/?retryWrites=true&w=majority&appName=VPS-00"
