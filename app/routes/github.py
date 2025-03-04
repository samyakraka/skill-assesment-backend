from flask import Blueprint, jsonify
from app.services.github_service import get_github_contributions

# Create a Blueprint for GitHub routes
github_bp = Blueprint('github', __name__, url_prefix='/api/github')

@github_bp.route('/analysis/<username>', methods=['GET'])
def analyze_github_profile(username):
    try:
        # Call the service function to get GitHub contribution data
        contribution_data = get_github_contributions(username)
        
        if not contribution_data:
            return jsonify({
                'success': False,
                'error': f'Could not fetch data for GitHub user: {username}'
            }), 404
            
        # Return successful response with contribution data
        return jsonify({
            'success': True,
            'data': {
                'username': username,
                'total_contributions': contribution_data['total_contributions'],
                'contributions_last_30_days': contribution_data['contributions_last_30_days'],
                'repositories_count': contribution_data['repositories_count']
            }
        }), 200
        
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500