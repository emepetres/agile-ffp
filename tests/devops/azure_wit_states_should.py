import pytest
from dateutil import parser

from agileffp.devops.azure_wit_states import get_wit_state_updates, parse_state_update


@pytest.fixture
def empty_query_result():
    return {
        "queryType": "flat",
        "queryResultType": "workItem",
        "asOf": "2021-03-01T09:00:00Z",
        "columns": [
            {
                "name": "Id",
                "referenceName": "System.Id",
                "url": "https://dev.azure.com/organization/project/_apis/wit/fields/System.Id",
            },
            {
                "name": "Title",
                "referenceName": "System.Title",
                "url": "https://dev.azure.com/organization/project/_apis/wit/fields/System.Title",
            },
            {
                "name": "State",
                "referenceName": "System.State",
                "url": "https://dev.azure.com/organization/project/_apis/wit/fields/System.State",
            },
            {
                "name": "Work Item Type",
                "referenceName": "System.WorkItemType",
                "url": "https://dev.azure.com/organization/project/_apis/wit/fields/System.WorkItemType",
            },
        ],
        "workItems": [],
    }


@pytest.fixture
def query_result(empty_query_result):
    empty_query_result["workItems"] = [
        {
            "id": "123456",
            "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123456",
        },
        {
            "id": "123457",
            "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123457",
        },
        {
            "id": "123458",
            "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123458",
        },
        {
            "id": "123459",
            "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123459",
        },
        {
            "id": "123460",
            "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123460",
        },
        {
            "id": "123461",
            "url": "https://dev.azure.com/organization/project/_apis/wit/workItems/123461",
        },
    ]
    return empty_query_result


