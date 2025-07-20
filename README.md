# sumologic-cse-python-sdk
An api client similar to the official Sumologic python API client but for the CSE api: https://api.sumologic.com/docs/sec/#

This project only intends to cover off and provide useful scripts to solve some common use cases rather than create an entire comprehensive API client.


# install package
```
pip install sumologiccse
```

# Getting Started
see the scripts section for examples. In general either set env vars:
- SUMO_ACCESS_ID
- SUMO_ACCESS_KEY
or you must privide as arguments.

## endpoints 
See: https://help.sumologic.com/docs/api/getting-started/#which-endpoint-should-i-should-use

The defeault endpoint is: https://api.sumologic.com/docs/sec
Using --endpoint 'prod' or 'us1' will also resolve to this value.

For endpoints other than prod/us1 use the endpoint short form name such as:
```
--endpoint 'us2'
--endpoint 'au'
--endpoint 'in'
```

## connection
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
You can find these in ./scripts for example:
- [Insights scripts readme](scripts/insights/readme.md)


# Docker

Build the dockerfile, you can then run build version of module for testing or build with package included by uncommenting the pypi package install

```
docker build -t sumocse-test .
```

Run and set relevant env vars e.g 
```
docker run -it -e SUMO_ACCESS_ID="$SUMO_ACCESS_ID_DEMO" -e SUMO_ACCESS_KEY="$SUMO_ACCESS_KEY_DEMO" -e SUMO_ACCESS_ID_DEMO="$SUMO_ACCESS_ID_DEMO" -e SUMO_ACCESS_KEY_DEMO="$SUMO_ACCESS_KEY_DEMO" sumocse-test bash
```

# TODOs
- Add a decent selection of endpoints
- Write some more unit and integration tests