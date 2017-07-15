# Vulnerable Slack Bot example created for Black Hat USA 2017

## Contributors

Andrew Krug @andrewkrug

## Deployment

	sls deploy

### Invocation

	curl <host>/posts
	curl <host>/posts/5

# Tips & Tricks

### `help` command
Just use it on anything:

	sls  help
or

	sls <command> --help

### `deploy function` command
Deploy only one function:

	sls deploy function -f <function-name>

### `logs` command
Tail the logs of a function:

	sls logs -f <function-name> -t

### `info` command
Information about the service (stage, region, endpoints, functions):

	sls info

### `invoke` command
Run a specific function with a provided input and get the logs

	sls invoke -f <function-name> -p event.json -l