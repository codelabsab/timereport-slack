#!/bin/bash
if [[ $1 == '' ]]; then
  echo "$basename <endpoint> argument missing"
  exit
fi
curl -X POST -d '{
"body": "token=fake_token&team_id=CHANGEME&team_domain=codelabsab&channel_id=CA8THJML6&channel_name=development&user_id=U2FGC795G&user_name=kamger&command=%2Fno-wsgi&text=list+semester+2018-12-20:2018-12-22&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT2FG58LDV%2F491076166711%2FbVUlrKZrnElSOBUqn01FoxNf&trigger_id=490225208629.83549292471.860541eab9e9c3c6d7464ea2e979c7a5"
}' $1
