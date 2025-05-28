import logging
import azure.functions as func
import os
import json
from azure.cosmos import CosmosClient, PartitionKey

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('logCommand function triggered.')

    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)

    conn_str = os.getenv("COSMOSDB_CONN_STRING")
    if not conn_str:
        return func.HttpResponse("Missing CosmosDB connection string", status_code=500)

    try:
        client = CosmosClient.from_connection_string(conn_str)
        database = client.get_database_client("OperatorStack")
        container = database.get_container_client("CommandLog")

        data["commandId"] = data.get("commandId", str(req.headers.get("x-request-id", "manual-command")))
        container.create_item(body=data)

        return func.HttpResponse("Command logged successfully", status_code=200)
    except Exception as e:
        logging.error(f"Error logging command: {e}")
        return func.HttpResponse("Error writing to CosmosDB", status_code=500)
