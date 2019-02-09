#!/bin/bash
if [[ $# -lt 5 ]]; then
  echo "arguments missing"
  echo "$basename <endpoint> <action> <reason> <date_start> <date_end>"
  echo "$basename 127.0.0.1:8080 add vab 2018-12-03 2018-12-05"
  exit
fi
# if add then generate random uid
# generate random user_id uppercase and 9 characters
NEW_UID=$(openssl rand -hex  9 | tr 'a-z' 'A-Z' | fold -w 9 | head -1)

if [[ $2 == 'add' ]]; then

  curl -X POST -d "{
  'body': 'token=fake_token&team_id=CHANGEME&team_domain=codelabsab&channel_id=CA8THJML6&channel_name=development&user_id=$NEW_UID&user_name=test.user&command=%2Fno-wsgi&text=$2+$3+$4:$5&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT2FG58LDV%2F491076166711%2FbVUlrKZrnElSOBUqn01FoxNf&trigger_id=490225208629.83549292471.860541eab9e9c3c6d7464ea2e979c7a5'
  }" $1
else
  curl -X POST -d "{
  'body': 'token=fake_token&team_id=CHANGEME&team_domain=codelabsab&channel_id=CA8THJML6&channel_name=development&user_id=U2FGC795G&user_name=test.user&command=%2Fno-wsgi&text=$2+$3+$4:$5&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT2FG58LDV%2F491076166711%2FbVUlrKZrnElSOBUqn01FoxNf&trigger_id=490225208629.83549292471.860541eab9e9c3c6d7464ea2e979c7a5'
  }" $1
fi

# test "today"
curl -X POST -d "{'body':
'token=OwjK95k89vMbtbyvhvLZkXNl&team_id=CHANGEME&team_domain=codelabsab&channel_id=CA8THJML6&channel_name=development&user_id=U2FGC795G&user_name=kamger&command=%2Fno-wsgi&text=add+vab+today&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT2FG58LDV%2F491076166711%2FbVUlrKZrnElSOBUqn01FoxNf&trigger_id=490225208629.83549292471.860541eab9e9c3c6d7464ea2e979c7a5'}"
