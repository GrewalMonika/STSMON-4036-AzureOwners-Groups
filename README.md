The python script interacts with both the Microsoft Graph API and Splunk to fetch information from Azure AD and send it to Splunk for monitoring and analysis. 
Here's a breakdown of how this process works and how you can ensure that your runbook runs successfully in your GitHub repository.
Key Steps:
Python Script (PythonscriptforAzureAD.py):

The group Id’s of the security group is stored in a variable inside the script. 

The group is then used to fetch group names, members, and owners of security groups from Azure Active Directory using the Microsoft Graph API.

Prepares the data in a format suitable for Splunk (e.g., JSON).

Sends the payload to Splunk's HTTP Event Collector (HEC) endpoint for ingestion.

Microsoft Graph API Authentication:

The Python script needs to authenticate with the Microsoft Graph API by obtaining an OAuth 2.0 token to make requests.

Typically, this is done by registering an Azure AD application and then requesting a token using client credentials (client ID, client secret, and tenant ID).

Fetching Data from Azure AD:

The script makes requests to Microsoft Graph API endpoints to fetch group details, such as:

Group names

Members

Owners

Sample API endpoint for group details might look like:
https://graph.microsoft.com/v1.0/groups/{group-id}/members

Formatting Payload for Splunk:

Once the data is fetched, the script should format it as a JSON payload.

Sending the Data to Splunk:

The Python script uses the Splunk HEC endpoint to send the payload via a POST request.

Index: azure_group_membership

Source type:

azure:assets:azgroup:members for group members data.

azure:assets:azgroup:owners for group owner's data.

We have dynamically set the source type based on whether the data pertains to members or owners.
