"""
Usage: fetch_data <mode> <query> [options]

Fetch a list of targets from Twitter API, following the given <mode>.
- In the 'users' mode, <query> refers to usernames, and we get their friends and followers.
- In the 'search' mode, <query> refers to a search query, and we get the users of the resulting tweets.
- In the 'likes' mode, <query> refers to usernames, and we get the users of the tweets they have liked.

Arguments:
  <mode>                       Mode of data fetching. Must be one of 'users', 'search', or 'likes'.
  <query>                      The username or search query for which to fetch data, depending on the mode.

Options:
  -h --help                    Show this screen.
  --max-tweets-count <type>    Maximum number of tweets to fetch before stopping. [default: 2500].
  --stop-on-rate-limit         Stop fetching and export the graph when a rate limit is raised.
  --nodes-to-consider <type>   Nodes to consider in the graph: friends, followers or all. [default: followers].
  --edges-ratio <ratio>        Ratio of edges to export in the graph (chosen randomly among non-mutuals). [default: 1].
  --credentials <file>         Path of the credentials for Twitter API [default: credentials.json].
  --excluded <file>            Path of the list of excluded users [default: excluded.json].
  --out <path>                 Directory of output files [default: out].
  --run-http-server            Run an HTTP server to visualize the graph in your browser with d3.js.
  --save_frequency <type>     Number of account between each save in cache. [default: 15].
  --filtering <type>          Filter to include only a subset of information for each account: full, light, min [default: full]
"""
from functools import partial
from time import sleep
import requests
import twitter
import json
import pandas as pd
import random
from docopt import docopt
from pathlib import Path
from enum import Enum

from serve_http import serve_http

TWITTER_RATE_LIMIT_ERROR = 88
COLUMNS_TO_EXPORT_MINIMUM = ["name", "screen_name", "followers_count", "friends_count", "created_at",
                             "default_profile_image", "Label"]
COLUMNS_TO_EXPORT_LIGHT = ["description"]


class Mode(Enum):
    USERS = 1
    SEARCH = 2
    LIKES = 3


def fetch_users(apis, target, mode, nodes_to_consider, max_tweets_count, out_path,
                followers_file="cache/followers.json",
                friends_file="cache/friends.json",
                tweets_file="cache/tweets.json"):
    """
        Fetch a list of users from Twitter API.

        - If in 'users' mode, the target is a username. We retrieve and cache the user's friends and followers.
        - If in 'search' mode, the target is a search query. We retrieve and cache the tweets associated with the query,
          up to max_tweets_count. The tweet authors are returned as "followers" of the query, and the list of friends is
          None.
        - If in 'likes' mode, the target is a username. We retrieve and cache the tweets liked by the user, up to
          max_tweets_count. The tweet authors are returned as "followers" of the query, and the list of friends is None.

        The tweets, friends and followers are all cached in json files, with the following paths populated depending on
        the mode:
        - users mode: "<out_path>/<username>/<followers_file>" and "<out_path>/<username>/<friends_file>"
        - tweets mode: "<out_path>/<query>/<followers_file>" and "<out_path>/<query>/<tweets_file>"
        - likes mode: "<out_path>/<username>/<followers_file>" and "<out_path>/<username>/<tweets_file>"

    :param List[twitter.Api] apis: a list of Twitter API instances
    :param str target: screen-name of a target
    :param Mode mode: operation mode, one of USERS, SEARCH, or LIKES.
    :param str nodes_to_consider: Nodes to consider in the graph: friends, followers or all.
    :param int max_tweets_count: maximum number of tweets fetched
    :param Path out_path: the path to the output directory
    :param str followers_file: the followers filename in the cache
    :param str friends_file: the friends filename in the cache
    :param str tweets_file: the tweets filename in the cache
    :return: followers, friends, intersection of both, and union of both
    """
    followers = friends = []
    if mode == Mode.USERS:
        if nodes_to_consider in ["followers", "all"]:
            followers = fetch_users_paged(apis, target, api_func='GetFollowersPaged',
                                          out_file=out_path / followers_file)
        if nodes_to_consider in ["friends", "all"]:
            friends = fetch_users_paged(apis, target, api_func='GetFriendsPaged',
                                        out_file=out_path / friends_file)
    else:
        if mode == Mode.SEARCH:
            tweets = get_or_set(out_path / tweets_file,
                                partial(fetch_tweets, search_query=target, apis=apis, max_count=max_tweets_count),
                                api_function=True)
        elif mode == Mode.LIKES:
            tweets = get_or_set(out_path / tweets_file,
                                partial(fetch_likes, user=target, api=apis[0], max_count=max_tweets_count),
                                api_function=True)
        else:
            raise ValueError("Unknown mode")
        print("Found {} tweets.".format(len(tweets)))
        followers = [{**tweet["user"], "query_created_at": tweet["created_at"]} for tweet in tweets]
        print("Found {} unique authors.".format(len(set(fol["id"] for fol in followers))))
        get_or_set(out_path / followers_file, followers, api_function=False)

    followers_ids = [user["id"] for user in followers]
    mutuals = [user["id"] for user in friends if user["id"] in followers_ids]
    all_users = followers + [user for user in friends if user["id"] not in followers_ids]
    return followers, friends, mutuals, all_users


