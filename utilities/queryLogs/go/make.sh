GOOS=linux GOARCH=amd64 go build  -o bin/linux/queryLogs queryLogs.go
GOOS=darwin GOARCH=amd64 go build -o bin/darwin/queryLogs queryLogs.go
GOOS=windows GOARCH=amd64 go build -o bin/windows/queryLogs.exe queryLogs.go