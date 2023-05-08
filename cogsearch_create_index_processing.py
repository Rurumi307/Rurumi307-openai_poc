import os
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    ComplexField,
    CorsOptions,
    SearchIndex,
    ScoringProfile,
    SearchFieldDataType,
    SimpleField,
    SearchableField
)

# Get the service endpoint and API key from the environment
service_name = "openaipoc-cogsearch"
endpoint = "https://{}.search.windows.net/".format(service_name)
key = os.environ.get("SEARCH_SERVICE_ADMIN_API_KEY")

# Create a service client
client = SearchIndexClient(endpoint, AzureKeyCredential(key))

# Create the index
name = "Attach"
fields=[
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
    SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
    SimpleField(name="sourcepage", type=SearchFieldDataType.String, filterable=True, facetable=True),
    SimpleField(name="sourcefile", type=SearchFieldDataType.String, filterable=True, facetable=True)
]
cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
scoring_profiles = []

index = SearchIndex(
    name=name,
    fields=fields,
    scoring_profiles=scoring_profiles,
    cors_options=cors_options)

result = client.create_index(index)