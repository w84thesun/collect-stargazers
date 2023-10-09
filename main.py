import requests
import csv

githubURI = 'https://api.github.com/graphql'
githubToken = 'TOKEN'
githubHeaders = {
    "Authorization": "token " + githubToken, 
    "User-Agent": "request",
    "Accept": "application/vnd.github.v3+json",
}
githubStatusCode = 200

def run_query(uri, query, statusCode, headers):
    request = requests.post(uri, json={'query': query}, headers=headers)
    if request.status_code == statusCode:
        return request.json()
    else:
        raise Exception(f"Unexpected status code returned: {request.status_code}")
        
def query_repo(owner, name, after=""):
    stargazers_query = """
{{
  repository(owner: "{owner}", name: "{name}") {{
    name
    owner {{
      login
    }}
    stargazers(after: {cursor}, first: 100) {{
      pageInfo {{
        hasNextPage
        endCursor
      }}
      edges {{
        node {{
          login
        }}
        starredAt
      }}
    }}
  }}
}}
""".format(owner=owner, name=name, cursor = '"' + after + '"' if after != "" else "null")
    
    print(stargazers_query)
    
    return run_query(githubURI, stargazers_query, githubStatusCode, githubHeaders)


def process_response(response):
    if not 'data' in response:
        raise Exception(f"Unexpected response: {response}")
    
    stargazers = response['data']['repository']['stargazers']['edges']
    pageInfo = response['data']['repository']['stargazers']['pageInfo']
    hasNextPage = pageInfo['hasNextPage']
    cursor = pageInfo['endCursor']
    
    return stargazers, hasNextPage, cursor


def main():
	file = open('stargazers.csv', 'w', newline='')

	writer = csv.writer(file)
	writer.writerow(["Login", "StarredAt"])

	response = query_repo("ORG", "REPO")
	stargazers, hasNextPage, cur = process_response(response)

	while hasNextPage:
	    for x in stargazers:
	        writer.writerow([x['node']['login'], x['starredAt']])

	    response = query_repo('ORG', 'REPO', cur)

	    stargazers, hasNextPage, cur = process_response(response)
	    
	writer.close()



if __name__ == '__main__':
	main()	