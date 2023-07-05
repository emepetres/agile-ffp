from azure.devops.connection import Connection
from azure.devops.v7_0.work import TeamContext
from msrest.authentication import BasicAuthentication
import pprint
from config import PAT, ORG_URL

# Fill in with your personal access token and org URL
personal_access_token = PAT
organization_url = ORG_URL

# Create a connection to the org
credentials = BasicAuthentication("", personal_access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Get a client (the "core" client provides access to projects, teams, etc)
core_client = connection.clients.get_core_client()

# Get the first page of projects
get_projects_response = core_client.get_projects()
index = 0
while get_projects_response is not None:
    for project in get_projects_response:
        pprint.pprint("[" + str(index) + "] " + project.name)
        index += 1
    # # if (
    # #     get_projects_response.continuation_token is not None
    # #     and get_projects_response.continuation_token != ""
    # # ):
    # #     # Get the next page of projects
    # #     get_projects_response = core_client.get_projects(
    # #         continuation_token=get_projects_response.continuation_token
    # #     )
    # # else:
    # All projects have been retrieved
    get_projects_response = None

# # tc = TeamContext("SecretAligner.CirugiasGuiadas", "SaaS Team")
# # index = 0
# # work_client = connection.clients.get_work_client()
# # get_backlog_response = work_client.get_backlog(tc, "backlog")
# # for item in get_backlog_response:
# #     pprint.pprint("[" + str(index) + "] " + item.name)
# #     index += 1
