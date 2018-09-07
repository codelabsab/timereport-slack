# Config for timereport
date_regex_start = "([0-9]{4}-[0-9]{2}-[0-9]{2}|today)"
date_regex_end = ":([0-9]{4}-[0-9]{2}-[0-9]{2})?"
hour_regex = " ([0-9]) "
type_regex = "(vab|betald_sjukdag|obetald_sjukdag|intern_arbete|semester|foraldrar_ledigt)"

def validate_user_name(type_id, date_start, date_end, hours):
   user_name_regex = "(?:{typid}).(?:{start}).(?:{end})?.(?:{hours})?.?(\w+[.]\w+)".format(typid=type_id, start=date_start, end=date_end, hours=hours)
   return user_name_regex
