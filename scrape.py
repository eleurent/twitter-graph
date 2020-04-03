import twitter
import json
from pathlib import Path

followers_path = Path("followers.json")
friends_path = Path("friends.json")
friendships_path = Path("friendships.json")
credentials = json.loads(open("credentials.json").read())
api = twitter.Api(consumer_key=credentials["api_key"],
                  consumer_secret=credentials["api_secret_key"],
                  access_token_key=credentials["access_token"],
                  access_token_secret=credentials["access_token_secret"],
                  sleep_on_rate_limit=True)


def fetch_users():
    followers = get_or_set(followers_path, api.GetFollowers, api_function=True)
    friends = get_or_set(friends_path, api.GetFriends, api_function=True)
    return followers, friends


def fetch_friendships(users):
    friendships = get_or_set(friendships_path, {})
    users_ids = set([user["id"] for user in users])
    for user in users:
        if str(user["id"]) not in friendships:
            print("Fetching friends of user @{}".format(user["screen_name"]))
            try:
                user_friends = api.GetFriendIDs(user_id=user["id"])
            except twitter.error.TwitterError as e:
                print("...but failed. @{} must be protected or banned: {}".format(user["screen_name"], e))
                continue
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


def main():
    followers, friends = fetch_users()
    print("Followers", len(followers))
    print("Friends", len(friends))
    friendships = fetch_friendships(followers)
    print("Friendships", len(friendships))


if __name__ == "__main__":
    main()
