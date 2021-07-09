"""
Usage: fetch_data (user|tweets) <query> [options]

Fetch a list of users from Twitter API.
- In the user mode, <query> refers to a username, and we get their friends and followers.
- In the tweets mode, <query> refers to a search query, and we get the users of the resulting tweets.

Options:
  -h --help                   Show this screen.
  --max-tweets-count <type>   Maximum number of tweets to fetch before stopping. [default: 2500].
  --graph-nodes <type>        Nodes to consider in the graph: friends, followers or all. [default: followers].
  --edges-ratio <ratio>       Ratio of edges to export in the graph (chosen randomly among non-mutuals). [default: 1].
  --credentials <file>        Path of the credentials for Twitter API [default: credentials.json].
  --excluded <file>           Path of the list of excluded users [default: excluded.json].
  --out <path>                Directory of output files [default: out].
  --stop-on-rate-limit        Stop fetching data and export the graph when reaching the rate limit of Twitter API.
  --run-http-server           Run an HTTP server to visualize the graph in you browser with d3.js.
"""
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler

import requests
import twitter
import json
import pandas as pd
import random
from docopt import docopt
from pathlib import Path

TWITTER_RATE_LIMIT_ERROR = 88


def fetch_users(api, user, search_query, max_tweets_count, out_path,
                followers_file="cache/followers.json",
                friends_file="cache/friends.json",
                tweets_file="cache/tweets.json"):
    """
        Fetch a list of users from Twitter API.

        - If a user is provided, get their friends and followers.
        - Alternatively, if a search query is provided, get the resulting tweets and their users.
          These users are returned as "followers" of the query, and the list of friends is None.

        The tweets, friends and followers are all cached in json files.

    :param twitter.Api api: a Twitter API instance
    :param str user: screen-name of a user
    :param str search_query: a search query
    :param int max_tweets_count: maximum number of tweets fetched
    :param Path out_path: the path to the output directory
    :param str followers_file: the followers filename in the cache
    :param str friends_file: the friends filename in the cache
    :param str tweets_file: the tweets filename in the cache
    :return: followers, friends, intersection of both, and union of both
    """
    if search_query:
        tweets = get_or_set(out_path / tweets_file,
                            partial(fetch_tweets, search_query=search_query, api=api, max_count=max_tweets_count),
                            api_function=True)
        # TODO: remove duplicate authors
        followers = [{**tweet["user"], "query_created_at": tweet["created_at"]} for tweet in tweets]
        # print("Found {} authors.".format(len(tweets)))
        get_or_set(out_path / followers_file, followers, api_function=False)
        friends = []
    else:
        followers = get_or_set(out_path / followers_file, partial(api.GetFollowers, screen_name=user), api_function=True)
        print("Found {} followers.".format(len(followers)))
        friends = get_or_set(out_path / friends_file, partial(api.GetFriends, screen_name=user), api_function=True)
        print("Found {} friends.".format(len(friends)))
    followers_ids = [user["id"] for user in followers]
    mutuals = [user for user in friends if user["id"] in followers_ids]
    all_users = followers + [user for user in friends if user["id"] not in followers_ids]
    return followers, friends, mutuals, all_users


def fetch_friendships(api, users, excluded, out, friends_restricted_to=None, friendships_file="cache/friendships.json"):
    """
        Fetch the friends of a list of users from Twitter API
    :param twitter.Api api: a Twitter API instance
    :param list users: the users whose friends to look for
    :param list excluded: path to a file containing the screen names of users whose friends not to look for
    :param Path out: the path to output directory
    :param list friends_restricted_to: the set of potential friends to consider
    :param friendships_file: the friendships filename in the cache
    :return dict: a dict of friendships in the form {user_id: [list of friends ids]}
    """
    friends_restricted_to = friends_restricted_to if friends_restricted_to else users
    friendships = get_or_set(out / friendships_file, {})
    users_ids = set([str(user["id"]) for user in friends_restricted_to])
    excluded = get_or_set(excluded, [])
    for i, user in enumerate(users):
        if user["screen_name"] in excluded:
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
            get_or_set(out / friendships_file, friendships, force=True)
    return friendships


