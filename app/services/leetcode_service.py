import requests
import json
from datetime import datetime

class LeetcodeScraper:
    def _init_(self):
        self.base_url = 'https://leetcode.com/graphql'

    def scrape_user_profile(self, username):
        # Queries to match the image output format
        queries = {
            'userPublicProfile': '''
            query userPublicProfile($username: String!) {
              matchedUser(username: $username) {
                profile {
                  realName
                  countryName
                  company
                  jobTitle
                }
              }
            }
            ''',
            'userProblemsSolved': '''
            query userProblemsSolved($username: String!) {
              matchedUser(username: $username) {
                submitStatsGlobal {
                  acSubmissionNum {
                    difficulty
                    count
                  }
                }
                languageProblemCount {
                  languageName
                  problemsSolved
                }
              }
            }
            ''',
            'recentAcSubmissions': '''
            query recentAcSubmissions($username: String!, $limit: Int!) {
              recentAcSubmissionList(username: $username, limit: $limit) {
                id
                title
                titleSlug
                timestamp
              }
            }
            '''
        }

        output = {}
        for operation, query in queries.items():
            json_data = {
                'query': query,
                'variables': {
                    'username': username,
                    'limit': 5  # For recent submissions
                },
            }

            try:
                response = requests.post(self.base_url, json=json_data, verify=False)
                output[operation] = response.json()['data']
            except Exception as e:
                print(f'Error in {operation}: {e}')

        return output

def format_timestamp(timestamp):
    """Convert Unix timestamp to human-readable format."""
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return 'Unknown Date'

def main():
    # Create an instance of the LeetcodeScraper
    scraper = LeetcodeScraper()
    
    # Specify LeetCode username
    username = 'rakasamyak'
    
    # Scrape the user profile
    raw_data = scraper.scrape_user_profile(username)
    
    # Create a simplified data structure
    user_data = {
        'profile': {
            'real_name': raw_data['userPublicProfile']['matchedUser']['profile'].get('realName', 'N/A'),
            'country': raw_data['userPublicProfile']['matchedUser']['profile'].get('countryName', 'N/A'),
            'company': raw_data['userPublicProfile']['matchedUser']['profile'].get('company', 'None'),
            'job_title': raw_data['userPublicProfile']['matchedUser']['profile'].get('jobTitle', 'None')
        },
        'problems_solved': {
            'by_difficulty': {},
            'total': 0
        },
        'language_stats': {},
        'recent_submissions': []
    }
    
    # Process problems solved
    solved_stats = raw_data['userProblemsSolved']['matchedUser']['submitStatsGlobal']['acSubmissionNum']
    total_solved = 0
    for stat in solved_stats:
        count = stat['count']
        difficulty = stat['difficulty']
        user_data['problems_solved']['by_difficulty'][difficulty] = count
        total_solved += count
    user_data['problems_solved']['total'] = total_solved
    
    # Process language stats
    lang_stats = raw_data['userProblemsSolved']['matchedUser']['languageProblemCount']
    for lang in lang_stats:
        if lang['problemsSolved'] > 0:
            user_data['language_stats'][lang['languageName']] = lang['problemsSolved']
    
    # Process recent submissions
    for submission in raw_data['recentAcSubmissions']['recentAcSubmissionList']:
        user_data['recent_submissions'].append({
            'title': submission['title'],
            'id': submission['id'],
            'solved_on': format_timestamp(submission['timestamp']),
            'problem_link': f"https://leetcode.com/problems/{submission['titleSlug']}/"
        })
    
    # Save the simplified data to JSON
    with open(f'{username}_leetcode_profile_simplified.json', 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=2, ensure_ascii=False)
    
    # Print the data in the desired format
    print(f"Real Name: {user_data['profile']['real_name']}")
    print(f"Country: {user_data['profile']['country']}")
    print(f"Company: {user_data['profile']['company']}")
    print(f"Job Title: {user_data['profile']['job_title']}")
    print()
    
    print("--- Problems Solved ---")
    for difficulty, count in user_data['problems_solved']['by_difficulty'].items():
        print(f"{difficulty} Problems: {count}")
    print(f"All Problems: {user_data['problems_solved']['total']}")
    print()
    
    print("--- Contest Ranking ---")
    print("No contest ranking information available.")
    print()
    
    print("--- Language Stats ---")
    for lang, count in user_data['language_stats'].items():
        print(f"{lang}: {count} problems")
    print()
    
    print("--- Last 5 Problems Solved ---")
    for submission in user_data['recent_submissions']:
        print(f"Problem: {submission['title']} (ID: {submission['id']})")
        print(f"Solved on: {submission['solved_on']}")
        print(f"Problem Link: {submission['problem_link']}")
        print("---")

if __name__ == '_main_':
    main()