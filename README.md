# twitter-graph

Fetch and visualize the graph of you twitter friends and followers.

## My own graph

Here is an example of what the graph of twitter friends looks like.

### Clusters

I identified several clusters, distinguished by color:
* ![#f00](https://placehold.it/15/f00/000000?text=+) the Machine Learning research community;
* ![#f0f](https://placehold.it/15/f0f/000000?text=+) the French research and higher education community;
* ![#00f](https://placehold.it/15/00f/000000?text=+) the students and professors of Mines ParisTech university;
* ![#ff0](https://placehold.it/15/ff0/000000?text=+) the SequeL lab, where I am doing my PhD;
* ![#0ff](https://placehold.it/15/0ff/000000?text=+) a startup and entrepreneurship community;
* ![#0f0](https://placehold.it/15/0f0/000000?text=+) the drone community, and that of Parrot where I worked as an engineer;

### Popular accounts

Given this graph, we can compute which account are the most popular. I use PageRank to estimate. It is related to the probability of reaching an account by following a random path in the graph.

### Hubs

People between several communities.


### 


## Usage

### Step 1. Get the data

To get access to the Twitter API, you must first register on the [Twitter Developer Portal](https://developer.twitter.com/en/apps), before filling your authentication keys in `credentials.json`.

The, run the script `python3 fetch_data.py`.
```shell
Usage: fetch_data [options]

Options:
  -h --help              Show this screen.
  --screen-name <name>   User's screen name.
  --graph-nodes <type>   Nodes to consider in the graph: friends, followers or all. [default: followers].
  --credentials <file>   Path of the credentials for Twitter API [default: credentials.json].
  --cache <path>         Path of the user's friends cache [default: cache].
  --out <path>           Path of the graph files [default: out/graph].
  --stop-on-rate-limit   Stop fetching data and export the graph when reaching the rate limit of Twitter API.
```

The script should start by getting the list of your friends and followers, before going through these accounts one by one in order to build the edges of the graph.

```
[1/2406] Fetching friends of @Mehdi_Moussaid
[2/2406] Fetching friends of @Inria_Lille
[3/2406] Fetching friends of @Limericking
```

Since Twitter limits the rate of its API to 15 requests per window of 15 minutes, this is going to take a bit of time, probably a few hours.
In order to interrupt and resume the requests at any time, a very simple caching system immediately exports the requests results to a local json file.

```
KeyboardInterrupt
[1/2406] @Mehdi_Moussaid found in cache.
[2/2406] @Inria_Lille found in cache.
[3/2406] @Limericking found in cache.
[4/2406] Fetching friends of @Ariane_lis
[5/2406] Fetching friends of @AdrienRahier
```
### Step 2. Visualize with Gephi
