# boto3-paginated-api-call-example

This is an example script that demonstrates making paginated Describe API calls with the boto3 SDK. 

## Execution

1. Update the script with a Spot Fleet Request ID.
2. Execute the Script `python3 example.py`

The script will describe all instances in the Spot Fleet Request and retrieved their Spot Fleet Request IDs. Then it will make a paginated call to describe the retrieved Spot Fleet Request IDs.