def fetch_tweets(search_query, api, max_count=2000):
    all_tweets, max_id = [], None
    while len(all_tweets) < max_count:
        tweets = api.GetSearch(term=search_query,
                               count=100,
                               result_type="recent",
                               max_id=max_id)
        all_tweets.extend(tweets)
        print(f"Found {len(all_tweets)}/{max_count} tweets.")
        if not tweets:
            print("Done: no more tweets.")
            break
        max_id = min(tweet.id for tweet in tweets)
    print(f"First & last tweet dates are: {all_tweets[0].created_at} - {all_tweets[-1].created_at}")
    return all_tweets


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


def save_to_graph(users, friendships, out_path, edges_ratio=1.0, protected_users=None):
    columns = [field for field in users[0] if field not in ["id", "id_str"]]
    nodes = {user["id_str"]: [user.get(field, "") for field in columns] for user in users}
    users_df = pd.DataFrame.from_dict(nodes, orient='index', columns=columns)
    users_df["Label"] = users_df["name"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nodes_path = out_path / "nodes.csv"
    users_df.to_csv(nodes_path, index_label="Id")
    print("Successfully exported {} nodes to {}.".format(users_df.shape[0], nodes_path))
    users_ids = [user["id_str"] for user in users]

    if edges_ratio < 1:
        protected_users = [user["id_str"] for user in protected_users] if protected_users else []
        edges, protected_edges = [], []
        for source, source_friends in friendships.items():
            if source not in users_ids:
                continue
            if source in protected_users:
                protected_edges += [[source, target] for target in source_friends if target in users_ids]
            else:
                edges += [[source, target] for target in source_friends if target in users_ids]
        edges = random.choices(edges, k=int(edges_ratio * len(edges)))
        edges += protected_edges
    else:
        edges = [[source, target] for source, source_friends in friendships.items() if source in users_ids
                 for target in source_friends if target in users_ids]
    edges_df = pd.DataFrame(edges, columns=['Source', 'Target'])
    edges_path = out_path / "edges.csv"
    edges_df.to_csv(edges_path)
    print("Successfully exported {} edges to {}.".format(edges_df.shape[0], edges_path))
    return nodes_path, edges_path


def serve_http(out_path=None, server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler,
               url="http://localhost", port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    if out_path:
        nodes_path = out_path / "nodes.csv"
        edges_path = out_path / "edges.csv"
        params = "nodes={}&edges={}".format(nodes_path.as_posix(), edges_path.as_posix())
    else:
        params = ""
    print("Serving HTTP at {}:{}?{}".format(url, port, params))
    httpd.serve_forever()


def main():
    options = docopt(__doc__)
    credentials = json.loads(open(options["--credentials"]).read())
    api = twitter.Api(consumer_key=credentials["api_key"],
                      consumer_secret=credentials["api_secret_key"],
                      access_token_key=credentials["access_token"],
                      access_token_secret=credentials["access_token_secret"],
                      sleep_on_rate_limit=not options["--stop-on-rate-limit"])

    try:
        screen_name, search_query = (options["<query>"], None) if options["user"] else (None, options["<query>"])
        followers, friends, mutuals, all_users = fetch_users(api, screen_name, search_query,
                                                             int(options["--max-tweets-count"]),
                                                             Path(options["--out"]))
        users = {"followers": followers, "friends": friends, "all": all_users,
                 "few": random.choices(followers, k=min(100, len(followers)))}[options["--graph-nodes"]]
        friendships = fetch_friendships(api, users, Path(options["--excluded"]), Path(options["--out"]),
                                        friends_restricted_to=all_users)
        save_to_graph(users, friendships, Path(options["--out"]),
                      edges_ratio=float(options["--edges-ratio"]), protected_users=mutuals)
        if options["--run-http-server"]:
            serve_http(Path(options["--out"]))
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        print(e)  # Why do I get these?
        main()  # Retry!


if __name__ == "__main__":
    main()
