# IBM Security Verify Privacy Utility for Viewing Trace Logs

Go program that retrieves trace logs on IBM Security Verify.

---

## Prerequisites

* Create an API client
 - An API client is necessary to get the accesses for viewing trace logs. The following document [Create an API client](https://docs.verify.ibm.com/verify/docs/create-api-client) describes
how to create an API client with the appropriate accesses.  The set of accesses that you need for viewing trace logs is readTraceLogs.


## Building the utility

Use [go](https://golang.org/doc/install) to build the utility:

```bash
$ go build  -o <output location> queryLogs.go
```
Alternatively, The bin directory contains statically linked binaries for [Linux](bin/linux/queryLogs) and [Mac](bin/darwin/queryLogs).

These don't require any runtime and should just run on the corresponding OS.

If go is installed you can build all three binaries on Linux using the make.sh script.

## Features

- Retrieve trace logs generated in ISV 

## Documentation

* [Trace logging in multi-line rule documentation](https://www.ibm.com/docs/en/security-verify?topic=attributes-multi-line-rule-executor#r_multiline_rule__title__8)


## Using the utility

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

The queryLogs utility accepts 7 commands:

* clientID 
 -  The client ID created in the previous step with the right access
* clientSecret 
 - The corresponding client secret
* filter 
 - The custom filter to filter logs, in the format `<key>=<value>` and delimited by `&` and enclosed in double quotes
* hostname 
 - The hostname of the tenant 
* severity 
 - The severity to filter logs  
* spanID 
 - The span ID to filter logs
* traceID 
 - The trace ID to filter logs

The program will initially retrieve all logs that match the filters from the last 15 minutes, then subsequently retrieve newer logs that match the filters as they are generated and available.