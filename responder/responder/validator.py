import cerberus

v = cerberus.Validator()

schema_type_id = {
    'type_id': {
        'type': 'dict',
        'schema': {
                'id': {
                    'type': 'string',
                    'allowed': ['vab','betald_sjukdag','obetald_sjukdag','intern_arbete','semester','foraldrar_ledigt']
                }
        }
    }
}

schema_date_range = {
    'date': {
        'type': 'dict',
        'schema': {
            'start': {
                'type': 'string',
                'anyof': [
                            {'regex': '[0-9]{4}-[0-9]{2}-[0-9]{2}' },
                            {'regex': '^today$'}
                         ]
                },
            'end': {
                'type': 'string',
                'regex': '[0-9]{4}-[0-9]{2}-[0-9]{2}',
                'nullable': True
            }
        }
    }
}

schema_hour = {
    'hours': {
        'type': 'dict',
        'schema': {
            'hour': {
                'type': 'number',
                'min': 1,
                'max': 8,
                'nullable': True,
                'empty': True
            }
        }
    }
}



schema_all = { **schema_type_id, **schema_date_range, **schema_hour }



"""
example of a challenge

challenge = {

    'hours':{
        'hour': 100,
    },
    'date': {
        'start': 'tomorrow'
    }
}
"""

def validate_type(type_id):
    # type_id = 'timereport <vab> 2018-09-11:2018-09-12 8'
    # validates <type_id> is one of schema_type_id at index 1
    type_id = type_id.split(' ')[1]
    challenge = {'type_id': {'id': type_id}}
    return v.validate(challenge, schema_type_id)

def validate_date_start(date_range):
    # date_range = 'timereport vab <2018-09-11:2018-09-12> 8'
    # validates <date_start:date_end> is one of schema_date_range at index 2
    date_start = date_range.split(' ')[2].split(':')[0]
    challenge = {'date': {'start': date_start}}
    return v.validate(challenge, schema_date_range)

def validate_date_end(date_range):
    # date_range = 'timereport vab <2018-09-11:2018-09-12> 8'
    # validates <date_start:date_end> is one of schema_date_range at index 2
    if ':' in date_range:
        date_end = date_range.split(' ')[2].split(':')[1]
        challenge = {'date': {'end': date_end}}
    else:
        # no date_end or wrong value so default to None
        challenge = {'date': {'end': None}}
    return v.validate(challenge, schema_date_range)


def validate_hour(date_range):
    # date_range = 'timereport vab 2018-09-11:2018-09-12 <8>'
    # validates <hour> is one of schema_hour at last index
    if len(date_range.split(' ')) >= 4:
        hour = date_range.split(' ')[-1:][0]
        if hour.isdigit():
            hour = int(hour)
            challenge = {'hours': {'hour': hour}}
    else:
        # default to 8
        challenge = {'hours': {'hour': 8}}
    return v.validate(challenge, schema_hour)


def validate_all(input):
    # validates all
    result = []
    result.append(validate_type(input))
    result.append(validate_date_start(input))
    result.append(validate_date_end(input))
    result.append(validate_hour(input))
    return result
