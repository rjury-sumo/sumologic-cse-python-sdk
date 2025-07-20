# CHANGELOG for sumologic-python-sdk
This project adheres to [Semantic Versioning](http://semver.org/). The CHANGELOG follows the format listed at [Keep A Changelog](http://keepachangelog.com/)

## [0.0.6]
Added rules API endpoints: get_rules(), get_rule(), and query_rules() methods.
Added integration tests for rules API endpoints.
Added example script get_rules.py.

## [0.0.5]
Fixed the mess around endpoint. Default, 'prod' or 'us1' all resolve to https://api.sumologic.com/docs/sec.

## [0.0.4]
Fixed a typo where a line of code had been removed accidentally in a prior commit.

## [0.0.3]
Updated dependencies to fix confict so package will build again.