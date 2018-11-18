import cerberus

v = cerberus.Validator()

schema_type_id = {
    'type': {
        'type': 'string',
        'allowed': ['vab','betald_sjukdag','obetald_sjukdag','intern_arbete','semester','foraldrar_ledigt']
    }
}

schema_date_range = {
    'date_start': {
        'type': 'string',
        'anyof': [ {'regex': '[0-9]{4}-[0-9]{2}-[0-9]{2}' }, {'regex': '^today$'} ]
    },
    'date_end': {
        'type': 'string',
        'regex': '[0-9]{4}-[0-9]{2}-[0-9]{2}',
        'nullable': True
    }
 }

schema_hour = {
    'hour': {
        'type': 'number',
        'min': 1,
        'max': 8,
        'nullable': True,
        'empty': True
    }
}

def validate_type(type_id):
    # type_id = 'timereport <vab> 2018-09-11:2018-09-12 8'
    # validates <type_id> is one of schema_type_id at index 1
    type_id = type_id.split(' ')[1]
    return v.validate(dict(type=type_id), schema_type_id)

def validate_date_start(date_range):
    # date_range = 'timereport vab <2018-09-11:2018-09-12> 8'
    # validates <date_start:date_end> is one of schema_date_range at index 2
    date_start = date_range.split(' ')[2].split(':')[0]
    return v.validate(dict(date_start=date_start), schema_date_range)

def validate_date_end(date_range):
    # date_range = 'timereport vab <2018-09-11:2018-09-12> 8'
    # validates <date_start:date_end> is one of schema_date_range at index 2
    if ':' in date_range:
        date_end = date_range.split(' ')[2].split(':')[1]
        return v.validate(dict(date_end=date_end), schema_date_range)
    else:
        # no date_end so default to date_start
        date_end = date_range.split(' ')[2]
        if 'today' in date_end:
            date_end = None
            return v.validate(dict(date_end=date_end), schema_date_range)
        return v.validate(dict(date_end=date_end), schema_date_range)

def validate_hour(date_range):
    # date_range = 'timereport vab 2018-09-11:2018-09-12 <8>'
    # validates <hour> is one of schema_hour at last index
    if len(date_range.split(' ')) >= 4:
        hour = date_range.split(' ')[-1:][0]
        if hour.isdigit():
            return v.validate(dict(hour=int(hour)), schema_hour)
    else:
        hour = None
        return v.validate(dict(hour=hour), schema_hour)