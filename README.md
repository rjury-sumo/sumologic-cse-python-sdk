# sumologic-cse-python-sdk
An api client similar to the official Sumologic python API client but for the CSE api: https://api.sumologic.com/docs/sec/#

This api has many endpoints this project only intends to cover off and provide useful scripts to solve some common use caes rather than support all of them.


# install package
```
pip install sumologiccse==0.0.1
```

# Getting Started
see the scripts section for examples. In general either set env vars:
- SUMO_ACCESS_ID
- SUMO_ACCESS_KEY
or you must privide as arguments.

The default endpoint is the prod us1 instance. endpoint param for another instance should be defined when creating the connection in sort or long form ie using endpoint:
- us2
- https://api.us2.sumologic.com/api/sec


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
statuses = cse.get('/insight-status')
```

# Example Use Case Scripts
You can find these in ./scripts

## Bulk Resolve Insights Script
For bulk closing insights using various criteria. This can be using the DSL (-q) or using client side filtering such as confidence score or a regex vs the json-ified payload. 

This has a dryrun mode set this to False to make updates.
The script will add a comment to each insight before changing it's status and resolution using the supplied params.

Assuming you set env vars as per above for key and id:
```
python ./scripts/insights/resolve_insights.py --endpoint 'us2' --dryrun True --limit 5 --query='-status:"closed"'
```

# TODOs
- Add a decent selection of endpoints
- Write some more unit and integration tests