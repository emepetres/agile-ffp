from agileffp.devops import config
from agileffp.devops.azure_query_results import get_work_items_from_query

data = get_work_items_from_query(
    config.PAT, config.SERVER, config.ORGANIZATION, config.PROJECT, config.QUERY_ID
)
print(data)
