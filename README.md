# twitter-graph

Fetch and visualize the graph of you twitter friends and followers.

## Example: my own Twitter graph

Here is what the graph of my Twitter friends looks like.

### Clusters

I identified several clusters, represented by color:
* ![#f00](https://placehold.it/15/f00/000000?text=+) Machine Learning researchers;
* ![#0f0](https://placehold.it/15/0f0/000000?text=+) Drone community, from my time at Parrot;
* ![#00f](https://placehold.it/15/00f/000000?text=+) French Academia;
* ![#ff0](https://placehold.it/15/ff0/000000?text=+) Entertainment: youtubers, cartoonists, video games
* ![#0ff](https://placehold.it/15/0ff/000000?text=+) Entrepreneurship/startup community;

By zooming in, we can find smaller additional clusters:
* students and professors of Mines ParisTech university;
* the SequeL lab, where I am doing my PhD

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

Since Twitter limits the rate of its API to 15 requests per window of 15 minutes, this is going to take a while.
In order to interrupt and resume the requests at any time, a very simple caching system immediately exports the requests results to a local json file.

```
KeyboardInterrupt

python3 fetch_data.py
[1/2406] @Mehdi_Moussaid found in cache.
[2/2406] @Inria_Lille found in cache.
[3/2406] @Limericking found in cache.
[4/2406] Fetching friends of @Ariane_lis
```

### Step 2. Visualize with d3.js

When the dataset has been fetched, the resulting graph will be exported to two csv files containing the nodes and edges.
It can be visualized directly in your browser with [d3-force](https://github.com/d3/d3-force).

To that end, an HTTP server will start at the end of the script.
```
[2406/2406] Fetching friends of @AdrienRahier
Successfully exported 94 nodes to out\graph.nodes.csv.
Successfully exported 111 edges to out\graph.edges.csv.
Serving HTTP server at http://localhost:8000?nodes=out/graph.nodes.csv&edges=out/graph.edges.csv
```

### Step 2 (bis). Visualize with Gephi

Gephi is a software for...
Refer to the documentation.

I will simply recall the main steps. 

### 1. Import nodes

* Start a new project;
* go to the the *Data Laboratory* tab;
* select *Import Spreadsheet* in the toolbar, and choose `out/graph.nodes.csv`;
* in the *General Options* pane, select _Import as: Nodes table_, then click Next and Finish;
* in the *Import report* window, select _Append to existing workspace_, and click OK.

A table of nodes should appear in the Data Laboratory.

### 2. Import edges

* select again *Import Spreadsheet* in the toolbar, and choose `out/graph.edges.csv`;
* in the *General Options* pane, select _Import as: Edges table_ **(not Matrix)**, then click Next and Finish;
* in the *Import report* window, click on *More options* and uncheck *Create-missing nodes* and choose *Edges merge strategy: Last*; 
* select _Append to existing workspace_, and click OK.

A table of edges should appear in the Data Laboratory.

### 3. Choose a layout

* Go back to the *Overview* tab. You should see the graph with a random square layout;
* In the *Layout* window, select a force-based layout, and click *Run*. I use ForceAtlas2 [Jacomy M. et. al., 2014];
* You can tinker with the layout parameters, such as *Dissuade Hubs* or *Prevent Overlap*.

The graph will reorganise so that connected nodes are closer, and you should see the emergence of clusters.

### 4. Set the nodes sizes

As mentioned above, I use PageRank to set the nodes sizes.
* First, the PageRank of nodes must be computed. In the *Statistics* window, locate *Network Overview/PageRank* and click Run. Keep default parameters and close the report;
* In the *Appearance* window, select *Nodes* and *Size* in the toolbar, and than select *Ranking*. Select the range of sizes (I use 10-50), and click Apply.  

The nodes labels can be enabled by clicking the black `T` icon in the bottom *Overview* toolbar. Then, the labels can be scaled with node size  by selecting the `A` icon (Size mode) and choosing Node size.  

### 4. Set the nodes colours

The nodes can be coloured automatically in the Appearance/Nodes/Colour tab, by either a Partition of attributes (e.g. verified or location), or by a Ranking of attributes (e.g.  Degree, In-Degree, Out-Degree, followers_count, etc.).

But I prefer colouring them manually so as to distinguish the different clusters. For each cluser, I  select the Brush tool in the toolbar, pick the cluster color, and click on a few highly-connected nodes inside the cluster. All its neighbours will be coloured as well, which makes the process quick. Repeat it until the whole graph is colored.

### 5. Render

Go to the Preview window, select the desired options, and click *Export:pdf*.


## References
* [Continuous Graph Layout Algorithm for Handy Network Visualization Designed for the Gephi Software](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0098679), Jacomy M. et. al., 2014.

## Credits

This project was more than inspired by this [excellent video](https://www.youtube.com/watch?v=UX7YQ6m2r_o) by [Mehdi Moussaïd
](https://twitter.com/Mehdi_Moussaid) [:tv:](https://www.youtube.com/fouloscopie).