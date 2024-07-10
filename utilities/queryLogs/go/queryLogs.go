package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"text/tabwriter"
	"time"
)

type logRequest struct {
	Limit 	int 		`json:"limit"`
	Start 	int 		`json:"start"`
	End 	int 		`json:"end"`
	Sort	string		`json:"sort"`
	Filter	logFilter 	`json:"filter"`
}

type logFilter struct {
	Op 		string				`json:"op"`
	Match 	[]logFilterMatch 	`json:"match"`
}

type logFilterMatch struct {
	Key		string	`json:"key"`
	Op		string	`json:"op"` 
	Value	string	`json:"value"`
}

type logResponse struct {
	Count 	int 	`json:"count"`
	Start 	int 	`json:"start"`
	End 	int 	`json:"end"`
	Logs 	[]log 	`json:"logs"`
}

type log struct {
	Timestamp	int 				`json:"timestamp"`
	TraceID 	string				`json:"traceID"`
	SpanID 		string				`json:"spanID"`
	Message		string				`json:"message"`
	Severity 	string				`json:"severity"`
	Attributes	map[string]string 	`json:"attributes"`
}

type tokenResponse struct {
	AccessToken		string 		`json:"access_token"`
	GrantId			string		`json:"grant_id"`
	TokenType		string		`json:"token_type"`
	ExpiresIn		int			`json:"expires_in"`
}

func main() {
	
	hostnamePtr := flag.String("hostname", "", "The hostname of the tenant")
	clientIDPtr := flag.String("clientID", "", "API credentials - client ID")
	clientSecretPtr := flag.String("clientSecret", "", "API credentials - client secret")
	traceIDPtr := flag.String("traceID", "", "The trace ID to filter for")
	spanIDPtr := flag.String("spanID", "", "The span ID to filter for")
	severityPtr := flag.String("severity", "", "The severity level to filter for")
	filterPtr := flag.String("filter", "", "Other custom filters to filter for, in the following format - \"<key>=<value>&<key>=<value>\"")
	
	flag.Parse()

	var missingParam bool

	if *hostnamePtr == "" {
		fmt.Println("ERROR: The tenant hostname is required. Use the -hostname flag.")
		missingParam = true
	}

	if *clientIDPtr == "" {
		fmt.Println("ERROR: The client ID is required. Use the -clientID flag.")
		missingParam = true
	}

	if *clientSecretPtr == "" {
		fmt.Println("ERROR: The client secret is required. Use the -clientSecret flag.")
		missingParam = true
	}

	if missingParam {
		os.Exit(3)
	}

	//------------------------------- all required parameters present ----------------------------

	// Get access token
	tokenURL := "https://" + *hostnamePtr + "/oidc/endpoint/default/token"

	data := url.Values{}
    data.Set("grant_type", "client_credentials")
    data.Set("client_id", *clientIDPtr)
    data.Set("client_secret", *clientSecretPtr)

	tokenReq, _ := http.NewRequest(http.MethodPost, tokenURL, strings.NewReader(data.Encode()))

	tokenReq.Header.Add("Content-Type", "application/x-www-form-urlencoded")

	client := &http.Client{}
    resp, err := client.Do(tokenReq)

    var accessToken string
    if err != nil {
    	fmt.Printf("ERROR: Unable to get the access token: %v\n", err)
    } else {
    	if resp.StatusCode != http.StatusOK {
    		fmt.Printf("ERROR: Unable to get the access token - status code: %v\n", resp.Status)
    	} else {
    		body, err := ioutil.ReadAll(resp.Body)
    		resp.Body.Close()

    		if err != nil {
    			fmt.Printf("ERROR: Unable to get the access token: %v\n", err)
    		}

    		var tokenResp tokenResponse
    		err = json.Unmarshal(body, &tokenResp)

    		if err != nil {
    			fmt.Printf("ERROR: Unable to get the access token: %v\n", err)
    		} else {

    			accessToken = tokenResp.AccessToken
    		}
    	}

    }

    //fmt.Println("Access token: " + accessToken)

    if accessToken == "" {
    	fmt.Println("ERROR: Unable to get the access token")
    	os.Exit(3)
    }

    currTime := time.Now()
    endTime := currTime.UnixMilli()
    startTime := currTime.Add(-time.Minute * 30).UnixMilli() 

    lfilter, err := getFilter(*traceIDPtr, *spanIDPtr, *severityPtr, *filterPtr)
    	
    if err != nil {
    	fmt.Println(err.Error())
    	os.Exit(3)
    }

    logRequest := logRequest{
    	Limit: 500,
    	Start: int(startTime),
    	End: int(endTime),
    	Sort: "asc",
    	Filter: *lfilter,
    }

    w := tabwriter.NewWriter(os.Stdout, 10, 1, 2, ' ', tabwriter.Debug)
    
    isFirstLog := true
    
    for true {
    	//

    	//fmt.Printf("REQ: %v", logRequest)
    	logs, err := getLogs(client, *hostnamePtr, accessToken, logRequest)

    	if err != nil {
    		fmt.Println(err.Error())
    		continue
    	}
    	
    	if len(logs) > 0 {
    		printLogs(w, logs, isFirstLog)
    		isFirstLog = false
    		// new start time will be the timestamp of the last log
    		logRequest.Start = logs[len(logs) - 1].Timestamp + 1
    	}

    	time.Sleep(10 * time.Second) 

    	logRequest.End = int(time.Now().UnixMilli())
    }
	
}

