"""
Usage: fetch_data [options]

Options:
  -h --help              Show this screen.
  --screen-name <name>   User's screen name.
  --graph-nodes <type>   Nodes to consider in the graph: friends, followers or all. [default: followers].
  --credentials <file>   Path of the credentials for Twitter API [default: credentials.json].
  --cache <path>         Path of the user's friends cache [default: cache].
  --out <path>           Path of the graph files [default: out/graph].
  --stop-on-rate-limit   Stop fetching data and export the graph when reaching the rate limit of Twitter API.
"""
import requests
import twitter
import json
import pandas as pd
from docopt import docopt
from pathlib import Path

TWITTER_RATE_LIMIT_ERROR = 88
EXCLUDED = ["TayeDiggs", "RauliMrd"]


def fetch_users(api, cache, followers_file="followers.json", friends_file="friends.json"):
    """
        Fetch the lists of followers and friends from Twitter API.

        Both lists are cached in json files.
    :param twitter.Api api: a Twitter API instance
    :param Path cache: the path to a cache directory
    :param str followers_file: the followers filename in the cache
    :param str friends_file: the friends filename in the cache
    :return: followers, friends, and union of both
    """
    followers = get_or_set(cache / followers_file, api.GetFollowers, api_function=True)
    friends = get_or_set(cache / friends_file, api.GetFriends, api_function=True)
    followers_ids = [user["id"] for user in followers]
    all_users = followers + [user for user in friends if user["id"] not in followers_ids]
    return followers, friends, all_users


def fetch_friendships(api, users, cache, friends_set=None, friendships_file="friendships.json"):
    """
        Fetch the friends of a list of users from Twitter API
    :param twitter.Api api: a Twitter API instance
    :param list users: the users whose friends to look for
    :param Path cache: the path to a cache directory
    :param list friends_set: the set of potential friends to consider
    :param friendships_file: the friendships filename in the cache
    :return dict: a dict of friendships in the form {user_id: [list of friends ids]}
    """
    friends_set = friends_set if friends_set else users
    friendships = get_or_set(cache / "friendships.json", {})
    users_ids = set([str(user["id"]) for user in friends_set])
    for i, user in enumerate(users):
        if user["screen_name"] in EXCLUDED:
            continue
        if str(user["id"]) in friendships:
            print("[{}/{}] @{} found in cache.".format(i+1, len(users), user["screen_name"]))
        else:
            print("[{}/{}] Fetching friends of @{}".format(i+1, len(users), user["screen_name"]))
            try:
                user_friends = api.GetFriendIDs(user_id=user["id"], stringify_ids=True)
            except twitter.error.TwitterError as e:
                print("...but it failed. Error: {}".format(e))
                user_friends = []
                if not isinstance(e.message, str) and e.message[0]["code"] == TWITTER_RATE_LIMIT_ERROR:
                    print("You reached the rate limit. Disable --stop-on-rate-limit or try again later.")
                    break
            common_friends = set(user_friends).intersection(users_ids)
            friendships[user["id"]] = list(common_friends)
            get_or_set(cache / friendships_file, friendships, force=True)
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


def save_to_graph(users, friendships, out_path):
    columns = [field for field in users[0] if field not in ["id", "id_str"]]
    nodes = {user["id_str"]: [user.get(field, "") for field in columns] for user in users}
    users_df = pd.DataFrame.from_dict(nodes, orient='index', columns=columns)
    nodes_path = out_path.with_suffix(".nodes.xlsx")
    users_df.to_excel(nodes_path, index_label="Id")
    print("Successfully exported {} nodes to {}.".format(users_df.shape[0], nodes_path))
    users_ids = [user["id_str"] for user in users]

    edges = [[source, target] for source, source_friends in friendships.items()
             for target in source_friends if target in users_ids]
    edges_df = pd.DataFrame(edges, columns=['Source', 'Target'])
    edges_path = out_path.with_suffix(".edges.xlsx")
    edges_df.to_excel(edges_path)
    print("Successfully exported {} edges to {}.".format(edges_df.shape[0], edges_path))


def main():
    options = docopt(__doc__)
    credentials = json.loads(open(options["--credentials"]).read())
    api = twitter.Api(consumer_key=credentials["api_key"],
                      consumer_secret=credentials["api_secret_key"],
                      access_token_key=credentials["access_token"],
                      access_token_secret=credentials["access_token_secret"],
                      sleep_on_rate_limit=not options["--stop-on-rate-limit"])

    try:
        followers, friends, all_users = fetch_users(api, Path(options["--cache"]))
        users = {"followers": followers, "friends": friends, "all": all_users}[options["--graph-nodes"]]
        friendships = fetch_friendships(api, users, Path(options["--cache"]), friends_set=all_users)
        save_to_graph(users, friendships, Path(options["--out"]))
    except requests.exceptions.ConnectionError as e:
        print(e)  # Why do I get these?
        main()  # Retry!


if __name__ == "__main__":
    main()
