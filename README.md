# sumologic-cse-python-sdk
https://api.sumologic.com/docs/sec/#

# Getting Started
see the scripts section for examples. In general either set env vars:
- SUMO_ACCESS_ID
- SUMO_ACCESS_KEY
  
or you must privide as arguments.

The default endpoint is the prod us1 instance. 
You can define another endpoint via the endpoint parameter when creating the connection object.

There is code that supposedly redirects to the correct API without an endpoint I haven't tested if this works.

To create connection:
```
from sumologiccse.sumologiccse import SumoLogicCSE
cse=SumoLogicCSE(endpoint='us2')
```

Then use any method such as:
```
q = '-status:"closed" created:>2022-11-17T00:00:00+00:00'
insights = cse.get_insights(q=q)
```

There are a lot of API endpoints you can also call them directly for example:
```
statuses = cse..get('/insight-status')
```

# TODOs
- Add a decent selection of endpoints
- Write some unit and integration tests