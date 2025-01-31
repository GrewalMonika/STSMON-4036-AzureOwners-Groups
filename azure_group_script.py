import requests
from azure.identity import ClientSecretCredential
import json

# Azure App Registration details
tenant_id = 'a33c6ac4-a52e-45c5-af07-b972df9bd004'
client_id = '8a8178c4-dc8a-4576-b60b-bf2e4ad3f9fe'
client_secret = 'CDe8Q~WNOnsbuFL2g3ME.NlXJFRLivnAjNoY0c3b'

# List of Group IDs for the specific groups
group_ids = [
    'e71ca2e6-ce8c-4099-8c93-2612fc6eb4e4',
    '61a68bfc-880a-4b7c-9d43-d9fbfc77daf6',
    '854826eb-8793-4307-bb63-b16590a0d034',
    '7a2a6c7c-433d-4d61-880e-9a3dfe1ec27d',
    '58f3e906-e90d-4ad2-ab43-6d97c9d54d90',
    '3d25ecfd-cb72-4b8f-899c-aada4b611281',
    'd5aa0cf2-17ee-4753-8059-c359449a8c28',
    'c9ea5aba-7e89-49c0-947c-fac435890721',
    '58bceac8-6e1d-4348-b560-744f9d5ff46f',
    '4f94ceb9-f21a-4440-a1b5-c70d1fc86993',
    '47ac7264-4918-4ff4-a35c-fa86e459f280',
    'a42c1d93-d395-4779-a8c9-22406cfdebbd',
    '70dc4d59-26bd-4394-81e1-e8557e05ac92',
    'd4e6a1c7-0f94-4e69-9e65-d99e25347fe9'
]

# Splunk HEC details
splunk_url = "https://http-inputs-interikea.splunkcloud.com"
hec_token = "77B44C9E-B3D4-4052-9CDA-0990D7B20227"

# Authenticate and get the access token using Client Credentials flow
credentials = ClientSecretCredential(tenant_id, client_id, client_secret)

# Get the access token
token = credentials.get_token('https://graph.microsoft.com/.default').token

# Set the headers for the request to Microsoft Graph API
headers = {
    'Authorization': f'Bearer {token}',
    'ConsistencyLevel': 'eventual'  # Optional: For eventual consistency if needed
}

# Loop over each group_id
for group_id in group_ids:
    # Microsoft Graph API endpoint to get group members with count
    url_members = f"https://graph.microsoft.com/v1.0/groups/{group_id}/members?$count=true"
    url_owners = f"https://graph.microsoft.com/v1.0/groups/{group_id}/owners"
    url_group = f"https://graph.microsoft.com/v1.0/groups/{group_id}"

    # Make the GET request to the Graph API for members and owners
    response_members = requests.get(url_members, headers=headers)
    response_owners = requests.get(url_owners, headers=headers)

    # Check if the request was successful (status code 200) for members and owners
    if response_members.status_code == 200 and response_owners.status_code == 200:
        data_members = response_members.json()
        data_owners = response_owners.json()

        # Extract member details and send to Splunk individually
        for member in data_members['value']:
            member_info = {
                "Name": member['displayName'],
                "email": member.get('mail', 'No email')
            }

            # Fetch the group name
            response_group = requests.get(url_group, headers=headers)
            if response_group.status_code == 200:
                group_data = response_group.json()
                group_name = group_data.get('displayName', 'No name')
                member_info["group_name"] = group_name

                # Prepare the event data for member
                member_event_data = {
                    "event": member_info,
                    "sourcetype": "Azure_members",  # Sourcetype for member
                    "index": "test",
                    "host": "azure_graph_api",
                    "source": "azure_graph_api"
                }

                # Print event data for debugging
                print(f"Sending the following event data for member {member_info['Name']} to Splunk:")
                print(json.dumps(member_event_data, indent=2))

                # Send data to Splunk via HEC (members)
                headers_splunk = {
                    "Authorization": f"Splunk {hec_token}",
                    "Content-Type": "application/json"
                }

                # Send the individual member event data to Splunk
                splunk_response_member = requests.post(f"{splunk_url}/services/collector/event", headers=headers_splunk, data=json.dumps(member_event_data), verify=True)

                if splunk_response_member.status_code == 200:
                    print(f"Event for member {member_info['Name']} successfully sent to Splunk.")
                else:
                    print(f"Failed to send event for member {member_info['Name']} to Splunk. Status code: {splunk_response_member.status_code}")
                    print("Response:", splunk_response_member.text)
            else:
                print(f"Failed to fetch group details for group {group_id}. Status code: {response_group.status_code}")
                print(response_group.text)

        # Extract owner details and send to Splunk individually
        for owner in data_owners['value']:
            owner_info = {
                "Name": owner['displayName'],
                "email": owner.get('mail', 'No email')
            }

            # Fetch the group name
            response_group = requests.get(url_group, headers=headers)
            if response_group.status_code == 200:
                group_data = response_group.json()
                group_name = group_data.get('displayName', 'No name')
                owner_info["group_name"] = group_name

                # Prepare the event data for owner
                owner_event_data = {
                    "event": owner_info,
                    "sourcetype": "Azure_owners",  # Sourcetype for owner
                    "index": "test",
                    "host": "azure_graph_api",
                    "source": "azure_graph_api"
                }

                # Print event data for debugging
                print(f"Sending the following event data for owner {owner_info['Name']} to Splunk:")
                print(json.dumps(owner_event_data, indent=2))

                # Send data to Splunk via HEC (owners)
                splunk_response_owner = requests.post(f"{splunk_url}/services/collector/event", headers=headers_splunk, data=json.dumps(owner_event_data), verify=True)

                if splunk_response_owner.status_code == 200:
                    print(f"Event for owner {owner_info['Name']} successfully sent to Splunk.")
                else:
                    print(f"Failed to send event for owner {owner_info['Name']} to Splunk. Status code: {splunk_response_owner.status_code}")
                    print("Response:", splunk_response_owner.text)
            else:
                print(f"Failed to fetch group details for group {group_id}. Status code: {response_group.status_code}")
                print(response_group.text)

    else:
        print(f"Error fetching group members or owners for group {group_id}. Status codes: {response_members.status_code}, {response_owners.status_code}")
        print("Member Response:", response_members.text)
        print("Owner Response:", response_owners.text)