def fetch_users_paged(apis, screen_name, api_func, out_file):
    api_idx = 0
    next_cursor = -1
    users = []
    while next_cursor != 0:
        try:
            # follower.json serve as a reference, it should not be used with cache
            new_users = []
            if api_func == "GetFollowersPaged":
                next_cursor, previous_cursor, new_users = apis[api_idx].GetFollowersPaged(screen_name=screen_name,
                                                                                           count=200,
                                                                                           cursor=next_cursor)
            elif api_func == "GetFriendsPaged":
                next_cursor, previous_cursor, new_users = apis[api_idx].GetFriendsPaged(screen_name=screen_name,
                                                                                           count=200,
                                                                                           cursor=next_cursor)
            users += [user._json for user in new_users]
            print(f"{api_func} found {len(users)} users.")
        except twitter.error.TwitterError as e:
            if not isinstance(e.message, str) and e.message[0]["code"] == TWITTER_RATE_LIMIT_ERROR:
                api_idx = (api_idx + 1) % len(apis)
                print(f"You reached the rate limit. Moving to next api: #{api_idx}")
                sleep(1)
            else:
                print("...but it failed. Error: {}".format(e))
    get_or_set(out_file, users, force=True, api_function=False)
    return users


def fetch_friendships(friendships, apis, users, excluded, out, target,
                      save_frequency=15,
                      stop_on_rate_limit=False,
                      friends_restricted_to=None,
                      friendships_file="cache/friendships.json") -> None:
    """
        Fetch the friends of a list of users from Twitter API
    :param Dict[str, List[str] friendships: a dictionary holding the list of friends ids, for each user id
    :param List[twitter.Api] apis: a list of Twitter API instances
    :param list users: the users whose friends to look for
    :param Path excluded: path to a file containing the screen names of users whose friends not to look for
    :param Path out: the path to output directory
    :param str target: the target query name
    :param bool stop_on_rate_limit: stop fetching when a rate limit is raised
    :param list friends_restricted_to: the set of potential friends to consider
    :param friendships_file: the friendships filename in the cache
    """
    friendships.update(get_or_set(out / target / friendships_file, friendships))
    friends_restricted_to = friends_restricted_to if friends_restricted_to else users
    users_ids = set([str(user["id"]) for user in friends_restricted_to])
    excluded = [s.lower() for s in get_or_set(excluded, [])]
    api_idx = 0
    for i, user in enumerate(users):
        if user["screen_name"].lower() in excluded:
            continue
        if str(user["id"]) in friendships:
            print(f"[{len(friendships)}] @{user['screen_name']} found in cache.")
        else:
            print(f"[{len(friendships)}] Fetching friends of @{user['screen_name']}")
            user_friends = []
            previous_cursor, next_cursor = 0, -1
            while previous_cursor != next_cursor and next_cursor != 0:
                try:
                    next_cursor, previous_cursor, new_user_friends = apis[api_idx].GetFriendIDsPaged(user_id=user["id"],
                                                                                                     stringify_ids=True,
                                                                                                     cursor=next_cursor)
                    user_friends += new_user_friends
                except twitter.error.TwitterError as e:
                    if not isinstance(e.message, str) and e.message[0]["code"] == TWITTER_RATE_LIMIT_ERROR:
                        if stop_on_rate_limit:
                            print(f"You reached the rate limit. Stopping as required.")
                            return friendships
                        api_idx = (api_idx + 1) % len(apis)
                        print(f"You reached the rate limit. Moving to next api: #{api_idx}")
                        sleep(15)
                    else:
                        print(f"failed at api: #{api_idx}")
                        print("...but it failed. Error: {}".format(e))
                        user_friends = []
                        break
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                    print(e)  # Why do I get these?
                    sleep(5)

            common_friends = set(user_friends).intersection(users_ids)
            friendships[str(user["id"])] = list(common_friends)
            # Write to file
            if i % save_frequency == 0:
                get_or_set(out / target / friendships_file, friendships.copy(), force=True)
    get_or_set(out / target / friendships_file, friendships.copy(), force=True)


