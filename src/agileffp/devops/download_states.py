
from agileffp.devops import config
from agileffp.devops.api import AzureDevOpsApi
from agileffp.devops.azure_wit_states import AzureWitStates


def main():
    api = AzureDevOpsApi(
        config.PAT,
        config.SERVER,
        config.ORGANIZATION,
        config.PROJECT,
        config.PROCESS_ID,
        config.WIT_TYPE_REF,
    )

    wit_states = AzureWitStates(api)

    states = wit_states.compute_states_from_query(config.QUERY_ID)

    states.to_csv("states.csv", index=False)


if __name__ == "__main__":
    main()
