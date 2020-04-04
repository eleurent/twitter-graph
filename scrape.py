import requests
import twitter
import json
from pathlib import Path
import pandas as pd
import tqdm

RATE_LIMIT_ERROR = 88

followers_path = Path("cache/followers.json")
friends_path = Path("cache/friends.json")
friendships_path = Path("cache/friendships.json")
nodes_path = Path("out/nodes.xlsx")
edges_path = Path("out/edges.xlsx")
credentials = json.loads(open("credentials.json").read())
api = twitter.Api(consumer_key=credentials["api_key"],
                  consumer_secret=credentials["api_secret_key"],
                  access_token_key=credentials["access_token"],
                  access_token_secret=credentials["access_token_secret"],
                  sleep_on_rate_limit=True)


def fetch_users():
    followers = get_or_set(followers_path, api.GetFollowers, api_function=True)
    friends = get_or_set(friends_path, api.GetFriends, api_function=True)
    mutuals = list(set(followers) & set(friends))
    return mutuals


def fetch_friendships(users, all_users=None):
    all_users = all_users if all_users else users
    friendships = get_or_set(friendships_path, {})
    users_ids = set([str(user["id"]) for user in all_users])
    for i, user in enumerate(users):
        if str(user["id"]) in friendships:
            print("[{}/{}] User @{} found in cache.".format(i, len(users), user["screen_name"]))
        else:
            print("[{}/{}] Fetching friends of user @{}".format(i, len(users), user["screen_name"]))
            try:
                user_friends = api.GetFriendIDs(user_id=user["id"], stringify_ids=True)
            except twitter.error.TwitterError as e:
                print("...but it failed. Error: {}".format(e))
                user_friends = []
                if not isinstance(e.message, str) and e.message[0]["code"] == RATE_LIMIT_ERROR:
                    print("You reached the rate limit. Use --sleep_on_rate_limit or try again later.")
                    break
            common_friends = set(user_friends).intersection(users_ids)
            friendships[user["id"]] = list(common_friends)
            get_or_set(friendships_path, friendships, force=True)
    return friendships


# noinspection PyProtectedMember
def get_or_set(path, value=None, force=False, api_function=False):
    """
        Get a value from a file if it exists, else write the value to the file.
        The value can also be a API callback, in which case the call is made only when the file is written.
    :param Path path: file path
    :param value: the value to write to the file, if known
    :param bool force:  force writing the value to the file, even if it already exists
    :param bool api_function: if the value an API function? If yes, value must be a callback for the API call.
    :return: the got or written value
    """
    # Get
    if path.exists() and not force:
        with path.open("r") as f:
            value = json.load(f)
    # Set
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        if api_function:
            value = [item._json for item in value()]
        with path.open("w") as f:
            json.dump(value, f, indent=2)
    return value


def save_to_graph(users, friendships):
    columns = [field for field in users[0] if field not in ["id", "id_str"]]
    nodes = {user["id_str"]: [user.get(field, "") for field in columns] for user in users}
    users_df = pd.DataFrame.from_dict(nodes, orient='index', columns=columns)
    users_df.to_excel(nodes_path, index_label="Id")
    edges = [[source, target] for source, source_friends in friendships.items() for target in source_friends]
    edges_df = pd.DataFrame(edges, columns=['Source', 'Target'])
    edges_df.to_excel(edges_path)


def main():
    try:
        followers, friends, mutuals = fetch_users()
        print("Followers", len(followers))
        print("Friends", len(friends))
        friendships = fetch_friendships(followers, all_users=mutuals)
        print("Friendships", len(friendships))
        save_to_graph(followers, friendships)
    except requests.exceptions.ConnectionError as e:
        print(e)
        main()  # retry!


if __name__ == "__main__":
    main()
