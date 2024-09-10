import requests
import re
import json
import tldextract


# Parameters
cookie = ""  # Replace this with the actual cookie
csrf_token = ""  # Replace this with the actual CSRF token

# Define the URL
url = "https://hackerone.com/graphql"


# Define the headers
headers = {
    "Host": "hackerone.com",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://hackerone.com/opportunities/my_programs?ordering=Last+invitation+accepted",
    "Content-Type": "application/json",
    "X-Csrf-Token": csrf_token,
    "X-Product-Area": "opportunity_discovery",
    "X-Product-Feature": "my_programs",
    "Origin": "https://hackerone.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Pwnfox-Color": "blue",
    "Priority": "u=0",
    "Te": "trailers",
    "Cookie": cookie
}


# Function to get data with different 'from' values
def fetch_data(cookie, csrf_token, from_value):
    # Define the GraphQL query payload
    payload = {
        "operationName": "DiscoveryQuery",
        "variables": {
            "size": 100,
            "from": from_value,
            "query": {},
            "filter": {
                "bool": {
                    "filter": [
                        {
                            "bool": {
                                "must_not": {
                                    "term": {
                                        "team_type": "Engagements::Assessment"
                                    }
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "field": "last_invitation_accepted_at",
                    "direction": "DESC"
                }
            ],
            "post_filters": {
                "my_programs": True,
                "bookmarked": False,
                "campaign_teams": False
            },
            "product_area": "opportunity_discovery",
            "product_feature": "my_programs"
        },
        "query": """
        query DiscoveryQuery($query: OpportunitiesQuery!, $filter: QueryInput!, $from: Int, $size: Int, $sort: [SortInput!], $post_filters: OpportunitiesFilterInput) {
          me {
            id
            ...OpportunityListMe
            __typename
          }
          opportunities_search(
            query: $query
            filter: $filter
            from: $from
            size: $size
            sort: $sort
            post_filters: $post_filters
          ) {
            nodes {
              ... on OpportunityDocument {
                id
                handle
                __typename
              }
              ...OpportunityList
              __typename
            }
            total_count
            __typename
          }
        }

        fragment OpportunityListMe on User {
          id
          ...OpportunityCardMe
          __typename
        }

        fragment OpportunityCardMe on User {
          id
          ...BookmarkMe
          __typename
        }

        fragment BookmarkMe on User {
          id
          __typename
        }

        fragment OpportunityList on OpportunityDocument {
          id
          ...OpportunityCard
          __typename
        }

        fragment OpportunityCard on OpportunityDocument {
          id
          team_id
          name
          handle
          triage_active
          publicly_visible_retesting
          allows_private_disclosure
          allows_bounty_splitting
          launched_at
          state
          offers_bounties
          last_updated_at
          currency
          team_type
          minimum_bounty_table_value
          maximum_bounty_table_value
          cached_response_efficiency_percentage
          first_response_time
          structured_scope_stats
          show_response_efficiency_indicator
          submission_state
          resolved_report_count
          campaign {
            id
            campaign_type
            start_date
            end_date
            critical
            target_audience
            __typename
          }
          gold_standard
          awarded_report_count
          awarded_reporter_count
          h1_clear
          idv
          __typename
        }
        """
    }

    # Send the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Extract and print all 'handle' fields
        opportunities = data['data']['opportunities_search']['nodes']
        handles = [opportunity['handle'] for opportunity in opportunities if 'handle' in opportunity]
        
        return handles
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return []


# Initialize an empty list to collect all handles
all_handles = []

# Loop through different 'from' values
for from_value in range(0, 1000, 100):  # Adjust the range as needed
    # print(f"Fetching data with 'from' value: {from_value}")
    handles = fetch_data(cookie, csrf_token, from_value)
    
    if not handles:  # This will be True if handles is an empty list
        # print("No handles found. Breaking the loop.")
        break
    
    # Append the handles found to the all_handles list
    all_handles.extend(handles)
    
    # print("Handles found:", handles)

# Print all collected handles
# print("All handles collected:", all_handles)


# ---------------------------------

# for handle in all_handles

for handle in all_handles:

  payload_2 = {
      "operationName": "PolicySearchStructuredScopesQuery",
      "variables": {
          "handle": handle,
          "searchString": "",
          "eligibleForSubmission": None,
          "eligibleForBounty": None,
          "asmTagIds": [],
          "assetTypes": [],
          "from": 0,
          "size": 100,
          "sort": {
              "field": "cvss_score",
              "direction": "DESC"
          },
          "product_area": "h1_assets",
          "product_feature": "policy_scopes"
      },
      "query": """
      query PolicySearchStructuredScopesQuery($handle: String!, $searchString: String, $eligibleForSubmission: Boolean, $eligibleForBounty: Boolean, $minSeverityScore: SeverityRatingEnum, $asmTagIds: [Int], $assetTypes: [StructuredScopeAssetTypeEnum!], $from: Int, $size: Int, $sort: SortInput) {
        team(handle: $handle) {
          id
          team_display_options {
            show_total_reports_per_asset
            __typename
          }
          structured_scopes_search(
            search_string: $searchString
            eligible_for_submission: $eligibleForSubmission
            eligible_for_bounty: $eligibleForBounty
            min_severity_score: $minSeverityScore
            asm_tag_ids: $asmTagIds
            asset_types: $assetTypes
            from: $from
            size: $size
            sort: $sort
          ) {
            nodes {
              ... on StructuredScopeDocument {
                id
                ...PolicyScopeStructuredScopeDocument
                __typename
              }
              __typename
            }
            pageInfo {
              startCursor
              hasPreviousPage
              endCursor
              hasNextPage
              __typename
            }
            total_count
            __typename
          }
          __typename
        }
      }

      fragment PolicyScopeStructuredScopeDocument on StructuredScopeDocument {
        id
        identifier
        display_name
        instruction
        cvss_score
        eligible_for_bounty
        eligible_for_submission
        asm_system_tags
        created_at
        updated_at
        total_resolved_reports
        attachments {
          id
          file_name
          file_size
          content_type
          expiring_url
          __typename
        }
        __typename
      }
      """
  }

  response = requests.post(url, headers=headers, data=json.dumps(payload_2))


  # Extract the response text
  response_text = response.text

  # Define the regex pattern
  pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'

  # Find all matches using the regex pattern
  matches = re.findall(pattern, response_text)

  # Print the matches
  # print(f"{handle}:{matches}")

  # Process each match with tldextract
  unique_domains = set()
  for match in matches:
      extracted = tldextract.extract(match)
      # Check if suffix is not empty
      if extracted.suffix:
          domain_info = f"{extracted.domain}.{extracted.suffix}"
          unique_domains.add(domain_info)
  # Convert the unique domains set to a list
  unique_domains_list = list(unique_domains)

  # Create a dictionary for the JSON output
  output = {
      handle: unique_domains_list
  }

  # Convert the dictionary to a JSON string and print it
  print(json.dumps(output, indent=4))

  # # Print unique domain values
  # for domain in unique_domains:
  #     print(domain)
