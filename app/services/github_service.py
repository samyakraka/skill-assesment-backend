import requests
from datetime import datetime, timedelta

def get_github_contributions(username):
    # Set up GitHub API headers - no auth token for public data
    headers = {
        'Accept': 'application/vnd.github.v3+json',
    }
    
    # Get user information to verify the user exists
    user_url = f"https://api.github.com/users/{username}"
    user_response = requests.get(user_url, headers=headers)
    
    if user_response.status_code != 200:
        return None
    
    # Calculate date 30 days ago from today
    today = datetime.now()
    thirty_days_ago = today - timedelta(days=30)
    
    # Get user's events (this includes contributions)
    # Note: GitHub API only provides events for the last 90 days
    events_url = f"https://api.github.com/users/{username}/events"
    events_response = requests.get(events_url, headers=headers)
    
    if events_response.status_code != 200:
        return None
    
    events = events_response.json()
    
    # Get user's repositories
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
    repos_response = requests.get(repos_url, headers=headers)
    
    if repos_response.status_code != 200:
        return None
    
    repos = repos_response.json()
    
    # Count contribution events
    total_contributions = 0
    recent_contributions = 0
    
    # Check events (PushEvent, CreateEvent, PullRequestEvent, etc.)
    contribution_event_types = [
        'PushEvent', 'PullRequestEvent', 'IssuesEvent', 
        'CommitCommentEvent', 'CreateEvent', 'DeleteEvent'
    ]
    
    for event in events:
        if event['type'] in contribution_event_types:
            total_contributions += 1
            event_date = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            if event_date >= thirty_days_ago:
                recent_contributions += 1
    
    return {
        "username": username,
        "total_contributions": total_contributions,
        "contributions_last_30_days": recent_contributions,
        "repositories_count": len(repos),
        "fetched_at": datetime.now().isoformat()
    }