def fetch_tweets(search_query, apis, max_count=1000000):
    all_tweets, tweets, max_id = [], [], None
    max_id = 0
    api_idx = 0
    while len(all_tweets) < max_count:
        try:
            tweets = apis[api_idx].GetSearch(term=search_query,
                                               count=100,
                                               result_type="recent",
                                               max_id=max_id)
        except twitter.error.TwitterError as e:
            if not isinstance(e.message, str) and e.message[0]["code"] == TWITTER_RATE_LIMIT_ERROR:
                api_idx = (api_idx + 1) % len(apis)
                print(f"You reached the rate limit. Moving to next api: #{api_idx}")
            else:
                print("...but it failed. Error: {}".format(e))
                user_friends = [""]

        all_tweets.extend(tweets)
        print(f"Found {len(all_tweets)}/{max_count} tweets.")
        if len(tweets) < 100:
            print("Done: no more tweets.")
            break
        max_id = min(tweet.id for tweet in tweets)
    print(f"First & last tweet dates are: {all_tweets[0].created_at} - {all_tweets[-1].created_at}")
    return all_tweets


# TODO: figure out what to do if the user wants to fetch all likes with no limit.
def fetch_likes(user, api, max_count=2000):
    all_tweets, max_id = [], None
    while len(all_tweets) < max_count:
        tweets = api.GetFavorites(screen_name=user,
                                  count=100,
                                  max_id=max_id)
        all_tweets.extend(tweets)
        print(f"Found {len(all_tweets)}/{max_count} tweets.")
        if len(tweets) < 100:
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
            result = value()
            value = [item._json for item in result]
        with path.open("w") as f:
            json.dump(value, f, indent=2)
    return value


def save_to_graph(users, friendships, out_path, filtering, edges_ratio=1.0):
    columns = [field for field in users[0] if field not in ["id", "id_str"]]
    nodes = {user["id_str"]: [user.get(field, "") for field in columns] for user in users}
    users_df = pd.DataFrame.from_dict(nodes, orient='index', columns=columns)
    users_df["Label"] = users_df["name"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nodes_path = out_path / "nodes.csv"
    if filtering == "full":
        users_df.to_csv(nodes_path, index_label="Id")
    else:
        columns_to_export = []
        if filtering == "light":
            columns_to_export = COLUMNS_TO_EXPORT_LIGHT + COLUMNS_TO_EXPORT_MINIMUM
        elif filtering == "minimum":
            columns_to_export = COLUMNS_TO_EXPORT_MINIMUM
        users_df.to_csv(nodes_path, index_label="Id", columns=columns_to_export)
    print("Successfully exported {} nodes to {}.".format(users_df.shape[0], nodes_path))
    print("Start calculated edge")
    edges_df = pd.DataFrame.from_dict(friendships, orient='index')
    if edges_ratio != 1.0:
        edges_df = edges_df.sample(frac=edges_ratio)
    edges_df = edges_df.stack().to_frame().reset_index().drop('level_1', axis=1)
    edges_df.columns = ['Source', 'Target']
    edges_path = out_path / "edges.csv"
    edges_df.to_csv(edges_path, index_label="Id")
    print("Successfully exported {} edges to {}.".format(edges_df.shape[0], edges_path))
    return nodes_path, edges_path


def main():
    options = docopt(__doc__)
    credentials = json.loads(open(options["--credentials"]).read())
    apis = [
        twitter.Api(consumer_key=credential["api_key"],
                    consumer_secret=credential["api_secret_key"],
                    access_token_key=credential["access_token"],
                    access_token_secret=credential["access_token_secret"],
                    sleep_on_rate_limit=False)
        for credential in credentials
    ]

    try:
        search_query = options["<query>"].split(',')
        if options["<mode>"] not in ["users", "search", "likes"]:
            raise Exception("Mode must be one of 'users', 'search', 'likes'.")
        else:
            mode = {"users": Mode.USERS, "search": Mode.SEARCH, "likes": Mode.LIKES}[options["<mode>"]]
        nodes_to_consider = options["--nodes-to-consider"]
        for target in search_query:
            print(f"Processing query {options['<mode>']}:{target}.")
            out_path = Path(options["--out"]) / target
            followers, friends, mutuals, all_users = fetch_users(apis, target, mode, nodes_to_consider,
                                                                 int(options["--max-tweets-count"]),
                                                                 out_path)
            users = {"followers": followers, "friends": friends, "all": all_users,
                     "few": random.choices(followers, k=min(100, len(followers)))}[options["--nodes-to-consider"]]
            try:
                friendships = {}
                fetch_friendships(friendships, apis, users, Path(options["--excluded"]), Path(options["--out"]), target,
                                  save_frequency=int(options["--save_frequency"]),
                                  stop_on_rate_limit=options["--stop-on-rate-limit"],
                                  friends_restricted_to=all_users)
            except KeyboardInterrupt:
                print('KeyboardInterrupt. Exporting the graph...')
            save_to_graph(users, friendships, out_path, filtering=options["--filtering"],
                          edges_ratio=float(options["--edges-ratio"]))
            if options["--run-http-server"]:
                serve_http(out_path)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        print(e)  # Why do I get these?
        main()  # Retry!


if __name__ == "__main__":
    main()