func printLogs(w *tabwriter.Writer, logs []log, isFirstLog bool) {
	//w := tabwriter.NewWriter(os.Stdout, 10, 1, 2, ' ', tabwriter.Debug)

	if isFirstLog {
		fmt.Fprintln(w, "Timestamp\tTrace ID\tSpan ID\tMessage\tSeverity")
	}

	for _, v := range logs {
		fmt.Fprintf(w, "%s\t%s\t%s\t%s\t%s\n", strconv.Itoa(v.Timestamp), v.TraceID, v.SpanID, v.Message, v.Severity)
	}
    
    w.Flush()
}

func getLogs(client *http.Client, tenant string, accessToken string, logReq logRequest) ([]log, error) {

	var logs []log
	logUrl := "https://" + tenant + "/v1.0/logs/query"

	body, err := json.Marshal(logReq)
	if err != nil {
		return logs, errors.New("ERROR: unable to form request body")
	}

	r, _ := http.NewRequest(http.MethodPost, logUrl, bytes.NewBuffer(body))

	r.Header.Add("Content-Type", "application/json")
	r.Header.Add("Authorization", "Bearer " + accessToken)

	//client := &http.Client{}
    resp, err := client.Do(r)

    if err != nil {
    	message := fmt.Sprintf("ERROR: Unable to get the logs: %v\n", err)
    	return logs, errors.New(message)
    } else {
    	if resp.StatusCode != http.StatusOK {
    		message := fmt.Sprintf("ERROR: Unable to get the logs - status code: %v\n", resp.Status)
    		return logs, errors.New(message)
    	} else {
    		body, err := ioutil.ReadAll(resp.Body)
    		resp.Body.Close()

    		if err != nil {
    			message := fmt.Sprintf("ERROR: Unable to get the logs: %v\n", err)
    			return logs, errors.New(message)
    		}

    		var logResp logResponse
    		err = json.Unmarshal(body, &logResp)

    		if err != nil {
    			message := fmt.Sprintf("ERROR: Unable to get the logs: %v\n", err)
    			return logs, errors.New(message)
    		} else {

    			logs = logResp.Logs
    		}
    	}
    }

    return logs, nil
}



func getFilter(traceID, spanID, severity, filterStr string) (*logFilter, error) {

	var matches []logFilterMatch

	if traceID != "" {
		m := logFilterMatch{"traceID", "eq", traceID}
		matches = append(matches, m)
	}

	if spanID != "" {
		m := logFilterMatch{"spanID", "eq", spanID}
		matches = append(matches, m)
	}

	if severity != "" {
		m := logFilterMatch{"severity", "eq", severity}
		matches = append(matches, m)
	}

	if filterStr != "" {

		filters := strings.Split(filterStr, "&")

		if len(filters) > 0 {

			for _, f := range filters {

				kv := strings.Split(f, "=")

				if len(kv) != 2 {
					return nil, errors.New("ERROR: Custom filter string is invalid.")
				}

				m := logFilterMatch{kv[0], "eq", kv[1]}
				matches = append(matches, m)

			}
		}
	}

	return &logFilter{Op: "AND", Match: matches,}, nil
}

func isEqualLogs(log1, log2 log) bool {

	if log1.Timestamp != log2.Timestamp {
		return false
	}

	if log1.TraceID != log2.TraceID {
		return false
	}

	if log1.SpanID != log2.SpanID {
		return false
	}

	if log1.Severity != log2.Severity {
		return false
	}

	if log1.Message != log2.Message {
		return false
	}

	return true
}