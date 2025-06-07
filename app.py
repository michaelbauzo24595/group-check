from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Roblox Group Rank API is running!"})

@app.route('/group-rank/<int:user_id>/<int:group_id>', methods=['GET'])
def get_user_rank(user_id, group_id):
    # Fetch user's group roles
    url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch user group data"}), 500

    groups = response.json().get("data", [])
    current_rank = None
    current_name = None
    group_name = None

    for group in groups:
        if group["group"]["id"] == group_id:
            current_rank = group["role"]["rank"]
            current_name = group["role"]["name"]
            group_name = group["group"]["name"]
            break

    if current_rank is None:
        return jsonify({"error": "User is not in the specified group"}), 404

    # Fetch full list of group roles
    roles_url = f"https://groups.roblox.com/v1/groups/{group_id}/roles"
    roles_response = requests.get(roles_url)
    if roles_response.status_code != 200:
        return jsonify({"error": "Failed to fetch group roles"}), 500

    roles = roles_response.json().get("roles", [])
    if not roles:
        return jsonify({"error": "No roles found for the group."}), 404

    # Debug: Print roles and their ranks
    print("Fetched Roles:")
    for role in roles:
        print(f"Role Name: {role['name']}, Rank: {role['rank']}")

    # Sort roles by rank
    roles_sorted = sorted(roles, key=lambda r: r["rank"])

    # Find the next rank
    next_rank_info = None
    for i, role in enumerate(roles_sorted):
        if role["rank"] == current_rank and i + 1 < len(roles_sorted):
            next_rank_info = roles_sorted[i + 1]
            break

    return jsonify({
        "group_id": group_id,
        "group_name": group_name,
        "role_name": current_name,
        "role_rank": current_rank,
        "next_rank": {
            "role_name": next_rank_info["name"],
            "role_rank": next_rank_info["rank"]
        } if next_rank_info else "User is at the highest rank or no higher rank found."
    })

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # fallback if PORT not set
    app.run(host="0.0.0.0", port=port)
