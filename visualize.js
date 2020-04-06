function convertPropsToLowerCase(d) {
  Object.keys(d).forEach(function(origProp) {
    var lowerCaseProp = origProp.toLocaleLowerCase();
    // if the uppercase and the original property name differ
    // save the value associated with the original prop
    // into the lowercase prop and delete the original one
    if (lowerCaseProp !== origProp) {
      d[lowerCaseProp] = d[origProp];
      delete d[origProp];
    }
  });
  return d;
}

nodes = d3.csv("out/friends.nodes.csv", convertPropsToLowerCase);
edges = d3.csv("out/friends.edges.csv", convertPropsToLowerCase);

Promise.all([nodes, edges]).then( (data ) => {
  console.log("success", data)
  data = {
    nodes: data[0],
    edges: data[1]
  }
    // Instantiate a Graph
  const graph = new G6.Graph({
    container: "mountNode", // The id of the container
    // The width and height of the graph
    width: document.body.clientWidth,
    height: window.innerHeight,
    layout: {                // Object, layout configuration. random by default
      type: 'force',         // Force layout
      preventOverlap: false,  // Prevent node overlappings
      linkDistance: 100,
      // nodeSize: 30        // The size of nodes for collide detection. Since we have assigned sizes for each node to their data in last chapter, the nodeSize here is not required any more.
      onLayoutEnd: () => {
        console.log('force layout done');
        layoutConfigTranslation();
      },
    },
    defaultNode: {
      labelCfg: {
        style: {
          fill: '#000'
        }
      }
    },
    defaultEdge: {
      labelCfg: {
        autoRotate: true
      }
    },
    nodeStateStyles: {
      hover: {
        fill: 'lightsteelblue'
      },
      click: {
        stroke: '#000',
        lineWidth: 3
      }
    },
    edgeStateStyles: {
      click: {
        stroke: 'steelblue'
      }
    },
    modes: {
      default: [ 'drag-node', 'drag-canvas', 'zoom-canvas',
                {
                  type: 'tooltip',
                  formatText(model) {
                    const text = '@' + model.screen_name;
                    return text;
                  },
                  shouldUpdate: e => {
                    return true;
                  }
                }
               ]
     }
  });
  // Load the data
  graph.data(data);
  // Render the graph
  graph.render();



  graph.on('node:mouseenter', e => {
    const nodeItem = e.item;
    graph.setItemState(nodeItem, 'hover', true);
  });
  graph.on('node:mouseleave', e => {
    const nodeItem = e.item;
    graph.setItemState(nodeItem, 'hover', false);
  });
  graph.on('node:click', e => {
    const clickNodes = graph.findAllByState('node', 'click');
    clickNodes.forEach(cn => {
      graph.setItemState(cn, 'click', false);
    });
    const nodeItem = e.item;
    graph.setItemState(nodeItem, 'click', true);
  });
  graph.on('edge:click', e => {
    const clickEdges = graph.findAllByState('edge', 'click');
    clickEdges.forEach(ce => {
      graph.setItemState(ce, 'click', false);
    });
    const edgeItem = e.item;
    graph.setItemState(edgeItem, 'click', true);
  });




  // setInterval(() => {
  //   layoutConfigTranslation();
  // }, 5000);

  function layoutConfigTranslation(){
    graph.updateLayout({
      linkDistance: 100,
      preventOverlap: true,
    });
  }

});
