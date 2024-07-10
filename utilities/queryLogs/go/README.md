# IBM Security Performance

## Verify - Identity and Access Management

### Verify example - Retrieving trace logs

This directory contains Golang example code for retrieving trace logs using the Verify APIs. The queryLogs program retrieves the trace logs based on the filter specified.

### Table of Contents

* [Create an API client](#create-an-api-client)
* [Usage of the example](#usage-of-the-example)
* [Building the example](#building-the-example)


### Create an API client

An API client is necessary to get the accesses for viewing trace logs. The following document [Create an API client](https://docs.verify.ibm.com/verify/docs/create-api-client) describes
how to create an API client with the appropriate accesses.  The set of accesses that you need for viewing trace logs is readTraceLogs.


### Usage of the example
```
Usage of ./queryLogs:
  -clientID string
    	API credentials - client ID
  -clientSecret string
    	API credentials - client secret
  -filter string
    	Other custom filters to filter for, in the following format - "<key>=<value>&<key>=<value>"
  -hostname string
    	The hostname of the tenant
  -severity string
    	The severity level to filter for
  -spanID string
    	The span ID to filter for
  -traceID string
    	The trace ID to filter for
```

The queryLogs program accepts 7 commands:

- clientID - The client ID created in the previous step with the right access
- clientSecret - The corresponding client secret
- filter - The custom filter to filter logs, in the format `<key>=<value>` and delimited by `&` and enclosed in double quotes
- hostname - The hostname of the tenant 
- severity - The severity to filter logs	
- spanID - The span ID to filter logs
- traceID - The trace ID to filter logs

The program will initially retrieve all logs that match the filters from the last 15 minutes, then subsequently retrieve newer logs that match the filters as they are generated and available.


### Building the example

The bin directory contains statically linked binaries for [Linux](bin/linux/queryLogs) and [Mac](bin/darwin/queryLogs).

These don't require any runtime and should just run on the corresponding OS.

If go is installed you can build all three binaries on Linux using the make.sh script.
Mac and Windows developers should be able to create a similar script.
Note that you will need the [go install from golang.org](https://golang.org/doc/install) in order to be sure of creating static binaries. The gccgo package that RedHat provides creates dynamically linked binaries that require a go runtime to be installed before they will run.