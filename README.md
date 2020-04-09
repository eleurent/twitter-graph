# twitter-graph

I spend a lot of time on Twitter, and over the years I have been following a wide variety of people: old friends, work colleagues, funny accounts, etc.
Gradually, my timeline has become this messy mix that makes Twitter so enjoyable. 

Wouldn't it be be nice, though, to have some hindsight and perspective on what's actually going on?

Contents | [Example](#behold-the-graph-of-my-twitter-friends) | [Usage](#usage) | [References](#references) | [Credits](#credits)

## Behold: the graph of my Twitter friends

![Friends](examples/friends/friends_1080p.jpg)

<p align="center">
<em>My twitter world litterally looks like a world map, which is fantastic!</em>
</p>

#### Download

| Original | [1080p](examples/friends/friends_1080p.png) | [2160p](examples/friends/friends_2160p.png) | [4320p](examples/friends/friends_4320p.jpg) | [8640p](examples/friends/friends_8640p.jpg) |  [pdf](examples/friends/friends.pdf) |
| ---- |:-----:|:-----:|:-----:|:-----:|:-----:|  
| Labeled | [1080p](examples/friends/friends_label_1080p.png) | [2160p](examples/friends/friends_label_2160p.png) | [4320p](examples/friends/friends_label_4320p.jpg) | [8640p](examples/friends/friends_label_8640p.jpg) | [pdf](examples/friends/friends_label.pdf) |
| Hubs | [1080p](examples/friends/friends_hubs_1080p.png) | [2160p](examples/friends/friends_hubs_2160p.png) | [4320p](examples/friends/friends_hubs_4320p.jpg) | [8640p](examples/friends/friends_hubs_8640p.jpg) | [pdf](examples/friends/friends_hubs.pdf) | 

#### Clusters

By running a clustering algorithm [1, 2], several communities are automatically discovered: 
* ![#f00](https://placehold.it/15/f00/000000?text=+) the Machine Learning research community;
* ![#00f](https://placehold.it/15/00f/000000?text=+) French academia;
* ![#0ff](https://placehold.it/15/0ff/000000?text=+) software engineers, mainly from my internship at Twitter, and silicon valley startups;
* ![#0f0](https://placehold.it/15/0f0/000000?text=+) the Drone community, from my time at Parrot;
* ![#ff0](https://placehold.it/15/ff0/000000?text=+) entertainment accounts: youtubers, cartoonists, video games.

As we zoom in closer, we can find additional smaller clusters:
* ![#f90](https://placehold.it/15/f90/000000?text=+) the SequeL lab, where I am doing my PhD, and French researchers in theoretical ML
* ![#b0b](https://placehold.it/15/b0b/000000?text=+) Anglo-Saxon academia;
* ![#09f](https://placehold.it/15/09f/000000?text=+) students and staff of Mines ParisTech, my university;
* ![#cf5](https://placehold.it/15/cf5/000000?text=+) French tech, startups and entrepreneurs

#### Popular accounts

The size of the nodes represents which accounts are the most popular *according to this graph*.  
 
Intuitively, a *popular* account is followed by many other *popular* accounts. Popularity is also related the probability of reaching a node by walking randomly in the graph. The PageRank algorithm [3], used in search engines, provides such a metric. 

<p align="center">
  <a href="https://github.com/eleurent/twitter-graph/blob/master/examples/friends/friends_label_8640p.jpg"><img width="460" height="300" src="https://raw.githubusercontent.com/eleurent/twitter-graph/master/examples/friends/friends_label_1080p.jpg"></a>
</p>

On this graph the results are reasonable: accounts with many followers such as [@elonmusk](https://twitter.com/elonmusk), [@ylecun](https://twitter.com/ylecun) and [@snowden](https://twitter.com/snowden) end up with a high PageRank. But the structure of the network also plays an important part, since by only relying on the number of followers, accounts such as [@TheRealJimCarey](https://twitter.com/TheRealJimCarey), [@RobertDowneyJr](https://twitter.com/RobertDowneyJr), [@tomhanks](https://twitter.com/tomhanks) would be very salient while they barely stand out in terms of PageRank.

#### Hubs

Instead of scaling the nodes by popularity, we can also look for nodes that are in-between several communities, and connect them together. It is measured by the Betweenness Centrality, which measures how often a node appears on shortest paths between nodes of the Network.
 
<p align="center">
  <a href="https://github.com/eleurent/twitter-graph/blob/master/examples/friends/friends_hubs_8640p.jpg"><img width="460" height="300" src="https://raw.githubusercontent.com/eleurent/twitter-graph/master/examples/friends/friends_hubs_1080p.jpg"></a>
</p>

For instance, we see accounts that belong to both the AI/ML research and French academia stand out, like [@freakonometrics](https://twitter.com/freakonometrics) and [@bguedj](https://twitter.com/bguedj), or people like [@chr1sa](https://twitter.com/chr1sa) who is in-between drones and Silicon Valley clusters. 

#### Statistics

| Statistics | Value | 
| ------------- |:-------------:| 
| Nodes | 2406 |
| Edges | 107697 |
| Diameter | 9 |
| Average path length | 3.1 |
| Average degree | 44.65 |
| Average clustering coefficient| 0.234 |  

### The graph of my followers

![Friends](examples/followers/followers_1080p.jpg)

The first thing we can notice is that this graph looks more clustered than the previous one, which is confirmed by a higher average clustering coefficient.
Some clusters also seem to have disappeared, namely the ![#ff0](https://placehold.it/15/ff0/000000?text=+) entertainment and ![#b0b](https://placehold.it/15/b0b/000000?text=+) Anglo-Saxon academia.     

#### Downloads

| Original | [1080p](examples/followers/followers_1080p.png) | [2160p](examples/followers/followers_2160p.png) | [4320p](examples/followers/followers_4320p.jpg) | [8640p](examples/followers/followers_8640p.jpg) |  [pdf](examples/followers/followers.pdf) |  [svg](examples/followers/followers.svg) |
| ---- |:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| Labeled | [1080p](examples/followers/followers_label_1080p.png) | [2160p](examples/followers/followers_label_2160p.png) | [4320p](examples/followers/followers_label_4320p.jpg) | [8640p](examples/followers/followers_label_8640p.jpg) | [pdf](examples/followers/followers_label.pdf) | [svg](examples/followers/followers_label.svg) |
| Hubs | [1080p](examples/followers/followers_hubs_1080p.png) | [2160p](examples/followers/followers_hubs_2160p.png) | [4320p](examples/followers/followers_hubs_4320p.jpg) | [8640p](examples/followers/followers_hubs_8640p.jpg) | [pdf](examples/followers/followers_hubs.pdf) | [svg](examples/followers/followers_hubs.svg) |  


#### Statistics

| Statistics | Value | 
| ------------- |:-------------:| 
| Nodes | 839 |
| Edges | 10614 |
| Diameter | 8 |
| Average path length | 3.4 |
| Average degree | 12.65 |
| Average clustering coefficient| 0.316 |  



## Usage

### Step 1. Get the data

To get access to the Twitter API, you must first register on the [Twitter Developer Portal](https://developer.twitter.com/en/apps), and record your authentication keys in `credentials.json`.

Then, install requirements with
```pip3 install -r requirements.txt```

and finally run the script. ```python3 fetch_data.py```
```
Usage: fetch_data [options]

Options:
  -h --help              Show this screen.
  --screen-name <name>   Screen name of the user. By default, the account used for authentication to the API.
  --graph-nodes <type>   Nodes to consider in the graph: friends, followers or all. [default: followers].
  --edges-ratio <ratio>  Ratio of edges to export in the graph (sampled among non-mutuals). [default: 1].
  --credentials <file>   Path of the credentials for Twitter API [default: credentials.json].
  --cache <path>         Path of the user's friends cache [default: cache].
  --out <path>           Path of the graph files [default: out/graph].
  --stop-on-rate-limit   Stop fetching data and export the graph when reaching the rate limit of Twitter API.
  --run-http-server      Run an HTTP server to visualize the graph in you browser with d3.js.
```

The script will start by getting the list of your friends and followers, before going through these accounts one by one in order to build the edges of the graph.

```
Found 841 followers.
Found 2406 friends.
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

If you are too impatient and want to preview the graph with the data downloaded so far, use the `--stop-on-rate-limit` option.

The resulting graph will be exported to two .csv files containing the nodes and edges.
```
[4/2406] Fetching friends of @Ariane_lis
...but it failed. Error: [{'message': 'Rate limit exceeded', 'code': 88}]
You reached the rate limit. Disable --stop-on-rate-limit or try again later.
Successfully exported 2406 nodes to out\graph.nodes.csv.
Successfully exported 128 edges to out\graph.edges.csv.
```

### Step 2. (optional) Visualize with [d3.js](https://d3js.org/)


Once exported, the graph can be visualized directly in your browser with [d3-force](https://github.com/d3/d3-force).

To that end, use the ``--run-http-server`` to automatically spawn an HTTP server at the end of the script.
```
[2406/2406] Fetching friends of @AdrienRahier
Successfully exported 2406 nodes to out\graph.nodes.csv.
Successfully exported 107697 edges to out\graph.edges.csv.
Serving HTTP at http://localhost:8000?nodes=out/graph.nodes.csv&edges=out/graph.edges.csv
```

Open the URL in your browser to see the results. While [d3-force](https://github.com/d3/d3-force) is lightweight and convenient, it can be a bit slow when the graph becomes too large (about 2000 nodes on my computer), and will only handle the graph layout.
For more advanced customization options, you can turn to Gephi. 

### Step 2. (bis) Visualize with [Gephi](https://gephi.org/)

 
> [Gephi](https://gephi.org/) is the leading visualization and exploration software for all kinds of graphs and networks. Gephi is open-source and free.
 
The [User Guide](https://gephi.org/users/) contains all the information that you need, and I recommend that you read the [Quick Start Guide](https://gephi.org/users/quick-start/).
I will simply recall the main steps involved. 

#### 1. Import nodes

* Start a new project;
* go to the the *Data Laboratory* tab;
* select *Import Spreadsheet* in the toolbar, and choose `out/graph.nodes.csv`;
* in the *General Options* pane, select _Import as: Nodes table_, then click Next and Finish;
* in the *Import report* window, select _Append to existing workspace_, and click OK.

A table of nodes should appear in the Data Laboratory.

#### 2. Import edges

* select again *Import Spreadsheet* in the toolbar, and choose `out/graph.edges.csv`;
* in the *General Options* pane, select _Import as: Edges table_ **(not Matrix)**, then click Next and Finish;
* in the *Import report* window, click on *More options* and uncheck *Create-missing nodes* and choose *Edges merge strategy: Last*; 
* select _Append to existing workspace_, and click OK.

A table of edges should appear in the Data Laboratory.

#### 3. Choose a layout

* Go back to the *Overview* tab. You should see the graph with a random square layout;
* In the *Layout* window, select a force-based layout, and click *Run*. I use ForceAtlas2 [4];
* You can tinker with the layout parameters, such as *strength*, *Dissuade Hubs* or *Prevent Overlap*.

The graph will reorganise so that connected nodes are closer, and you should see the emergence of clusters.

#### 4. Set the nodes sizes

As mentioned above, I use PageRank [3] to set the nodes sizes.
* First, the PageRank of nodes must be computed. In the *Statistics* window, locate *Network Overview/PageRank* and click Run. Keep default parameters and close the report;
* In the *Appearance* window, select *Nodes* and *Size* in the toolbar, and than select *Ranking*. Select the range of sizes (I use 10-50), and click Apply.  

The nodes labels can be enabled by clicking the black `T` icon in the bottom *Overview* toolbar. Then, the labels can be scaled with node size  by selecting the `A` icon (Size mode) and choosing Node size.  

#### 4. Set the nodes colors

The nodes can be colored automatically in the Appearance/Nodes/Color tab, by either a Partition of attributes (e.g. verified or location), or by a Ranking of attributes (e.g.  Degree, In-Degree, Out-Degree, followers_count, etc.).

In order to identify clusters, we must first run the *Modularity* algorithm from the Statistics window. Use the *Resolution* parameter to tune the desired number of clusters.
Then, set the nodes colours in the Appearance window by Ranking of Modularity.

#### 5. Render

Go to the Preview window, select the desired options, and Export to png, pdf or svg.


## References
* [1] [Fast unfolding of communities in large networks](https://arxiv.org/abs/0803.0476), Blondel V. et al. (2008).
* [2] [Laplacian Dynamics and Multiscale Modular Structure in Networks](https://arxiv.org/abs/0812.1770), Lambiotte R. et al. (2008).
* [3] [Sergey Brin, Lawrence Page, The Anatomy of a Large-Scale Hypertextual Web Search Engine](https://snap.stanford.edu/class/cs224w-readings/Brin98Anatomy.pdf), Brin S., Page L. (1998).
* [4] [Continuous Graph Layout Algorithm for Handy Network Visualization Designed for the Gephi Software](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0098679), Jacomy M. et al. (2014).

## Credits

This project was more than inspired by this [excellent video](https://www.youtube.com/watch?v=UX7YQ6m2r_o) by [Mehdi Moussaïd
](https://twitter.com/Mehdi_Moussaid) [:tv:](https://www.youtube.com/fouloscopie).
