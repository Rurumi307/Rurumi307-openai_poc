import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient 
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    ComplexField,
    CorsOptions,
    SearchIndex,
    ScoringProfile,
    SearchFieldDataType,
    SimpleField,
    SearchableField
)

from dotenv import load_dotenv
import os 
from datetime import datetime
load_dotenv(override=True)

service_name = "openaipoc-cogsearch"
SEARCH_SERVICE_ADMIN_API_KEY = os.environ.get("SEARCH_SERVICE_ADMIN_API_KEY")
index_name = os.environ.get("SEARCH_INDEX_NAME")

# Create an SDK client
endpoint = "https://{}.search.windows.net/".format(service_name)
admin_client = SearchIndexClient(endpoint=endpoint,
                      index_name=index_name,
                      credential=AzureKeyCredential(SEARCH_SERVICE_ADMIN_API_KEY))

search_client = SearchClient(endpoint=endpoint,
                      index_name=index_name,
                      credential=AzureKeyCredential(SEARCH_SERVICE_ADMIN_API_KEY))

search_suggestion = input()
results = search_client.search(search_text=search_suggestion, include_total_count=True, logging_enable=True)

print("Autocomplete for:", search_suggestion)
for result in results:
    print (result['content'])
# print(results[0])