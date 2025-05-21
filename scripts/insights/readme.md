# Scripts to get or bulk resolve insigts

requires the module installed (see main readme file)
```
pip install sumologiccse
```

## Authentication: accessid and accesskey
You can set these via environment variables such as:
```
export SUMO_ACCESS_ID='abdcefg'
export SUMO_ACCESS_KEY='ajkldfjaksflaskjflkasdlf'
```

or using arguments such as ```--accessid='asdfafdsa'```

## endpoints 
See: https://help.sumologic.com/docs/api/getting-started/#which-endpoint-should-i-should-use

For the origional prod/us1 instance use the long form api name
```
—-endpoint ‘https://api.sumologic.com/api/sec'
```

You can also use complete name e.g for fed:
```
--endpoint https://api.fed.sumologic.com/api/sec
```

For endpoints other than prod/us1 use the endpoint short form name such as:
```
--endpoint 'us2'
--endpoint 'au'
--endpoint 'in'
```

## What DSL should I use for -query?
You can determine the correct values for DSL by...
1. open CSIEM UI and go to insights page
2. do a search for one or more keywords or fields
3. note the -q query param in the browser. This is the 'dsl' value but it's url encoded
4. urldecode this string and since it uses double quotes you need to single quote that as the -q param. for example:
```
--query='-status:"closed"'
```

## Get Insights
```
python ./scripts/insights/get_insights.py --endpoint 'us2' --accessid "$SUMO_ACCESS_ID" --accesskey "$SUMO_ACCESS_KEY --query='-status:"closed"'"
```

## Bulk Resolve Insights Script
For bulk closing insights using various criteria.
This can be using the DSL (-query) or using client side filtering such as confidence score or a regex vs the json-ified payload.
The script will add a comment to each insight before changing it's status and resolution using the supplied params.

### Example 1: close all open insights but only a max of 5 use:
```
python resolve_insights.py --endpoint 'us2' --limit 5 --query='-status:"closed"'
```

### Example 2: close insights created over 70 days ago that are not closed.
For testing here limit 1 is set to only close one insight.
```
python3 resolve_insights.py --endpoint 'https://api.sumologic.com/api/sec' --daysold 70  --limit 1 --query='-status:"closed"' 
INFO:root:query: -status:"closed" created:<2023-05-23T22:03:43+00:00 found: 1 insights. dryrun: False
INFO:root:after confidence filter: 1
INFO:root:{"id": "0459d19d-766e-3c52-872d-51a93fe9fd69", "readableId": "INSIGHT-964", "confidence": "0.15", "created": "2023-05-23T21:03:45.356623", "status": "new"}
INFO:root:Closing: INSIGHT-964 with resolution: False Positive
```

### Example 3: a more complex dsl query with escaped " on windows
```
"C:\Program Files\Python310\python.exe" C:\Temp\resolve-insights.py --endpoint https://api.fed.sumologic.com/api/sec --accessid SUMO_ACCESS_ID --accesskey SUMO_ACCESS_KEY --daysold 0 --query="srcDevice_ip_asnOrg = \"Some Vendor\.\" -status:\"closed\"" --dryrun --status closed --resolution "Tuned" --comment "Some vendor tuned with ASN on matchlist. Closing with API"
```

### dryrun
The script has a safety feature a 'dyrun mode' add ```--dryrun``` flag to the commandline to print out rather than close insights.
In this mode the script will only display matching insights not update them.

### limit
The script will only close a max number of insights in limit (50 by default). increase with --limit

### resolution
The resolution value, defaults to "False Positive". Change with --resolution

### confidence
Note: this should now be supported via the DSL server side but didn't used to be hence in this client side script.
Allows for a client side filter on the confidence score if you want to only bulk close low confidence score insights and preseve high ones. By default this is set to 1 (all scores).
Set say:
```
--confidence=.5
```
to close only insights with <.5 confidence score.

### filterregex
A client side filter regular expresssion evaluated again a json dump of the insight recor. Will include ONLY json insight format that matches this expression.
This allows for quite advanced regular expression pattern selection criteria in the client side. It is evaluated vs the raw json string version of the insight.

### daysold
The minimum age for the insight. For example if set to 14 will filter to insights > 14 days old only.

### comment
You can add a comment to closed insights.