//create somewhere to put the force directed graph
var svg = d3.select("svg");
var width = +svg.attr("width"),
    height = +svg.attr("height");
var radius = 8;

function convertPropsToLowerCase(d) {
  Object.keys(d).forEach(function(origProp) {
    var lowerCaseProp = origProp.toLocaleLowerCase();
    if (lowerCaseProp !== origProp) {
      d[lowerCaseProp] = d[origProp];
      delete d[origProp];
    }
  });
  return d;
}

var url = new URL(document.URL);
var search_params = url.searchParams;
var nodes_path = search_params.get("nodes") || "out/graph.nodes.csv";
var edges_path = search_params.get("edges") || "out/graph.edges.csv";

nodes_import = d3.csv(nodes_path, convertPropsToLowerCase);
edges_import = d3.csv(edges_path, convertPropsToLowerCase);

Promise.all([nodes_import, edges_import]).then( (data ) => {
  var nodes_data = data[0], links_data = data[1];

  //set up the simulation and add forces
  var simulation = d3.forceSimulation()
                      .nodes(nodes_data);

  var link_force =  d3.forceLink(links_data)
                          .id(function(d) { return d.id; });

  var charge_force = d3.forceManyBody()
      .strength(-200);

  var center_force = d3.forceCenter(width / 2, height / 2);

  simulation
      .force("charge_force", charge_force)
      .force("center_force", center_force)
      .force("links",link_force)
   ;


  //add tick instructions:
  simulation.on("tick", tickActions );

  //add encompassing group for the zoom
  var g = svg.append("g")
      .attr("class", "everything");

  //draw lines for the links
  var link = g.append("g")
        .attr("class", "links")
      .selectAll("line")
      .data(links_data)
      .enter().append("line");
        //.attr("stroke-width", 2)
        // .style("stroke", linkColour);

  //draw circles for the nodes
  var node = g.append("g")
          .attr("class", "nodes")
          .selectAll("circle")
          .data(nodes_data)
          .enter()
          .append("circle")
          .attr("r", radius)
          .attr("fill", circleColour)

  var label = g.append("g")
        .attr("class", "labels")
        .selectAll("text")
        .data(nodes_data)
        .enter().append("text")
        .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'central')
          .text(function (d) {return d.name;})


  //add drag capabilities
  var drag_handler = d3.drag()
      .on("start", drag_start)
      .on("drag", drag_drag)
      .on("end", drag_end);

  drag_handler(node);


  //add zoom capabilities
  var zoom_handler = d3.zoom()
      .on("zoom", zoom_actions);

  zoom_handler(svg);

  /** Functions **/

  //Function to choose what color circle we have
  function circleColour(d){
      return "Silver";
      if(d.verified == "True"){
          return "DodgerBlue";
      } else {
          return d3.interpolateOranges(0.3 + 0.7 * d.followers_count / 2000);
      }
  }

  //Function to choose the line colour
  // function linkColour(d){
  //     return "grey"
  // }

  //Drag functions
  //d is the node
  function drag_start(d) {
   if (!d3.event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
  }

  //make sure you can't drag the circle outside the box
  function drag_drag(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  }

  function drag_end(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  //Zoom functions
  function zoom_actions(){
      g.attr("transform", d3.event.transform)
  }

  function tickActions() {
      //update circle positions each tick of the simulation
         node
          .attr("cx", function(d) { return d.x; })
          .attr("cy", function(d) { return d.y; });

      //update link positions
      link
          .attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });

      label
          .attr("x", function(d) { return d.x; })
          .attr("y", function (d) { return d.y-radius-5; })
  }
});