@pytest.fixture
def update():
    return {
        "id": 1,
        "workItemId": 168975,
        "rev": 1,
        "revisedBy": {
            "id": "87270860-c2d5-4d53-a77a-8a15e1fb4680",
            "name": "Antonio Ávila Membrives <aavila@plainconcepts.com>",
            "displayName": "Antonio Ávila Membrives",
            "url": "https://spsprodeus24.vssps.visualstudio.com/A03fda1b0-beae-4349-a672-45e912480c5d/_apis/Identities/87270860-c2d5-4d53-a77a-8a15e1fb4680",
            "_links": {
                "avatar": {
                    "href": "https://dev.azure.com/plainconcepts/_apis/GraphProfile/MemberAvatars/aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx"
                }
            },
            "uniqueName": "aavila@plainconcepts.com",
            "imageUrl": "https://dev.azure.com/plainconcepts/_apis/GraphProfile/MemberAvatars/aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx",
            "descriptor": "aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx",
        },
        "revisedDate": "2023-06-13T11:57:06.947Z",
        "fields": {
            "System.Id": {"newValue": 168975},
            "System.AreaId": {"newValue": 141633},
            "System.NodeName": {"newValue": "SecretAligner.CirugiasGuiadas"},
            "System.AreaLevel1": {"newValue": "SecretAligner.CirugiasGuiadas"},
            "System.Rev": {"newValue": 1},
            "System.AuthorizedDate": {"newValue": "2023-06-13T11:54:07.583Z"},
            "System.RevisedDate": {"newValue": "2023-06-13T11:57:06.947Z"},
            "System.IterationId": {"newValue": 142694},
            "System.IterationLevel1": {"newValue": "SecretAligner.CirugiasGuiadas"},
            "System.IterationLevel2": {"newValue": "Evergine"},
            "System.IterationLevel3": {"newValue": "Sprint 12"},
            "System.WorkItemType": {"newValue": "Product Backlog Item"},
            "System.State": {"newValue": "New"},
            "System.Reason": {"newValue": "New backlog item"},
            "System.AssignedTo": {},
            "System.CreatedDate": {"newValue": "2023-06-13T11:54:07.583Z"},
            "System.CreatedBy": {
                "newValue": {
                    "displayName": "Antonio Ávila Membrives",
                    "url": "https://spsprodeus24.vssps.visualstudio.com/A03fda1b0-beae-4349-a672-45e912480c5d/_apis/Identities/87270860-c2d5-4d53-a77a-8a15e1fb4680",
                    "_links": {
                        "avatar": {
                            "href": "https://dev.azure.com/plainconcepts/_apis/GraphProfile/MemberAvatars/aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx"
                        }
                    },
                    "id": "87270860-c2d5-4d53-a77a-8a15e1fb4680",
                    "uniqueName": "aavila@plainconcepts.com",
                    "imageUrl": "https://dev.azure.com/plainconcepts/_apis/GraphProfile/MemberAvatars/aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx",
                    "descriptor": "aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx",
                }
            },
            "System.ChangedDate": {"newValue": "2023-06-13T11:54:07.583Z"},
            "System.ChangedBy": {
                "newValue": {
                    "displayName": "Antonio Ávila Membrives",
                    "url": "https://spsprodeus24.vssps.visualstudio.com/A03fda1b0-beae-4349-a672-45e912480c5d/_apis/Identities/87270860-c2d5-4d53-a77a-8a15e1fb4680",
                    "_links": {
                        "avatar": {
                            "href": "https://dev.azure.com/plainconcepts/_apis/GraphProfile/MemberAvatars/aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx"
                        }
                    },
                    "id": "87270860-c2d5-4d53-a77a-8a15e1fb4680",
                    "uniqueName": "aavila@plainconcepts.com",
                    "imageUrl": "https://dev.azure.com/plainconcepts/_apis/GraphProfile/MemberAvatars/aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx",
                    "descriptor": "aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx",
                }
            },
            "System.AuthorizedAs": {
                "newValue": {
                    "displayName": "Antonio Ávila Membrives",
                    "url": "https://spsprodeus24.vssps.visualstudio.com/A03fda1b0-beae-4349-a672-45e912480c5d/_apis/Identities/87270860-c2d5-4d53-a77a-8a15e1fb4680",
                    "_links": {
                        "avatar": {
                            "href": "https://dev.azure.com/plainconcepts/_apis/GraphProfile/MemberAvatars/aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx"
                        }
                    },
                    "id": "87270860-c2d5-4d53-a77a-8a15e1fb4680",
                    "uniqueName": "aavila@plainconcepts.com",
                    "imageUrl": "https://dev.azure.com/plainconcepts/_apis/GraphProfile/MemberAvatars/aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx",
                    "descriptor": "aad.Njc0MThlZTMtZWY3MS03NDA5LTk2MzctNWQ1YjlkNTRiN2Mx",
                }
            },
            "System.PersonId": {"newValue": 21257114},
            "System.Watermark": {"newValue": 1011294},
            "System.IsDeleted": {"newValue": False},
            "System.CommentCount": {"newValue": 1},
            "System.TeamProject": {"newValue": "SecretAligner.CirugiasGuiadas"},
            "System.AreaPath": {"newValue": "SecretAligner.CirugiasGuiadas"},
            "System.IterationPath": {
                "newValue": "SecretAligner.CirugiasGuiadas\\Evergine\\Sprint 12"
            },
            "System.BoardColumnDone": {"newValue": False},
            "Microsoft.VSTS.Common.Priority": {"newValue": 2},
            "Microsoft.VSTS.Common.ValueArea": {"newValue": "Business"},
            "WEF_074AE9F3108D4C65993E6BEEA1D86824_System.ExtensionMarker": {
                "newValue": True
            },
            "WEF_074AE9F3108D4C65993E6BEEA1D86824_Kanban.Column.Done": {
                "newValue": False
            },
            "WEF_F10BD31DDF194FA7B15351E3F028EBD9_Kanban.Column.Done": {
                "newValue": False
            },
            "WEF_22C2BBA295614D779A28B8CD0DA94944_Kanban.Column": {"newValue": "New"},
            "WEF_22C2BBA295614D779A28B8CD0DA94944_Kanban.Column.Done": {
                "newValue": False
            },
            "WEF_D96794364361494ABA00132745C4DEB4_Kanban.Column": {"newValue": "New"},
            "WEF_D96794364361494ABA00132745C4DEB4_Kanban.Column.Done": {
                "newValue": False
            },
            "WEF_27D37A568BC84A79804B57CD0E4B83D1_Kanban.Column": {"newValue": "New"},
            "WEF_27D37A568BC84A79804B57CD0E4B83D1_Kanban.Column.Done": {
                "newValue": False
            },
            "System.History": {
                "newValue": 'Copied from <a href="x-mvwit:workitem/168889">Product Backlog Item 168889</a>'
            },
            "System.BoardColumn": {"newValue": "New"},
            "Microsoft.VSTS.Common.StateChangeDate": {
                "newValue": "2023-06-13T11:54:07.583Z"
            },
            "WEF_074AE9F3108D4C65993E6BEEA1D86824_Kanban.Column": {"newValue": "New"},
            "WEF_F10BD31DDF194FA7B15351E3F028EBD9_Kanban.Column": {"newValue": "New"},
            "System.Title": {
                "newValue": "[3D] Mejora Visual de arcadas: Postprocessing"
            },
            "System.Description": {"newValue": "TODO"},
            "Microsoft.VSTS.Common.BacklogPriority": {"newValue": 999685268.0},
            "WEF_D96794364361494ABA00132745C4DEB4_System.ExtensionMarker": {
                "newValue": True
            },
            "WEF_27D37A568BC84A79804B57CD0E4B83D1_System.ExtensionMarker": {
                "newValue": True
            },
            "WEF_F10BD31DDF194FA7B15351E3F028EBD9_System.ExtensionMarker": {
                "newValue": True
            },
            "WEF_22C2BBA295614D779A28B8CD0DA94944_System.ExtensionMarker": {
                "newValue": True
            },
            "System.Tags": {"newValue": "[Visor]; ToRefineEstimation"},
            "System.Parent": {"newValue": 165687},
        },
        "relations": {
            "added": [
                {
                    "rel": "System.LinkTypes.Related",
                    "url": "https://dev.azure.com/plainconcepts/4b5209c5-0a90-4a6e-acef-1eaa20630758/_apis/wit/workItems/168889",
                    "attributes": {"isLocked": False, "name": "Related"},
                },
                {
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": "https://dev.azure.com/plainconcepts/4b5209c5-0a90-4a6e-acef-1eaa20630758/_apis/wit/workItems/165687",
                    "attributes": {"isLocked": False, "name": "Parent"},
                },
            ]
        },
        "url": "https://dev.azure.com/plainconcepts/4b5209c5-0a90-4a6e-acef-1eaa20630758/_apis/wit/workItems/168975/updates/1",
    }


@pytest.fixture
def updates(update):
    return {
        "count": 1,
        "value": [update],
    }


def assert_parse_state_update(update):
    log = parse_state_update(update)
    assert len(log) == 3
    assert log == [168975, parser.parse("2023-06-13T11:57:06.947Z"), "New"]


@pytest.fixture
def wit_state_updates_mock(updates):
    def mock(pat: str, server: str, org: str, project: str, wit_id: str) -> dict:
        return updates

    return mock


def assert_states_table_colums(empty_query_result, wit_state_updates_mock):
    df = get_wit_state_updates(empty_query_result, wit_state_updates_mock)
    columns = df.columns.tolist()
    assert len(columns) == 3
    assert columns == ["id", "date", "state"]


def assert_states_are_parsed(query_result, wit_state_updates_mock):
    df = get_wit_state_updates(query_result, wit_state_updates_mock)
    assert len(df) == 6
