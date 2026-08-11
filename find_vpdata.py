from datetime import date
import pandas as pd

from pymongo.synchronous.collection import Collection

import vp_tools as vpt

def get_membership_list(
    members: Collection,
    people: Collection,
    payments: Collection,
    season: list[str],
    m_type: list[str],
) -> pd.DataFrame:
    member_df = pd.DataFrame(members.find(
        {'season': season, 'type': {'$in': m_type}}
    ))
    person_df = pd.DataFrame(people.find())
    payment_df = pd.DataFrame(payments.find(
        {'Type': 'Membership Subscription', 'Amount': {'$gt': 0}}
    ))
    person_df.drop('gdpr', axis=1, inplace=True)

    for column in ['_id', 'person', 'payment']:
        member_df[column] = vpt.convert_objid_to_str(member_df[column])
            
    person_df._id = vpt.convert_objid_to_str(person_df._id)
    person_df.set_index('_id', inplace=True)
            
    payment_df._id = vpt.convert_objid_to_str(payment_df._id)
    payment_df.set_index('_id', inplace=True)

    member_df = member_df.join(person_df, 'person')
    # member_df = member_df.join(payment_df, 'payment')
    return member_df
