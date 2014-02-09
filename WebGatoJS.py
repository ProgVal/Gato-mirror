animationhead = """<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html style="border-width: 0px; margin: 0px; width: 100%%; height: 100%%" xmlns="http://www.w3.org/1999/xhtml">
<head >
    <link rel="stylesheet" type="text/css" href="%(lib_directory)s/subModal/subModal.css" />
<script type="text/javascript" src="%(lib_directory)s/subModal/common.js"></script>
<script type="text/javascript" src="%(lib_directory)s/subModal/subModal.js"></script>
<style>
html, body { margin:0; padding:0; background-image:url('./img/white_wall.png')}
embed {  overflow:scroll; position: absolute; width: 100%%; height: 100%%; background-color: #F5F5F5}
</style>
<meta http-equiv="content-type" content="application/xhtml+xml;charset=UTF-8" />
</head>
<body id="body" >
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
style="position:absolute; width:100%%; height:100%%"
xmlns:ev="http://www.w3.org/2001/xml-events" version="1.1" baseProfile="full"
preserveAspectRatio="xMinYMin meet"
viewBox="%(x)d %(y)d %(width)d %(height)d"
onload="Initialize(evt)">

<style type="text/css">
<![CDATA[
    * {
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    }
]]>

  g#AlgoButtonGroup:hover{
    opacity: 0.75;
    cursor: pointer;
  }
</style>

<defs>     
    <linearGradient id="slider_bar_lg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#999999" ></stop>
        <stop offset="1" stop-color="#AAAAAA"></stop>
    </linearGradient>

    <linearGradient id="algo_button_lg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#6ee768"></stop>
        <stop offset="1" stop-color="#42e73a"></stop>
    </linearGradient>
    
    <linearGradient id="slider_thumb_lg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#EFEFEF" ></stop>
        <stop offset="1" stop-color="#DEDEDE"></stop>
    </linearGradient>
    
    <linearGradient id="code_box_lg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fcfcfc"></stop>
        <stop offset="1" stop-color="#cbcbcb"></stop>
    </linearGradient>
    
    <linearGradient id="speed_box_lg" x1="0" y1="1" x2="0" y2="0">
        <stop offset="0" stop-color="#fcfcfc"></stop>
        <stop offset="1" stop-color="#cbcbcb"></stop>
    </linearGradient>
    
    <linearGradient id="control_box_lg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#232323"></stop>
        <stop offset="1" stop-color="#434343"></stop>
    </linearGradient>
</defs>

<filter id="dropshadow" height="130%%">
  <feGaussianBlur in="SourceAlpha" stdDeviation="1"/> <!-- stdDeviation is how much to blur -->
    <feOffset dx="2.5" dy="2.5" result="offsetblur"/> <!-- how much to offset -->
    <feMerge> 
      <feMergeNode/> <!-- this contains the offset blurred image -->
      <feMergeNode in="SourceGraphic"/> <!-- this contains the element that the filter is applied to -->
   </feMerge>
</filter>

<script type="text/ecmascript"><![CDATA[

// Index in the animation we are currently on
var step = 0;    
var time = 0;
var v_ano_id = "va"; //ID prefix for vertex annotation
var e_arrow_id = "ea"; //ID prefix for edge arrow
var svgNS = "http://www.w3.org/2000/svg";
var the_evt_target;     
var the_target;
var the_evt_target;
var element;
var code;    //HTB of code in a vertical layout
var init_graphs;  //initial graphs used for restarting animation
var edges;  //Array of all edges used for SetAllEdgesColor
var action_panel;   //ButtonPanel object for start, step, continue, and stop buttons
var speed_select;   //SpeedSelector object for controlling the speed
var state = null;  //tracks animation state ("running", "stopped", "stepping", "moving")
var movie_slider;       //Slider that controls the point in time of the graph
var timer;  //timer for AnimateLoop
var timeout = 200;  //Multiplicative factor for timeout
var horiz_layout;  //horizontal LLC for visible elements
var vert_layout;   //vertical LLC for visible elements
var left_vert_layout;   //Layout for code and speed select
var right_vert_layout;  //Layout for graphs
var current_line = 0;  //Currently 'executing' line of code in program.  While running, in range [1, infinity).  0 otherwise.
var default_vertex_radius = 14.0; //Default vertex radius
var default_line_width = 4.0; //Default line width
var x_offset = 25;  //Distance the layout is translated horizontally, in pixels
var y_offset = 45;  //Distance layout is translated vertically, in pixels
var translate_buffer = []; //Global buffer for translating graphs.
var blinking = false; //True iff blinking animation is commencing.  Prevents premature stepping
var step_pressed = false;  //Whether the step button was pressed.  Used to emulate an interrupt.
var step_evt;
var continue_pressed = false;
var continue_evt;
var button_color = "#87afff";   // Color of the buttons at bottom
var border_color = "#476fbf";   // Color of the button borders
var link_color = "#FFFFFF";     // Color of the back link
var show_algo_button_color = "#3333FF"

// Triangular scaler at bottom right of graph
var scaler;            

// Current scale factor of the graph
var g_scale_factor = {"x":1, "y":1 };

// Coordinates of mouse start when scaling
var mouse_start;        

// SVGPoint for converting browser space to svg space
var pt;             

// Interval between saved graph states
var STEP_INTERVAL = 200;

// Array of GraphState objects representing the state of the graph at every STEP_INTERVAL
var graph_states = [];      

// Array of attributes that are in use on the elements.  Check to make sure differnet graphs don't introduce new attributes.
var attr_array;                     

// Width and height of the browser after initialize
var browser_width;                  
var browser_height;                 

//Coordiante transformation matrix of the screen
var screen_ctm;                     

// Option dropdown box
var option_menu;                

// Viewbox values of the containing svg
var viewbox_x;
var viewbox_y;

// Minimum scale factor for the graph
var MIN_SCALE_FACTOR = .2;          

// Holds the bounding box maximum width and height, to which it will always be set
var G_BBOX_WIDTH;   
var G_BBOX_HEIGHT;

// Graph width(considering scaling) at the time of a mouse click on the scaler
var scale_graph_width;  

// Boolean variable that is set to true when the graph states are being filled at the start of execution
var filling_states;     

// Boolean variable that is set to true in the midst of a setgraphstate to reduce the amount of sizegraphbbox calls
var switching_states = false;

// Max width and height that the graph bounding box is throughout the animation
var MAX_GBBOX_WIDTH = 0;
var MAX_GBBOX_HEIGHT = 0;

var deleted_elements;
var added_elements;  

var two_graph = false;      // True if it is a two-graph animation
var init_height_g1;
var init_transy_g2;         // The initial translate-y value for g2.  Used for scaling smoothly


var active_tt = {"tt":null, "rect":null, "text":null};       // The tooltip that is currently visible, or null if there isn't one
var tt_padding = {"x":40, "y":20};                           // Padding constants for the tooltips
var G_INFO_POS = {"height":40, "horiz_offset":50};           // Positioning constants for the graph info

var last_line = 0;      // Last line number added to graph

var algo_info_active = false;  // Set to true when the algorithm info is currently popped up

/**
*
*
*
* Helper functions
*
*
**/
//Accepts a string of the form "...translate(x y)..." and returns x and y in a 2-index array
function getTranslate(str){
    var x;
    var y;
    
    if(str == null || str.indexOf("translate") == -1){
        return new Array(0, 0);
    }
    
    var to_parse = str.slice(str.indexOf("translate") + "translate".length);
    
    if(to_parse == null){
        return new Array(0, 0);
    }
    
    
    var r = to_parse.match(/[^,\(\)\sA-Za-z]+/g);;
    
    if(r[0] != null){
        x = parseFloat(r[0]);
    }
    
    if(r[1] != null){
        y = parseFloat(r[1]);
    }
    
    if(r[1] == null || (to_parse.indexOf(")") < to_parse.indexOf(r[1]))){
        return new Array(x, 0);
    }
    
    return new Array(x, y);

}


//Sets the first instance of "translate" in components "transform" attribute to "translate(x y)"
//Creates one if none exists.
function setTranslate(component, x, y){
    var transformation = component.getAttribute("transform");

    if(transformation != null){
        if(transformation.indexOf("translate") == -1){
            component.setAttribute("transform", transformation + " translate(" + x + " " + y + ")");
        }else{
                        var header = transformation.substring(0, transformation.indexOf("translate") + "translate".length);
            var trailer = transformation.slice(transformation.indexOf("translate") + "translate".length);
            trailer = trailer.slice(trailer.indexOf(")"));
        
            var newattr = header + "(" + x + " " + y + trailer;
            component.setAttribute("transform", newattr);
        }

    }else{
        component.setAttribute("transform", "translate(" + x + " " + y + ")");
    }
}

function shift_opacity(evt) {
    if (parseInt(evt.target.getAttribute("opacity")) <= 0.7) {
        evt.target.setAttribute("opacity", 1);
    } else {
        evt.target.setAttribute("opacity", 0.7);
    }
}

//Accepts a string of the form "...scale(x y)..." and returns x and y in a 2-index array
function getScale(str){
    var x;
    var y;
    
    if(str == null || str.indexOf("scale") == -1){
        return new Array(1, 1);
    }
    
    var to_parse = str.slice(str.indexOf("scale") + "scale".length);
    
    if(to_parse == null){
        return new Array(1, 1);
    }
    
    
    var r = to_parse.match(/[^,\(\)\sA-Za-z]+/g);
    
    if(r[0] != null){
        x = parseFloat(r[0]);
    }
    
    if(r[1] != null){
        y = x;              //This line doesn't make sense?
    }
    
    if(r[1] == null || (to_parse.indexOf(")") < to_parse.indexOf(r[1]))){
        return new Array(x, x);
    }
    
    return new Array(x, y);

}


//Sets the first instance of "scale" in components "transform" attribute to "scale(x y)"
//Creates one if none exists
function setScale(component, x, y){
    var transformation = component.getAttribute("transform");
    
    if(transformation != null){
        if(transformation.indexOf("scale") == -1){
            component.setAttribute("transform", transformation + " scale(" + x + " " + y + ")");
        }else{
                        var header = transformation.substring(0, transformation.indexOf("scale") + "scale".length);
            var trailer = transformation.slice(transformation.indexOf("scale") + "scale".length);
            trailer = trailer.slice(trailer.indexOf(")"));
        
            var newattr = header + "(" + x + " " + y + trailer;

            component.setAttribute("transform", newattr);
        }

    }else{
        component.setAttribute("transform", "scale(" + x + " " + y + ")");
    }
}


// Resizes and positions the graph bounding box based on the size and position of the graph,
// or the MAX_GBBOX_WIDTH/HEIGHT variables if not filling_states
// Additionally, it positions the scaler at the bottom right of the box
function sizeGraphBBox(graph) {
    if (switching_states === true)
        return;

    var rect = document.getElementById(graph.getAttribute("id") + "_bg");

    // Set the size of the bounding box
    if (filling_states) {
        rect.setAttribute("width",graph.getBBox().width+10);
        rect.setAttribute("height",graph.getBBox().height+10);

        // Update MAX_GBBOX values if needed
        if ((graph.getBBox().width+10) > MAX_GBBOX_WIDTH)
            MAX_GBBOX_WIDTH = graph.getBBox().width+10;
        if ((graph.getBBox().height+10) > MAX_GBBOX_HEIGHT)
            MAX_GBBOX_HEIGHT = graph.getBBox().height+10;

    } else {
        rect.setAttribute("width", MAX_GBBOX_WIDTH);
        rect.setAttribute("height", MAX_GBBOX_HEIGHT);
    }

    repositionScaler(graph.getBBox().x, graph.getBBox().y);
    // Reposition the bounding box
    rect.setAttribute("x", graph.getBBox().x-10);
    rect.setAttribute("y", graph.getBBox().y-10);
}


//Creates a textnode with the given text
function createLabel(id, text, color) {
    var label = document.createElementNS(svgNS, "text");
    label.setAttribute("id", id);
    label.setAttribute("x", 0);
    label.setAttribute("y", 14);
    label.setAttribute("fill", color);
    label.setAttribute("font-size", "15px");
    var textNode = document.createTextNode(text);
    label.appendChild(textNode);
    the_evt_target.appendChild(label);
    return label;
}


//Return a 2-index array [v1,v2] which has an angle of
//90 degrees clockwise to the vector (dx,dy)
function Orthogonal(dx, dy){

    var u1 = dx;
    var u2 = dy;
    
    var length = Math.sqrt(Math.pow(u1,2) + Math.pow(u2,2));
    
    if(length < 0.001){
        length = 0.001;
    }
    
    u1 /= length;
    u2 /= length;
    return [-1*u2, u1];
}


//Fills the edges array with all the edges that are currently active on the graph
function fillEdgesArray() {
    edges = new Array();
    edges.push(new Array());
    if (two_graph) {
        edges.push(new Array());
    }

    var highestNodeg1 = 1;
    while (document.getElementById("g1_" + highestNodeg1) != null)
        highestNodeg1++;
    highestNodeg1--;

    //See if it is a two graph algo also, have 2nd edges array declared just in case
    for (var i=0; i<=highestNodeg1; i++) {
        for (var j=0; j<=highestNodeg1; j++) {
            var element = document.getElementById("g1_("+i+", "+j+")");
            if (element != null) 
                edges[0].push(element);
        }
    }


    if (two_graph) {
        var highestNodeg2 = 1;
        while (document.getElementById("g2_" + highestNodeg2) != null)
            highestNodeg2++;
        highestNodeg2--;
        //See if it is a two graph algo also, have 2nd edges array declared just in case
        for (var i=0; i<=highestNodeg2; i++) {
            for (var j=0; j<=highestNodeg2; j++) {
                var element = document.getElementById("g2_("+i+", "+j+")");
                if (element != null) 
                    edges[1].push(element);
            }
        }
    }
}


//Creates an arrowhead on a line starting at (vx,vy) and ending at (wx,wy) and parallel to it
//Arrowhead with given id touches the outide of a vertex with cx=wx and xy=wy
function createArrowhead(vx, vy, wx, wy, stroke_width, id){

    var l = Math.sqrt(Math.pow(parseFloat(wx)-parseFloat(vx),2) + Math.pow(parseFloat(wy)-parseFloat(vy), 2));
    
    if (l < .001)
        l = .001;
                
    var a_width = (1 + 1.5/(1*Math.pow(Math.log(parseFloat(stroke_width))/Math.log(10), 6)));

    if(a_width > 5.0)
        a_width = 5.0;
        
    var cr = default_vertex_radius;
    
    a_width = a_width * parseFloat(stroke_width);

    var p1 = [0,0];
    var p2 = [0, a_width];
    var p3 = [cr, a_width/2];
    var angle = (Math.atan2(parseInt(wy)-parseInt(vy), parseInt(wx)-parseInt(vx))) * 180/Math.PI;
    var c = (l-2*default_vertex_radius)/l;
    var tmpX = parseFloat(vx) + c*(parseFloat(wx) - parseFloat(vx));
    var tmpY = parseFloat(vy) + c*(parseFloat(wy) - parseFloat(vy));
    
    var arrowhead = document.createElementNS(svgNS, "polyline");
    arrowhead.setAttribute("points", p1[0] + " " + p1[1] + " " + p2[0] + " " + p2[1] + " " + p3[0] + " " + p3[1]);
    arrowhead.setAttribute("fill", "#EEEEEE");
    arrowhead.setAttribute("transform", "translate(" + tmpX + " " + (tmpY-a_width/2) + ") rotate(" + angle + " " + p1[0] + " " + a_width/2 + ")");
    arrowhead.setAttribute("id", id);

    return arrowhead;
}


/**
*
*
*
* Classes for visible components
*
*
*/
//Highlightable block of text
//Parameters: horizontal and vertical padding between lines, id, font size of text, and layout mode (horizontal or vertical)
function HighlightableTextBlock(hp, vp, id, font_size, layout){
    this.line_llc = new LinearLayoutComponent(hp, vp, id, layout);
    this.line_llc.group.setAttribute("font-size", font_size);
    this.highlight_group = document.createElementNS(svgNS,"g");
    this.highlight_group.setAttribute("id", id + "_hg");
    the_evt_target.insertBefore(this.highlight_group, this.line_llc.group);
}


//Initializes prototype, to call object.function
function HTB_prototypeInit(){
    var htb = new HighlightableTextBlock(2,2,"foo",14, "vertical");
    HighlightableTextBlock.prototype.insertLine = HTB_insertLine;
    HighlightableTextBlock.prototype.deleteLine = HTB_deleteLine;
    HighlightableTextBlock.prototype.highlightLine = HTB_highlightLine;
    HighlightableTextBlock.prototype.removeHighlight = HTB_removeHighlight;
    HighlightableTextBlock.prototype.addBoundingBoxAndAlgoButton = HTB_addBoundingBoxAndAlgoButton;
    htb = document.getElementById("foo");
    htb.parentNode.removeChild(htb);
    htb = document.getElementById("foo_hg");
    htb.parentNode.removeChild(htb);
}


//Adds a rectangular box around the code section
function HTB_addBoundingBoxAndAlgoButton(color) {
    var bbox = this.line_llc.group.getBBox();
    var line = this.line_llc.group.childNodes.item(0);
    var rect = document.createElementNS(svgNS, "rect");
    var line_translation = getTranslate(this.line_llc.group.childNodes.item(0).getAttribute("transform"));
    var dx = line.getAttribute("dx");
    if(dx == null)
        dx = 0;
    else
        dx = parseFloat(dx);
    
    rect.setAttribute("id", "codeBox");
    rect.setAttribute("width", bbox.width + this.line_llc.h_padding*2);
    rect.setAttribute("height", bbox.height + this.line_llc.v_padding*2 + 10);
    rect.setAttribute("x", bbox.x + line_translation[0] - this.line_llc.h_padding - dx);
    rect.setAttribute("y", bbox.y - this.line_llc.v_padding - 5);
    rect.setAttribute("fill", "url(#code_box_lg)");
    rect.setAttribute("stroke", color);
    rect.setAttribute("stroke-width", "3px");
    rect.setAttribute("rx", 5);
    rect.setAttribute("ry", 5);
    //var button = addAlgoButton(bbox.x + line_translation[0] - this.line_llc.h_padding - dx, bbox.y - this.line_llc.v_padding - 5);
    
    this.highlight_group.insertBefore(rect, this.highlight_group.firstChild);
}


//Insert line with respective into nth slot.  0-based indexing.  If line already exists in HTB, line is shifted to respective spot.
function HTB_insertLine(id, n){
    var to_insert = document.getElementById(id);
    if(to_insert != null && to_insert.getAttribute("blank") != null && to_insert.getAttribute("blank") == "true"){ // Empty Text  Replace with Rectangle
        var new_rect = document.createElementNS(svgNS, "rect");
        var children = this.line_llc.group.childNodes;
        for (var i = 0; i < children.length; i++){
            if(children.item(i).getAttribute("blank") == "false"){
                new_rect.setAttribute("x", children.item(i).getAttribute("x"));
                new_rect.setAttribute("y", children.item(i).getAttribute("y"));
                new_rect.setAttribute("height", children.item(i).getBBox().height);
                new_rect.setAttribute("width", this.line_llc.group.getBBox().width);
                to_insert.parentNode.removeChild(to_insert);
                new_rect.setAttribute("id", to_insert.getAttribute("id"));
                new_rect.setAttribute("fill", "white");
                new_rect.setAttribute("fill-opacity", 0);
                the_evt_target.appendChild(new_rect);
                break;
            }
        }
    }
    this.line_llc.insertComponent(id, n);
}


//Deletes nth line, using 0-based indexing
function HTB_deleteLine(n){
    this.line_llc.deleteComponent(n);
    this.removeHighlight(this.line_llc.group.childNodes.length);
}


//highlight nth line, using 0-based indexing
function HTB_highlightLine(n){
    if(n < this.line_llc.group.childNodes.length && n >= 0){
        if(document.getElementById(this.line_llc.group.getAttribute("id") + "_hl" + (n+1)) == null){
            var line = this.line_llc.group.childNodes.item(n);
            var htb_bbox = this.line_llc.group.getBBox();
            var line_bbox = line.getBBox();
            var line_translation = getTranslate(this.line_llc.group.childNodes.item(n).getAttribute("transform"));

            
            var dx = line.getAttribute("dx");
            var dy = line.getAttribute("dy");
            if(dx == null){
                dx = 0;
            }else{
                dx = parseFloat(dx);
            }
            if(dy == null){
                dy = 0;
            }else{
                dy = parseFloat(dy);
            }

            var background = document.createElementNS(svgNS, "rect");
            background.setAttribute("x", line_bbox.x + line_translation[0] - this.line_llc.h_padding - dx + 2);
            background.setAttribute("y", line_bbox.y + line_translation[1] - this.line_llc.v_padding - dy);
            background.setAttribute("width", htb_bbox.width + 2*this.line_llc.h_padding - 24);
            background.setAttribute("height", line_bbox.height + 2*this.line_llc.v_padding);
            background.setAttribute("style", "opacity:.35");
            background.setAttribute("stroke", "blue");
            background.setAttribute("fill", "yellow");
            background.setAttribute("id", this.line_llc.group.getAttribute("id") + "_hl" + (n+1));
            
            this.highlight_group.appendChild(background);
        }
    }
}


//Removes the highlight of the nth line, using 0-based indexing.
function HTB_removeHighlight(n){
    var hl = document.getElementById(this.line_llc.group.getAttribute("id") + "_hl" + (n+1));
    if(hl != null){
        hl.parentNode.removeChild(hl);
    }
}


//Layout for components
//Lays out components linearly either 'horizontal' or 'vertical' as specified by layout
//With hp pixels of horizontal padding and vp pixels of vertical padding
function LinearLayoutComponent(hp, vp, id, layout){
    this.h_padding = hp;  //Number of pixels padding the top and bottom of each line
    this.v_padding = vp;  //Number of pixels padding the left and right of each line
    this.id = id;           //ID of group that is abstracted by this HTB instance
    
    //Create new group element to place all lines of code
    this.group = document.createElementNS(svgNS,"g");
    this.group.setAttribute("id", id);
    the_evt_target.appendChild(this.group);
    this.layout = layout;  //'horizontal' or 'vertical'
}


//Initializes prototype to call methods of the form object.function
function LLC_prototypeInit(){
    var llc = new LinearLayoutComponent(0,0,"foo","horizontal");
    LinearLayoutComponent.prototype.insertComponent = LLC_insertComponent;
    LinearLayoutComponent.prototype.deleteComponent = LLC_deleteComponent;
    LinearLayoutComponent.prototype.resnapComponent = LLC_resnapComponent;
    llc.group.parentNode.removeChild(llc.group);
}


//Insert element of specified id into nth slot, using 0-based indexing.
//If element is already in LLC, element is moved to nth slot
function LLC_insertComponent(id, n){
    var new_c = document.getElementById(id);
    var padding = 0;
    if(this.layout == "horizontal"){
        padding = this.h_padding;
    }else{
        padding = this.v_padding;
    }
    var bbox = null;
    var translation = null;
    var shift = 0;
    
    if(new_c != null){   //Component exists
        if((new_c.parentNode != this.group) && (n <= this.group.childNodes.length) && (n >=0)){ //Component is not in group.  Insert and shift if necessary
        
            if(n == 0){ //inserting as first element
                setTranslate(new_c, 0, 0);
            }else{  //not inserting as first element
                bbox = this.group.childNodes.item(n-1).getBBox();
                //translation of previous element
                translation = getTranslate(this.group.childNodes.item(n-1).getAttribute("transform"));
                
                if(this.layout == "horizontal"){
                    shift = translation[0] + bbox.width + 2*padding;
                    setTranslate(new_c, shift, 0);

                }else{      
                    shift = translation[1] + bbox.height + 2*padding;
                    setTranslate(new_c, 0, shift);
                }
            }
            
            if(n == this.group.childNodes.length){
                this.group.appendChild(new_c);
            }else{  
                var children = this.group.childNodes;
                this.group.insertBefore(new_c, children.item(n));
                for (var i = n+1; i < children.length; i++){
                    bbox = children.item(i-1).getBBox();
                    translation = getTranslate(children.item(i-1).getAttribute("transform"));
                    if(this.layout == "horizontal"){
                        shift = translation[0] + bbox.width + 2*padding;
                        setTranslate(children.item(i), shift, 0);
                    }else{      
                        shift = translation[1] + bbox.height + 2*padding;
                        setTranslate(children.item(i), 0, shift);
                    }
                    
                }
            }
        }else if(n <= this.group.childNodes.length && (n >= 0)){ //Component is in group.  Move it and shift necessary lines
            var children = this.group.childNodes;
            var old_index = 0;
            for(; old_index < children.length; old_index++){
                if(children.item(old_index) === new_c){
                    break;
                }
            }
            if(old_index > n){
                this.group.insertBefore(new_c, children.item(n));
                
                for (var i = n; i <= old_index; i++){
                    if(i == 0){
                        setTranslate(children.item(i), 0, 0);
                    }else{
                        bbox = children.item(i-1).getBBox();    
                        translation = getTranslate(children.item(i-1).getAttribute("transform"));
                        if(this.layout == "horizontal"){
                            shift = translation[0] + bbox.width + 2*padding;
                            setTranslate(children.item(i), shift, 0);
                        }else{      
                            shift = translation[1] + bbox.height + 2*padding;
                            setTranslate(children.item(i), 0, shift);
                        }
                    }
                }
            }else if(old_index < n){
                if(n == children.length){
                    this.group.appendChild(new_c);
                }else{  
                    this.group.insertBefore(new_c, children.item(n+1));
                }
                for (var i = old_index; i <= n; i++){            
                    if(i == 0){
                        setTranslate(children.item(i), 0, 0);

                    }else{
                        bbox = children.item(i-1).getBBox();
                        translation = getTranslate(children.item(i-1).getAttribute("transform"));
                        if(this.layout == "horizontal"){
                            shift = translation[0] + bbox.width + 2*padding;
                            setTranslate(children.item(i), shift, 0);
                        }else{      
                            shift = translation[1] + bbox.height + 2*padding;
                            setTranslate(children.item(i), 0, shift);
                        }
                    }
                }
            }
        }
    }
}


//Refits the nth element, to fit according to specs
function LLC_resnapComponent(n){
    var children = this.group.childNodes;
    var child = children.item(n);
    child.parentNode.removeChild(child);
    
    the_evt_target.appendChild(child);
    this.insertComponent(child.getAttribute("id"), n);
}


//Deletes the nth element, using 0-based indexing, and refits components if necessary
function LLC_deleteComponent(n){
    var padding = 0;
    var children = this.group.childNodes;
    var bbox = null;
    var translation = null;
    var shift = 0;
    
    if(this.layout == "horizontal"){
        padding = this.h_padding;
    }else{
        padding = this.v_padding;
    }
    
    if(this.group.childNodes.length == 0){
        return;
    }   

    var removed_element = this.group.removeChild(this.group.childNodes.item(n));
    
    for (var i = n; i < children.length; i++){

        if(i == 0){

            setTranslate(children.item(i), 0, 0);


        }else{
            bbox = children.item(i-1).getBBox();


            translation = getTranslate(children.item(i-1).getAttribute("transform"));

            if(this.layout == "horizontal"){
                shift = translation[0] + bbox.width + 2*padding;
                setTranslate(children.item(i), shift, 0);
            }else{      
                shift = translation[1] + bbox.height + 2*padding;

                setTranslate(children.item(i), 0, shift);
            }
        }
    }
}

function LinearLayoutComponent(hp, vp, id, layout){
    this.h_padding = hp;  //Number of pixels padding the top and bottom of each line
    this.v_padding = vp;  //Number of pixels padding the left and right of each line
    this.id = id;           //ID of group that is abstracted by this HTB instance
    
    //Create new group element to place all lines of code
    this.group = document.createElementNS(svgNS,"g");
    this.group.setAttribute("id", id);
    the_evt_target.appendChild(this.group);
    this.layout = layout;  //'horizontal' or 'vertical'
}


//Initializes prototype to call methods of the form object.function
function LLC_prototypeInit(){
    var llc = new LinearLayoutComponent(0,0,"foo","horizontal");
    LinearLayoutComponent.prototype.insertComponent = LLC_insertComponent;
    LinearLayoutComponent.prototype.deleteComponent = LLC_deleteComponent;
    LinearLayoutComponent.prototype.resnapComponent = LLC_resnapComponent;
    llc.group.parentNode.removeChild(llc.group);
}


//Insert element of specified id into nth slot, using 0-based indexing.
//If element is already in LLC, element is moved to nth slot
function LLC_insertComponent(id, n){
    var new_c = document.getElementById(id);
    var padding = 0;
    if(this.layout == "horizontal"){
        padding = this.h_padding;
    }else{
        padding = this.v_padding;
    }
    var bbox = null;
    var translation = null;
    var shift = 0;
    
    if(new_c != null){   //Component exists
        if((new_c.parentNode != this.group) && (n <= this.group.childNodes.length) && (n >=0)){ //Component is not in group.  Insert and shift if necessary
        
            if(n == 0){ //inserting as first element
                setTranslate(new_c, 0, 0);
            }else{  //not inserting as first element
                bbox = this.group.childNodes.item(n-1).getBBox();
                //translation of previous element
                translation = getTranslate(this.group.childNodes.item(n-1).getAttribute("transform"));
                
                if(this.layout == "horizontal"){
                    shift = translation[0] + bbox.width + 2*padding;
                    setTranslate(new_c, shift, 0);

                }else{      
                    shift = translation[1] + bbox.height + 2*padding;
                    setTranslate(new_c, 0, shift);
                }
            }
            
            if(n == this.group.childNodes.length){
                this.group.appendChild(new_c);
            }else{  
                var children = this.group.childNodes;
                this.group.insertBefore(new_c, children.item(n));
                for (var i = n+1; i < children.length; i++){
                    bbox = children.item(i-1).getBBox();
                    translation = getTranslate(children.item(i-1).getAttribute("transform"));
                    if(this.layout == "horizontal"){
                        shift = translation[0] + bbox.width + 2*padding;
                        setTranslate(children.item(i), shift, 0);
                    }else{      
                        shift = translation[1] + bbox.height + 2*padding;
                        setTranslate(children.item(i), 0, shift);
                    }
                    
                }
            }
        }else if(n <= this.group.childNodes.length && (n >= 0)){ //Component is in group.  Move it and shift necessary lines
            var children = this.group.childNodes;
            var old_index = 0;
            for(; old_index < children.length; old_index++){
                if(children.item(old_index) === new_c){
                    break;
                }
            }
            if(old_index > n){
                this.group.insertBefore(new_c, children.item(n));
                
                for (var i = n; i <= old_index; i++){
                    if(i == 0){
                        setTranslate(children.item(i), 0, 0);
                    }else{
                        bbox = children.item(i-1).getBBox();    
                        translation = getTranslate(children.item(i-1).getAttribute("transform"));
                        if(this.layout == "horizontal"){
                            shift = translation[0] + bbox.width + 2*padding;
                            setTranslate(children.item(i), shift, 0);
                        }else{      
                            shift = translation[1] + bbox.height + 2*padding;
                            setTranslate(children.item(i), 0, shift);
                        }
                    }
                }
            }else if(old_index < n){
                if(n == children.length){
                    this.group.appendChild(new_c);
                }else{  
                    this.group.insertBefore(new_c, children.item(n+1));
                }
                for (var i = old_index; i <= n; i++){            
                    if(i == 0){
                        setTranslate(children.item(i), 0, 0);

                    }else{
                        bbox = children.item(i-1).getBBox();
                        translation = getTranslate(children.item(i-1).getAttribute("transform"));
                        if(this.layout == "horizontal"){
                            shift = translation[0] + bbox.width + 2*padding;
                            setTranslate(children.item(i), shift, 0);
                        }else{      
                            shift = translation[1] + bbox.height + 2*padding;
                            setTranslate(children.item(i), 0, shift);
                        }
                    }
                }
            }
        }
    }
}


//Refits the nth element, to fit according to specs
function LLC_resnapComponent(n){
    var children = this.group.childNodes;
    var child = children.item(n);
    child.parentNode.removeChild(child);
    
    the_evt_target.appendChild(child);
    this.insertComponent(child.getAttribute("id"), n);
}


//Deletes the nth element, using 0-based indexing, and refits components if necessary
function LLC_deleteComponent(n){
    var padding = 0;
    var children = this.group.childNodes;
    var bbox = null;
    var translation = null;
    var shift = 0;
    
    if(this.layout == "horizontal"){
        padding = this.h_padding;
    }else{
        padding = this.v_padding;
    }
    
    if(this.group.childNodes.length == 0){
        return;
    }   

    var removed_element = this.group.removeChild(this.group.childNodes.item(n));
    
    for (var i = n; i < children.length; i++){

        if(i == 0){

            setTranslate(children.item(i), 0, 0);


        }else{
            bbox = children.item(i-1).getBBox();


            translation = getTranslate(children.item(i-1).getAttribute("transform"));

            if(this.layout == "horizontal"){
                shift = translation[0] + bbox.width + 2*padding;
                setTranslate(children.item(i), shift, 0);
            }else{      
                shift = translation[1] + bbox.height + 2*padding;

                setTranslate(children.item(i), 0, shift);
            }
        }
    }
}


//Button Panel
//Buttons are padded by hp and vp pixels.
//Button panel's id given by id, and layout of buttons is given by layout
function ButtonPanel(hp, vp, id, layout){
    this.llc = new LinearLayoutComponent(hp, vp, id, layout);
}


//Initializes prototype for button panel
function BP_prototypeInit(){
    var bp = new ButtonPanel(0,0,"baz","horizontal");
    ButtonPanel.prototype.createButton = BP_createButton;
    ButtonPanel.prototype.deleteButton = BP_deleteButton;
    ButtonPanel.prototype.deleteButtonById = BP_deleteButtonById;
    ButtonPanel.prototype.activateButton = BP_activateButton;
    ButtonPanel.prototype.deactivateButton = BP_deactivateButton;
    bp.llc.group.parentNode.removeChild(bp.llc.group);
}


//Creates a button
//Parameters:  button id, shape (path), color, index in button panel, button action
//Inserts button into specified and assigns specifieds action
function BP_createButton(id, draw_path, color, index, action){  //Create button with corresponding id, text, and action into slot #index
    if(document.getElementById(id) == null){
        var button_group = document.createElementNS(svgNS, "path");
        button_group.setAttribute("id", id);
        button_group.setAttribute("d", draw_path);
        button_group.setAttribute("fill", color);
        button_group.setAttribute("cursor", "pointer");
        button_group.setAttribute("onclick", action);
                button_group.setAttribute("fill-opacity", 1);
        the_evt_target.appendChild(button_group);
        this.llc.insertComponent(button_group.getAttribute("id"), index);
    }else{
        this.llc.insertComponent(id, index);
    }
}


//Deletes the nth button from panel (0-based indexing)
function BP_deleteButton(n){
    this.llc.deleteComponent(n);
}


//Deletes button of given id from the panel
function BP_deleteButtonById(id){
    var children = this.llc.group.childNodes;
    
    for (var i = 0; i < children.length; i++){
        if(children.item(i).getAttribute("id") == id){
            this.deleteButton(i);
            break;
        }
    }
}


//Activates button with corresponding id and assigns a specified action
function BP_activateButton(id, action){
    var children = this.llc.group.childNodes;
    for (var i = 0; i < children.length; i++){
        if(children.item(i).getAttribute("id") == id){
            children.item(i).setAttribute("onclick", action);
            children.item(i).setAttribute("cursor", "pointer");
            children.item(i).setAttribute("fill-opacity", 1);
            break;
        }
    }
}


//Deactivates button with corresponding id
function BP_deactivateButton(id){
    var children = this.llc.group.childNodes;

    for (var i = 0; i < children.length; i++){
        if(children.item(i).getAttribute("id") == id){
            children.item(i).setAttribute("onclick", "");
            children.item(i).setAttribute("cursor", "default");
            children.item(i).setAttribute("fill-opacity", "0.47");
            break;
        }
    }
}


function BackLink(id, text, color) {
    this.link = document.getElementById("backlink_a");
    this.group = document.createElementNS(svgNS, "g");
    this.group.setAttribute("id", "backlink");
    this.group.appendChild(this.link);
    the_evt_target.appendChild(this.group);
}


/* Constructor that creates a speed selector group. */
function SpeedSelector(id, boxWidth, color, border_color) {
    this.llc = new LinearLayoutComponent(8,4,id, "horizontal");
    this.color = color;
    this.border_color = border_color;
    this.boxWidth = boxWidth;
    this.label = createLabel("speedLabel", "Animation Speed:", "#DDDDDD");
    this.label.setAttribute("font-family", "Helvetica");
    this.label.setAttribute("font-weight", "bold");
    this.llc.insertComponent(this.label.getAttribute("id"),0);
    this.lo = createSpeedSelect("lo", "0", "0", boxWidth, ".25x", this.color, this.border_color);
    this.lomid = createSpeedSelect("lomid", "0", "0", boxWidth, ".5x", this.color, this.border_color);
    this.mid = createSpeedSelect("mid", "0", "0", boxWidth, "1x", this.color, this.border_color);
    this.midhi = createSpeedSelect("midhi", "0", "0", boxWidth, "2x", this.color, this.border_color);
    this.hi = createSpeedSelect("hi", "0", "0", boxWidth, "4x", this.color, this.border_color);
    this.llc.insertComponent(this.lo.getAttribute("id"),1);
    this.llc.insertComponent(this.lomid.getAttribute("id"), 2);
    this.llc.insertComponent(this.mid.getAttribute("id"), 3);
    this.llc.insertComponent(this.midhi.getAttribute("id"), 4);
    this.llc.insertComponent(this.hi.getAttribute("id"), 5);
    
    this.boxSelected(this.lo.firstChild);
    this.group = this.llc.group;
}

function SS_prototypeInit() {
    SpeedSelector.prototype.boxSelected = SS_boxSelected;
    SpeedSelector.prototype.addBoundingBox = SS_addBoundingBox;
}

function SS_boxSelected(box) {
    var boxId = box.getAttribute("id");
    var groups = this.llc.group.childNodes;     

    //Change box colors
    //Start at i=1 to skip the label, and the bounding box
    for ( i=1; i<groups.length; i++) {
        var currBox = groups.item(i).firstChild;
        
        if (boxId === currBox.getAttribute("id")) {
            currBox.setAttribute("fill-opacity", 1);
        } else {
            currBox.setAttribute("fill-opacity", .5);
        }
    }
    
    //Change animation speed
    if (boxId === "lo") {
        timeout = 200;
    } else if (boxId === "lomid") { 
        timeout = 37;
    } else if (boxId === "mid") {
        timeout = 22;
    } else if (boxId === "midhi") {
        timeout = 10;
    } else if (boxId === "hi") {
        timeout = .8;
    }
}

function SS_addBoundingBox(color) {
    var this_bbox = this.llc.group.getBBox();
    var llc_bbox = left_vert_layout.group.getBBox();
    this.bbox = document.createElementNS(svgNS, "rect");
    
    this.bbox.setAttribute("id", "speedBox");
    this.bbox.setAttribute("width", this_bbox.width + this.llc.h_padding*3);
    this.bbox.setAttribute("height", this_bbox.height + this.llc.v_padding*2 + 10);
    this.bbox.setAttribute("x", llc_bbox.x - left_vert_layout.h_padding);
    this.bbox.setAttribute("y", this_bbox.y - this.llc.v_padding);
    this.bbox.setAttribute("rx", 5);
    this.bbox.setAttribute("ry", 5);
    this.bbox.setAttribute("fill", "url(#speed_box_lg)");
    this.bbox.setAttribute("stroke", color);
    this.bbox.setAttribute("stroke-width", "2px");
    this.llc.group.insertBefore(this.bbox, the_evt_target.getElementById('speedLabel'));
}

//Creates a speed selector box with the given parameters
function createSpeedSelect(id, x, y, boxWidth, text, color, border_color) {
    var group = document.createElementNS(svgNS, "g");
    var rect = document.createElementNS(svgNS, "rect");
    var label = document.createElementNS(svgNS, "text");
    
    group.setAttribute("id", id + "_g");
    
    rect.setAttribute("id", id);
    rect.setAttribute("x", x);
    rect.setAttribute("y", y);
    rect.setAttribute("rx", 4);
    rect.setAttribute("ry", 4);
    rect.setAttribute("width", boxWidth);
    rect.setAttribute("height", boxWidth);
    rect.setAttribute("fill", button_color);
    rect.setAttribute("stroke", border_color);
    rect.setAttribute("stroke-width", "1px");
    rect.setAttribute("cursor", "pointer");
    rect.setAttribute("onclick", "speed_select.boxSelected(this)");
    
    label.setAttribute("x", x + boxWidth/8);
    label.setAttribute("y", y-4);
    label.setAttribute("font-size", "10px");
    label.setAttribute("font-family", "Helvetica");
    label.setAttribute("font-weight", "bold");
    label.setAttribute("fill", "#DDDDDD");
    var textNode = document.createTextNode(text);
    label.appendChild(textNode);
    
    group.appendChild(rect);
    group.appendChild(label);
    
    the_evt_target.appendChild(group);
    return group;
}

function AlgorithmInfoButton() {
    this.group = document.createElementNS(svgNS, "g");
    this.text = document.createElementNS(svgNS, "text");
    this.rect = document.createElementNS(svgNS, "rect");
    this.group.setAttribute("id", "AlgoButtonGroup");
    this.text.setAttribute("id", "AlgoButtonText");
    this.rect.setAttribute("id", "AlgoButtonRect");
    this.group.setAttribute("onmousedown", "ShowAlgoInfo(evt)");

    this.rect.setAttribute("width", 200);
    this.rect.setAttribute("height", 30);
    this.rect.setAttribute("fill", "url(#algo_button_lg)");
    this.rect.setAttribute("stroke", "#078600");
    this.rect.setAttribute("stroke-width", "1px");
    this.rect.setAttribute("rx", 5);
    this.rect.setAttribute("ry", 5);

    this.text.setAttribute("font-family", "Helvetica");
    this.text.setAttribute("fill", "#334433");
    this.text.appendChild(document.createTextNode("Show Algorithm Info!"));

    this.group.appendChild(this.rect);
    this.group.appendChild(this.text);
    the_evt_target.appendChild(this.group);
    setTranslate(this.text, (200 - this.text.getBBox().width)/2, this.text.getBBox().height + (30 - this.text.getBBox().height)/2 - 5);    
}



/* Creates the option menu, opened by clicking the cog.  Adds everything in menu_items to the menu.
 the menu_items parameter is a list of Functions that return an object, with an attribute 'group' containing the g-element. to be added to the menu.  
 the items in menu_items must already have been appended to the document.
*/
function OptionMenu(id, height, width, menu_items) {
    OptionMenu.prototype.translate_dropdown = OD_translate_dropdown;
    this.height = height;
    this.width = width;
    this.x_trans = null;
    this.y_trans = null;
    this.menu_visible = false;
    this.menu_height = 0;
    
    //The g-element containing all other pieces
    this.dropdown = null;

    //Cog image that pops the menu open/closed 
    this.cog = null; 
    
    this.dropdown = document.createElementNS(svgNS, 'g');
    this.dropdown.setAttribute("id", id);
    the_evt_target.appendChild(this.dropdown);

    this.cog = document.createElementNS(svgNS, "image");
    this.cog.setAttribute("id", "dropdown_cog");
    this.cog.setAttributeNS('http://www.w3.org/1999/xlink','href', "./img/cog.png");
    this.cog.setAttribute('width', (this.width*2/3 + this.width/12)*2);
    this.cog.setAttribute('height', height*1.5);
    this.cog.setAttribute("cursor", "pointer");
    this.cog.setAttribute("onmouseover", "OD_mouseover(evt)");
    this.cog.setAttribute("onmouseout", "OD_mouseout(evt)");
    this.cog.setAttribute("onmousedown", "OD_mouseclick(evt)");
    the_evt_target.appendChild(this.cog);

    //Array of items to be displayed in the menu
    this.menu_items = menu_items;
    //g-element containing the actual dropdown menu
    this.menu = new DrawnMenuItems(this.menu_items);
    this.dropdown.appendChild(this.menu.menu);

    function DrawnMenuItems(constructors) {
        // Build the menu_items
        this.menu_items = new Array();
        for (var i in constructors) {
            this.menu_items.push(construct(constructors[i]['function'], constructors[i]['args']));
            if (constructors[i]['function'] === SpeedSelector) {
                speed_select = this.menu_items[this.menu_items.length-1];
            }
        }
        
        // Figure out what the widest menu item is.  Make all menu item bounding boxes that big, with centered menu items underneath an item label
        this.width = 0;
        this.height = 0;
        for (var i in this.menu_items) {
            var bbox = this.menu_items[i].group.getBBox();
            this.height += bbox.height;
            if (bbox.width > this.width) {
                this.width = bbox.width;
            }
        }
        this.height += 15*(this.menu_items.length);     // Add the 15 for menu_items due to separation in llc
        this.width += 20;

        this.menu = document.createElementNS(svgNS, 'g');
        this.menu_rect = document.createElementNS(svgNS, 'rect');
        this.menu_rect.setAttribute("height", this.height);
        this.menu_rect.setAttribute("width", this.width);
        this.menu_rect.setAttribute("rx", 4);
        this.menu_rect.setAttribute("ry", 4);
        this.menu_rect.setAttribute("fill", "url(#control_box_lg)");     // Change this to a dark gradient
        this.menu.appendChild(this.menu_rect);

        this.llc = new LinearLayoutComponent(5, 0, "option_menu_llc", "vertical");
        for (var i in this.menu_items) {
            this.llc.insertComponent(this.menu_items[i].group.getAttribute("id"), i);
        }

        // Translate the elements appropriately
        var last = 0;
        for (var i in this.menu_items) {
            var offset = last*i*10 - 10;
            if (last === 0)
                offset += 10;

            var y_trans = getTranslate(this.menu_items[i].group.getAttribute("transform"))[1];
            setTranslate(this.menu_items[i].group, (this.width - this.menu_items[i].group.getBBox().width)/2, y_trans + offset);
            last ++;
        }

        setTranslate(this.llc.group, 0, 20);
        this.menu.appendChild(this.llc.group);
        this.menu.setAttribute("visibility", "hidden");
    }

    function construct(constructor, args) {
        function F() {
            return constructor.apply(this, args);
        }
        F.prototype = constructor.prototype;
        return new F();
    }
}

function OD_translate_dropdown(dropdown) {
    var bbox = horiz_layout[1].group.getBBox();
    var translate = getTranslate(horiz_layout[1].group.getAttribute("transform"));
    console.log(horiz_layout[1].group.getAttribute("transform"));
    console.log(translate[1]);
    console.log(horiz_layout[1].group);
    console.log(horiz_layout[1].group.parentNode);
    setTranslate(this.dropdown, viewbox_x - this.dropdown.getBBox().width*1.5, translate[1] - this.dropdown.getBBox().height*.5 - 25);
}

//Positions the option dropdown at the top right of the screen
function OD_position_dropdown() {
    this.y_trans = 10;
    //var x_trans = right_vert_layout.group.getBBox().x + right_vert_layout.group.getBBox().width;
    this.x_trans = (browser_width - 50)/screen_ctm.a;
    var graph = document.getElementById(init_graphs[0].getAttribute("id"));
    var translation1 = getTranslate(right_vert_layout.group.getAttribute("transform"));
    var translation2 = getTranslate(vert_layout.group.getAttribute("transform"));
    var translation3 = getTranslate(graph.getAttribute("transform"));
    
    this.x_trans = translation1[0] + translation2[0] + translation3[0] + graph.getBBox().width;
    setTranslate(this.dropdown, this.x_trans, this.y_trans);
}

//Changes the appearance of the dropdown when the mouse is over it
function OD_mouseover(evt) {
    option_menu.cog.setAttribute("opacity", .8);

}

//reverses the change in appearance of mouseover, and closes dropdown menu
function OD_mouseout(evt) {
    option_menu.cog.setAttribute("opacity", 1);
}

//Pops open the dropdown menu
function OD_mouseclick(evt) {
    if (option_menu.menu_visible === false) {
        option_menu.menu.menu.setAttribute('visibility', 'visible');
        option_menu.menu_visible = true;
    } else {
        option_menu.menu.menu.setAttribute('visibility', 'hidden');
        option_menu.menu_visible = false;
    }
}

/**
*
*
*
* Animation control functions
*
*
*/
//Starts animation loop.  If called more than once, resets display and begins loop
function StartAnimation(evt){
    if(evt.target.getAttribute("id") == "start_button"){
        if(state != null){ //Graph must be refreshed
            jumpToStep(step);
        }

        // If previous animation completed, then reset elements to beginning state
        // Don't reset when the step is not 0 though(user can move playback bar then start animation)
        if (state == "stopped" && step == 0) {
            setGraphState(graph_states[0]);
        }

        // Reposition scaler
        for (var x in init_graphs) {
            var graph = the_evt_target.getElementById(init_graphs[x].getAttribute("id"));
            repositionScaler(graph.getBBox().x, graph.getBBox().y);
        }   
    
        state = "running";
        action_panel.activateButton("stop_button", "StopAnimation(evt)");
        action_panel.activateButton("continue_button", "ContinueAnimation(evt)");
        action_panel.activateButton("step_button", "StepAnimation(evt)");
        action_panel.deactivateButton("start_button");
        //Begin animation loop
        AnimateLoop();
    }
}


//Loop of animation.  Performs actions in animation array at specified intervals
function AnimateLoop(){
    
    //Without this block, edges/vertices may be black
    //on the fastest speed.  Comment this out to verify
    if (blinking) {
        setTimeout(AnimateLoop, 1);
        return;
    }
    if (state === "stopped" || state === 'waiting') {
        setTimeout(AnimateLoop, 1);
        return;
    }
    if (movie_slider.thumb_active === true || scaler.scaler_active === true) {
        setTimeout(AnimateLoop, 1);
        return;
    }
    
    //Do next command
    //Special case for SetAllVertices Color
    if(animation[step][1] == SetAllVerticesColor && animation[step].length > 3){
        var vertexArray = new Array();
        for (var i = 3; i < animation[step].length; i++){
            vertexArray[i-3] = animation[step][i];
        }
        animation[step][1](animation[step][2],vertexArray);
    }else{
        animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
    }       
    step = step + 1;
    time = time + animation[step][0];
    
    //Realign components
    document.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
    document.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
    
    //Check if steps remain
    if(step < animation.length) { //If steps remain
        Refresh_MovieSlider(step, time);
        
        if(animation[step-1][1] == ShowActive && ( document.getElementById(code.line_llc.group.getAttribute("id") + "_bp" + animation[step-1][2].split("_")[1] + "_act") != null 
                || step_pressed) ){ //If the line was a show_active and the line is a breakpoint or the step button was pressed, wait
                
                state = "waiting";
                clearTimeout(timer);
                //If waiting because step pressed, then step animation
                if (step_pressed) {
                    step_pressed = false;
                    StepAnimation(step_evt);
                } else {
                    step_pressed = false;
                }
        }else{
            //Otherwise, execute the next command
            var duration = animation[step][0] * timeout;
            timer = setTimeout(AnimateLoop, duration);
        }
        
    }else{  //If no steps left, stop
        state = "stopped";
        action_panel.activateButton("start_button", "StartAnimation(evt)");
        action_panel.deactivateButton("continue_button");
        action_panel.deactivateButton("stop_button");
        action_panel.deactivateButton("step_button");
        step = 0;
        code.removeHighlight(current_line-1);
                current_line = 0;
    }
    
}


//Resumes execution of animation loop if paused by pressing step button
function ContinueAnimation(evt){
    if(evt.target.getAttribute("id") == "continue_button"){
        if(state == "waiting"){
            state = "running";
            continue_pressed = false;
            AnimateLoop();
        }else{
            continue_pressed = true;
            continue_evt = evt;
        }
    }
}


//Stops execution of animation loop and plays next animation on press of step button
function StepAnimation(evt){
    if(state == "running"){
        step_evt = evt;
        step_pressed = true;
        return;
    }

    
    if(evt.target.getAttribute("id") == "step_button" || evt.target.getAttribute("id") == "start_button"){ //see StartAnimation to see why start button is here                
                if(blinking){
                    if(state == "stepping"){
                        setTimeout(StepAnimation,1, evt);
                    }
                        return; //prevent buggy behavior
                }
        state = "stepping";

        
        if(animation[step][1] != ShowActive && step < animation.length){
            if(animation[step][1] == SetAllVerticesColor && animation[step].length > 3){
                var vertexArray = new Array();
                for (var i = 3; i < animation[step].length; i++){
                    vertexArray[i-3] = animation[step][i];
                }
                animation[step][1](animation[step][2],vertexArray);
            }else{
                animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
            }       
            step = step + 1;
            time = time + animation[step][0];
            Refresh_MovieSlider(step, time);
            
            if(blinking){
                        setTimeout(StepAnimation,1, evt);
                return;
            }
            document.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
            document.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
            setTimeout(StepAnimation,1,evt);
            return;
        }
        
        
        if(step < animation.length){
            if(animation[step][1] == SetAllVerticesColor && animation[step].length > 3){
                var vertexArray = new Array();
                for (var i = 3; i < animation[step].length; i++){
                    vertexArray[i-3] = animation[step][i];
                }
                    animation[step][1](animation[step][2],vertexArray);
            }else{
                animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
            }
            step = step + 1;
            time = time + animation[step][0];
            Refresh_MovieSlider(step, time);
            
            document.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
            document.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
            state = "waiting";
            if(continue_pressed){
                continue_pressed = false;
                ContinueAnimation(continue_evt);
            }
        }else{
                    state = "stopped";
                    action_panel.activateButton("start_button", "StartAnimation(evt)");
                    action_panel.deactivateButton("continue_button");
                    action_panel.deactivateButton("stop_button");
                    action_panel.deactivateButton("step_button");
                    step = 0;
                    code.removeHighlight(current_line-1);
                    current_line = 0;
                }
    }
}


//Stops animation and clears code highlights.  To resume animation, it must be restarted
function StopAnimation(evt){
    
    clearTimeout(timer);
    state = "stopped";
    action_panel.activateButton("start_button", "StartAnimation(evt)");
    action_panel.deactivateButton("continue_button");
    action_panel.deactivateButton("stop_button");
    action_panel.deactivateButton("step_button");
    step = 0;
    time = 0;
    code.removeHighlight(current_line-1);
    current_line = 0;
    Refresh_MovieSlider(step, time);
    setGraphState(graph_states[0]);

    // Reposition scaler
    for (var x in init_graphs) {
        var graph = the_evt_target.getElementById(init_graphs[x].getAttribute("id"));
        repositionScaler(graph.getBBox().x, graph.getBBox().y);
    }
    
    //StopAnimation only ever called from stop button, or at end of fillGraphStates
    /*if(evt.target.getAttribute("id") == "stop_button"){
        clearTimeout(timer);
        state = "stopped";
        action_panel.activateButton("start_button", "StartAnimation(evt)");
        action_panel.deactivateButton("continue_button");
        action_panel.deactivateButton("stop_button");
        action_panel.deactivateButton("step_button");
        step = 0;
        code.removeHighlight(current_line-1);
                current_line = 0;
    }*/
}


//Inserts a breakpoint by creating a grey highlight
function SetBreakpoint(evt){            
    var line = evt.target;
    
    if(line.nodeName == "tspan"){
        line = line.parentNode;
    }

    if(line.nodeName == "path"){
        var id = "";
        if(line.getAttribute("id").indexOf("_bp") != -1){
            var target_id = evt.target.getAttribute("id");
            id = "l_" + target_id.substring(target_id.indexOf("_") + "_bp".length);
        }else if(line.getAttribute("id").indexOf("_hl") != -1){
            id = "l_" + target_id.substring(target_id.indexOf("_") + "_hl".length);
            line.setAttribute("cursor", "default");
            line.setAttribute("onclick", "");
        }else {
            return;
        }

        line = document.getElementById(id);
    }

    //put breakpoint functionality on highligt if it is over highlighted text
    var hl_num = line.getAttribute("id").split("_")[1];
    var hl = document.getElementById("code_hl" + hl_num);
    if(hl != null){
        hl.setAttribute("cursor", "pointer");
        hl.setAttribute("onclick", "RemoveBreakpoint(evt)");
    }
    
    var htb_bbox = code.line_llc.group.getBBox();
    var line_bbox = line.getBBox();
    var line_translation = getTranslate(line.getAttribute("transform"));

    var dx = line.getAttribute("dx");
    var dy = line.getAttribute("dy");
    if(dx == null){
        dx = 0;
    }else{
            dx = parseFloat(dx);
    }
    if(dy == null){
            dy = 0;
    }else{
            dy = parseFloat(dy);
    }
    
    var indicator = the_evt_target.getElementById(code.line_llc.group.getAttribute("id") + "_bp" + line.getAttribute("id").split("_")[1]);
    var new_id = indicator.getAttribute("id") + "_act";
    indicator.setAttribute("id", new_id);
    indicator.setAttribute("opacity", 1);
    indicator.setAttribute("onclick", "RemoveBreakpoint(evt)");
    line.setAttribute("onclick", "RemoveBreakpoint(evt)");
}


// Add transparent breakpoints to codebox to indicate the breakpoint capability
function AddBreakpoints(code) {
    var lines = code.line_llc.group.childNodes;
    for (l in lines) {
        var line = lines[l];
        if(line.nodeName == "tspan"){
            line = line.parentNode;
        }
        if (line.nodeName != "text")
            continue;

        var line_bbox = line.getBBox();
        var line_translation = getTranslate(line.getAttribute("transform"));

        var dx = line.getAttribute("dx");
        var dy = line.getAttribute("dy");
        if(dx == null){
            dx = 0;
        }else{
                dx = parseFloat(dx);
        }
        if(dy == null){
                dy = 0;
        }else{
                dy = parseFloat(dy);
        }

        var text = document.createElementNS(svgNS, "text");
        text.appendChild(document.createTextNode(++last_line));

        var y_start = line_bbox.y + line_translation[1] - code.line_llc.v_padding - dy + line_bbox.height/4;
        var x_start = code.line_llc.group.getBBox().x + 8;
        var indicator = document.createElementNS(svgNS, "path");
        indicator.setAttribute("d", String("M" + x_start + " " + y_start + " L" + (x_start+8) + " " + y_start + " L" + (x_start+12) + " " + (y_start+4) + " L" + (x_start+8) + " " + (y_start+8) + " L" + x_start + " " + (y_start+8) + " L" + x_start + " " + y_start + " Z"));
        indicator.setAttribute("stroke", "blue");
        indicator.setAttribute("fill", "blue");
        indicator.setAttribute("id", code.line_llc.group.getAttribute("id") + "_bp" + line.getAttribute("id").split("_")[1]);
        indicator.setAttribute("transform", "translate(" + x_offset + " " + y_offset + ")");
        indicator.setAttribute("onclick", "SetBreakpoint(evt)");
        indicator.setAttribute("cursor", "pointer");
        indicator.setAttribute("opacity", .15);
        text.setAttribute("x", x_start - 24);
        text.setAttribute("y", y_start);
        text.setAttribute("font-family", "Courier New");
        text.setAttribute("font-size", 14.0);
        text.setAttribute("font-style", "normal");
        setTranslate(text, x_offset, y_offset + line_bbox.height/2);
        code.highlight_group.parentNode.appendChild(text);
        code.highlight_group.parentNode.appendChild(indicator);
    }
}


//Removes a highlight by removing a grey highlight
function RemoveBreakpoint(evt){
    var line = evt.target;
    if(line.nodeName == "path"){
        var id = "";
        if(line.getAttribute("id").indexOf("_bp") != -1){
            var target_id = evt.target.getAttribute("id");
            evt.target.setAttribute("onclick", "SetBreakpoint(evt)");
            id = "l_" + target_id.substring(target_id.indexOf("_") + "_bp".length, target_id.length-4);
        }else if(line.getAttribute("id").indexOf("_hl") != -1){
            id = "l_" + target_id.substring(target_id.indexOf("_") + "_hl".length);
            line.setAttribute("cursor", "default");
            line.setAttribute("onclick", "");
        }else {
            return;
        }
        line = document.getElementById(id);
    }
    
    if(line.nodeName == "tspan"){
        line = line.parentNode;
    }
    
    if(line.nodeName == "text"){
        var background = document.getElementById(code.line_llc.group.getAttribute("id") + "_bp" + line.getAttribute("id").split("_")[1] + "_act");
        if(background != null) {
            background.setAttribute("opacity", .15);
            var new_id = background.getAttribute("id");
            new_id = new_id.substring(0, new_id.length-4);
            background.setAttribute("id", new_id);
            line.setAttribute("onclick", "SetBreakpoint(evt)");
        }   
    }
}


/**
*
*
*
* Graph animation functions
*
*
*/
//Sets color of vertex with id given by v to specified color
function SetVertexColor(v, color) {
    element = document.getElementById(v);
    element.setAttribute("fill", color);
}


function AddToolTip(edge_id, graph) {
    var edge = the_evt_target.getElementById(edge_id);
    edge.setAttribute("onmouseover", "EdgeInfo_mouseover(evt)");
    edge.setAttribute("cursor", "pointer");
    edge.setAttribute("onmouseout", "EdgeInfo_mouseout(evt)");
    var tt = new ToolTip(edge, "#AABAAA", graph);
    AddToolTipArrowhead(edge_id);
}


// Pass an edge_id.  If an arrowhead is associated with that edge_id then the onmouseover is set to display the tooltip
function AddToolTipArrowhead(edge_id) {
    var arrowhead = the_evt_target.getElementById("ea" + edge_id);
    if (arrowhead) {
        arrowhead.setAttribute("onmouseover", "EdgeInfo_mouseover(evt)");
        arrowhead.setAttribute("cursor", "pointer");
        arrowhead.setAttribute("onmouseout", "EdgeInfo_mouseout(evt)");
    }
}


function removeToolTip(edge_id) {
    var edge = the_evt_target.getElementById(edge_id + "_tt");
    edge.parentNode.removeChild(edge);
}



// Change this name
function AddToolTips() {
    for (var e in edges) {
        for (var i in edges[e]) {
            var edge_id = edges[e][i].getAttribute("id");
            var edge = the_evt_target.getElementById(edge_id);
            var graph_id = edge_id.split("_")[0];
            var graph = the_evt_target.getElementById(graph_id);
            edge.setAttribute("onmouseover", "EdgeInfo_mouseover(evt)");
            edge.setAttribute("cursor", "pointer");
            edge.setAttribute("onmouseout", "EdgeInfo_mouseout(evt)");
            var tt = new ToolTip(edge, "#AABAAA", graph);
            AddToolTipArrowhead(edge_id);
        }
    }
}


// Searches through the first 200 animations for the first set of UpdateEdgeInfo and UpdateGraphInfo commands and applies them
// If it doesn't find them, it does nothing
function loadInitialInfo() {
    // UpdateEdgeInfo commands occur in blocks, so after an updateedgeinfo command is seen
    // and then another command is seen, we know we are done
    // UpdateGraphInfo commands are only seen once, in which case we are done

    var update_edge_seen = 0;   // Set to 1 when command is seen, set to 2 when another command is seen afterwards
    var update_graph_seen = 0;  // Set to 2 when all present graphs have been info'ed.  If two graphs, set to 1 when only 1 has been initialized
    
    for (var i=0; i<Math.min(200, animation.length); i++) {
        var anim_cmd = animation[i][1];
        if (update_edge_seen === 2 && update_graph_seen === 1) 
            return;

        if (update_edge_seen !== 2 && anim_cmd === UpdateEdgeInfo) {
            UpdateEdgeInfo(animation[i][2], animation[i][3]);

            if (update_edge_seen === 0)
                update_edge_seen = 1;
        } else if (update_graph_seen !== 2 && anim_cmd === UpdateGraphInfo) {
            UpdateGraphInfo(animation[i][2], animation[i][3]);

            if (!two_graph)
                update_graph_seen = 2;
            else if (update_graph_seen === 1) 
                update_graph_seen = 2;
            else
                update_graph_seen = 1;

            if (update_edge_seen === 1) 
                update_edge_seen = 2;
        } else {
            if (update_edge_seen === 1)
                update_edge_seen = 2;
        }
    }
}


function resetToolTips() {
    for (var e in edges) {
        for (var i in edges[e]) {
            var tt_text = the_evt_target.getElementById(edges[e][i].getAttribute("id") + "_tt_text");
            tt_text.removeChild(tt_text.firstChild);
        }
    }
}


function ToolTip(edge, color, graph) {
    /* Constructor function for tooltips.  It creates a tooltip for the edge with the given color.  
    *  If there is an arrowhead associated with the edge then the arrowhead is also mapped to 
    *  display the tooltip.
    */
    this.tt_g = document.createElementNS(svgNS, "g");
    this.tt_rect = document.createElementNS(svgNS, "rect");
    this.tt_text = document.createElementNS(svgNS, "text");

    this.tt_g.setAttribute("id", edge.getAttribute("id") + "_tt");

    var trans = getTranslate(graph.getAttribute("transform"));
    var x1 = parseInt(edge.getAttribute("x1"), 10);
    var x2 = parseInt(edge.getAttribute("x2"), 10);    
    var y1 = parseInt(edge.getAttribute("y1"), 10);
    var y2 = parseInt(edge.getAttribute("y2"), 10);
    var x_val = (x1 + x2)/2 - 20 + trans[0];
    var y_val = (y1 + y2)/2 - 10 + trans[1];

    var textnode = document.createTextNode("Start animation to see edge information.");
    this.tt_text.appendChild(textnode);
    this.tt_text.setAttribute("text-anchor", "middle");
    this.tt_text.setAttribute("id", edge.getAttribute("id") + "_tt_text");
    this.tt_text.setAttribute("fill", "#334433");
    this.tt_text.setAttribute("font-family", "Helvetica");
    this.tt_text.setAttribute("x", x_val + 50);     // This doesn't do anything
    this.tt_text.setAttribute("y", y_val + 25);     // This doesn't do anything
    this.tt_text.setAttribute("opacity", .9);

    this.tt_g.appendChild(this.tt_text);
    edge.parentNode.parentNode.appendChild(this.tt_g);

    this.tt_rect.setAttribute("width", this.tt_text.getBBox().width + tt_padding.x);
    this.tt_rect.setAttribute("height", this.tt_text.getBBox().height + tt_padding.y);
    this.tt_rect.setAttribute("id", edge.getAttribute("id") + "_tt_rect");
    this.tt_rect.setAttribute("x", this.tt_text.getBBox().x);
    this.tt_rect.setAttribute("y", this.tt_text.getBBox().y);
    this.tt_rect.setAttribute("opacity", .7);
    this.tt_rect.setAttribute("fill", color);
    this.tt_rect.setAttribute("stroke", "#335533");
    this.tt_rect.setAttribute("stroke-width", "5px");
    this.tt_rect.setAttribute("rx", "5");
    this.tt_rect.setAttribute("ry", "5");
    
    this.tt_g.setAttribute("visibility", "hidden");
    setTranslate(this.tt_g, trans[0], trans[1]);    // This is responsible for the tooltip positioning

    this.tt_g.insertBefore(this.tt_rect, this.tt_text);
}


function UpdateEdgeInfo(edge, info) {
    var text_element = document.getElementById(edge + "_tt_text");
    if (text_element)
        text_element.firstChild.nodeValue = info;
}


function EdgeInfo_mouseover(evt) {
    var id = evt.target.getAttribute("id");
    // Check if the evt.target is an arrowhead and strip the beginning ea if necessary
    if (id.indexOf("ea") === 0) 
        id = id.substring(2);

    var tt = the_evt_target.getElementById(id + "_tt");
    tt.setAttribute("visibility", "visible");
    active_tt.tt = tt;
    active_tt.rect = the_evt_target.getElementById(id + "_tt_rect");
    active_tt.text = the_evt_target.getElementById(id + "_tt_text");
}


function EdgeInfo_mouseout(evt) {
    var id = evt.target.getAttribute("id");
    // Check if the evt.target is an arrowhead and strip beginning ea if necessary
    if (id.indexOf("ea") === 0)
        id = id.substring(2);

    var tt = the_evt_target.getElementById(id + "_tt");
    tt.setAttribute("visibility", "hidden");
    active_tt.tt = null;
    active_tt.rect = null;
    active_tt.text = null;
}


// Has the tooltip follow the mouse
function positionTooltip(evt) {
    if (active_tt.tt === null) {
        return;
    }

    // If the evt.target is an arrowhead replace with an edge
    var target = evt.target;
    if (target.getAttribute("id").indexOf("ea") === 0) {
        target = the_evt_target.getElementById(target.getAttribute("id").substring(2));
    }

    var cursor_point = cursorPoint(evt, evt.target);
    active_tt.text.setAttribute("y", cursor_point.y*g_scale_factor.y + 40);
    active_tt.text.setAttribute("x", cursor_point.x*g_scale_factor.x - active_tt.text.getBBox().width/2 - tt_padding.x/2);
    active_tt.rect.setAttribute("width", active_tt.text.getBBox().width + tt_padding.x);
    active_tt.rect.setAttribute("height", active_tt.text.getBBox().height + tt_padding.y);
    active_tt.rect.setAttribute("x", active_tt.text.getBBox().x - tt_padding.x/2);
    active_tt.rect.setAttribute("y", active_tt.text.getBBox().y - tt_padding.y/2);

    /* Don't think this is needed since tooltips are drawn to the left of the cursor */
    // Check if the tooltip goes off the screen
    var diff = active_tt.text.getBBox().x*g_scale_factor.x + active_tt.text.getBBox().width - viewbox_x;
    if (diff > 0) {
        active_tt.text.setAttribute("x", active_tt.text.getAttribute("x") - diff/g_scale_factor.x);
        active_tt.rect.setAttribute("x", active_tt.rect.getAttribute("x") - diff/g_scale_factor.x);
    }
}


// Positions graph info at bottom left of graph.  Works for both graphs in 2-graph situation
function positionGraphInfo() {
    for (var x in init_graphs) {
        var graph = the_evt_target.getElementById(init_graphs[x].getAttribute("id"));
        var info = the_evt_target.getElementById(init_graphs[x].getAttribute("id") + "_()_info");
        setTranslate(info, graph.getBBox().x + G_INFO_POS["horiz_offset"], graph.getBBox().y + graph.getBBox().height + G_INFO_POS["height"]);
    }
}


function UpdateGraphInfo(graph_id, info) {

    // If UpdateGraphInfo was called with the actual graph id then append the "_()"
    if (graph_id.charAt(graph_id.length-1) !== ')')
        graph_id = graph_id + "_()";

    var text = the_evt_target.getElementById(graph_id + "_info");
    
    if (text.firstChild)
        text.removeChild(text.firstChild);
    var new_node = document.createTextNode(info);
    text.appendChild(new_node);
}



//Colors edge with id given by e
function SetEdgeColor(e, color) {
    // NOTE: Gato signature SetEdgeColor(v, w, color)
    var element = document.getElementById(e);
    if (element == null) {
        e = switch_edge_vertices(e);
        element = document.getElementById(e);
    }
    element.setAttribute("stroke", color);
    //added changes to color of arrowheads
    element = document.getElementById(e_arrow_id + e);
    if(element != null){
        element.setAttribute("fill", color);
    }
}


//Takes in an edge and switches the vertices to accomodate for directed graphs.
//Usual form of edge is g1_(1, 2) or g2_(2, 1) etc.
function switch_edge_vertices(e){
    var prefix = e.split('(')[0];
    var split = e.split(',');
    var losplit = split[0].split('(');
    var v1 = losplit[1].substring(0, losplit[1].length);
    //var v1 = split[0].split[0].length-1);
    var v2 = split[1].substring(1, split[1].length-1);
    var new_e = prefix + "(" + v2 + ", " + v1 + ")";
    return new_e;
}


//Sets color of all vertices of a given graph to a given color
//If vertices != null, then only color the set of vertices specified by vertices
function SetAllVerticesColor(graph_id_and_color, vertices) {

    var graph_id = graph_id_and_color.split("_")[0];
    var color = graph_id_and_color.split("_")[1];
    var children = document.getElementById(graph_id).childNodes;

    if(vertices != null){
        for (var i = 0; i < children.length; i++){
        for(j = 0; j < vertices.length; j++){
            if(children.item(i).nodeName == "circle" && children.item(i).getAttribute("id") == graph_id + "_" + vertices[j]){
                children.item(i).setAttribute("fill", color);
                break;
            }
        }
    }
    }else{
        for (var i = 0; i < children.length; i++){
        if(children.item(i).nodeName == "circle"){
            children.item(i).setAttribute("fill", color);
        }
    }
    }
    
}


// Sets all the edges of one of the graphs to color given.  sample param: "g1_#dd3333"
function SetAllEdgesColor(graphColor) {
    var graph = graphColor.substring(0, 2);
    var edge_index = parseInt(graph.substring(1,2)) - 1;
    graphColor = graphColor.substring(3);

    for (var i=0; i<edges[edge_index].length; i++) {
        var id = edges[edge_index][i].getAttribute("id");
        if (id.substring(0, 2) !== graph)
            continue;
        var element = document.getElementById(id);
        element.setAttribute("stroke", graphColor);
        element = document.getElementById(e_arrow_id + id);
        if (element != null) {
            element.setAttribute("fill", graphColor);
        }
    }
}


//Vertex blinks between black and current color
function BlinkVertex(v, color) {
    // Return if doing the initial filling of graph states
    if (filling_states || switching_states || movie_slider.thumb_active)
        return;

    blinking = true;
    var element = document.getElementById(v);
    var blinkcolor = element.getAttribute("fill");
    var blinkcount = 3;
    element.setAttribute("fill", "black");
    setTimeout(function() {
        if (blinkcolor === 'black')
            console.log(v);
        VertexBlinker(element, blinkcolor, blinkcount);
    }, 3*timeout);
}

//Helper for BlinkVertex
function VertexBlinker(element, blinkcolor, blinkcount) {
    if (blinkcount %% 2 == 1) {
       element.setAttribute("fill", "black"); 
    } else {
       element.setAttribute("fill", blinkcolor); 
    }
    blinkcount = blinkcount - 1;
    if (blinkcount >= 0) {
       setTimeout(function() {
            VertexBlinker(element, blinkcolor, blinkcount)
        }, 3*timeout);
    } else {
        blinking = false;
    }
}


//Edge blinks between black and current color
function BlinkEdge(e, color){
    // Return if doing the initial filling of graph states
    if (filling_states || switching_states || movie_slider.thumb_active)
        return;

    blinking = true;
    var e_element = document.getElementById(e);
    var e_blinkcolor = e_element.getAttribute("stroke");
    var e_blinkcount = 3;
    e_element.setAttribute("stroke", "black");
    var element2 = document.getElementById(e_arrow_id + e);
    if(element2 != null){
        element2.setAttribute("fill", "black");
    }
    setTimeout(function() {
        EdgeBlinker(e_element, e_blinkcolor, e_blinkcount);
    }, 3*timeout);
    
}

//Helper for BlinkEdge
function EdgeBlinker(e_element, e_blinkcolor, e_blinkcount){
    var element2;
    if (e_blinkcount %% 2 == 1) {
       e_element.setAttribute("stroke", "black");
       element2 = document.getElementById(e_arrow_id + e_element.getAttribute("id"));
       if(element2 != null){
           element2.setAttribute("fill", "black");
       }
    } else {
       e_element.setAttribute("stroke", e_blinkcolor);
       element2 = document.getElementById(e_arrow_id + e_element.getAttribute("id"));
       if(element2 != null){
           element2.setAttribute("fill", e_blinkcolor);
       }
    }
    e_blinkcount = e_blinkcount - 1;
    if (e_blinkcount >= 0) {
       setTimeout(function() {
            EdgeBlinker(e_element);
        }, 3*timeout);
    } else {
        blinking = false;
    }
}


//Blink(self, list, color=None):
//Sets the frame width of a vertex
function SetVertexFrameWidth(v, val) {
    var element = document.getElementById(v);
    element.setAttribute("stroke-width", val);

    // Eliminate blur if increasing frame width, add back in if removing frame width
    if (val === "0")
        element.setAttribute("style", "filter:url(#dropshadow)");
    else 
        element.setAttribute("style", "");

    var graph = document.getElementById(v).parentNode;
    sizeGraphBBox(graph);
}


//Sets annotation of vertex v to annotation.  Annotation's color is specified
function SetVertexAnnotation(v, annotation, color) //removed 'self' parameter to because 'self' parameter was assigned value of v, v of annotation, and so on.
{
    element = document.getElementById(v);
    
    if(element != null){
        if(typeof color == "undefined")
        color = "black";        
        
    if(document.getElementById(v_ano_id + v) != null){
        ano = document.getElementById(v_ano_id + v);
        ano.parentNode.removeChild(ano);
    
    }
    
    var newano = document.createElementNS(svgNS,"text");
    x_pos = parseFloat(element.getAttribute("cx")) + parseFloat(element.getAttribute("r")) + 1;
    y_pos = parseFloat(element.getAttribute("cy")) + parseFloat(element.getAttribute("r")) + 1;
    newano.setAttribute("x", x_pos);
    newano.setAttribute("y", y_pos);
    newano.setAttribute("fill",color);
    newano.setAttribute("id", v_ano_id+v);
    newano.setAttribute("text-anchor","center");
    newano.setAttribute("font-size","14.0");
    newano.setAttribute("font-family","Helvetica");
    newano.setAttribute("font-style","normal");
    newano.setAttribute("font-weight","bold");
    newano.appendChild(document.createTextNode(annotation));
    element.parentNode.appendChild(newano);

    var graph = document.getElementById(v).parentNode;
    sizeGraphBBox(graph);
    }
}


//Line with specified id is highlighted.  Becomes current line of code.  Previous highlight is removed.
function ShowActive(line_id){
    for (var i = 0; i < code.line_llc.group.childNodes.length; i++){
        if(code.line_llc.group.childNodes.item(i).getAttribute("id") == line_id){
            code.removeHighlight(current_line-1);
            code.highlightLine(i);
            current_line = i+1;
            if(document.getElementById("code_bp" + current_line) != null){
                var hl = document.getElementById("code_hl" + current_line);
                hl.setAttribute("cursor", "pointer");
                hl.setAttribute("onclick", "RemoveBreakpoint(evt)");
            }
            break;
        }
    }
}


//Directed or undirected added to graph.
function AddEdge(edge_id){
    var graph_id = edge_id.split("_")[0];
    var vertices = edge_id.split("_")[1].match(/[^,\(\)\s]+/g);
    var v = document.getElementById(graph_id + "_" + vertices[0]);
    var w = document.getElementById(graph_id + "_" + vertices[1]);
    
    var vx = v.getAttribute("cx");
    var wx = w.getAttribute("cx");
    var vy = v.getAttribute("cy");
    var wy = w.getAttribute("cy");
    
    var parent_graph = document.getElementById(graph_id);
    
    if(v != null && w != null && document.getElementById(graph_id + "_(" + vertices[0] + ", " + vertices[1] + ")") == null){
        var arrowhead = null;
        var edge = null;
        
        if(parent_graph.getAttribute("type") == "directed"){
            var reverse_edge = document.getElementById(graph_id + "_(" + vertices[1] + ", " + vertices[0] + ")");
            if(reverse_edge != null){  //reverse edge exists.  Make this edge an arc.
                //Another directed edge.  Great... Change existing edge to arc and add new arc
                //Be sure to alter polylines as well.   
                var l = Math.sqrt(Math.pow((parseFloat(vx)-parseFloat(wx)),2) + Math.pow((parseFloat(vy)-parseFloat(wy)),2));
                
                if(l < 0.001)
                    l = 0.001;
                
                var c = (l - default_vertex_radius)/l - 0.001;
                var tmpX = parseFloat(vx) + c * (parseFloat(wx) - parseFloat(vx));
                var tmpY = parseFloat(vy) + c * (parseFloat(wy) - parseFloat(vy));
                
                
                var orthogonal = Orthogonal((parseFloat(wx)-parseFloat(vx)),(parseFloat(wy)-parseFloat(vy)));
                
                var mX = orthogonal[0];
                var mY = orthogonal[1];
                c = 1.5*default_vertex_radius + l/25;
                mX = parseFloat(vx) + .5 * (parseFloat(wx) - parseFloat(vx)) + c * mX
                mY = parseFloat(vy) + .5 * (parseFloat(wy) - parseFloat(vy)) + c * mY
                
                
                
                arrowhead = createArrowhead(mX, mY, wx, wy, 4.0, "ea" + edge_id);
                
                
                l = Math.sqrt(Math.pow(wx-mX,2) + Math.pow(wy-mY,2));
               
                if (l < .001)
                    l = .001;
                

                c = (l-2*default_vertex_radius)/l + .01;
                tmpX = mX + c*(wx - mX);
                tmpY = mY + c*(wy - mY);
                
                
                edge = document.createElementNS(svgNS,"path");
                edge.setAttribute("id", edge_id);
                edge.setAttribute("stroke", "#EEEEEE");
                edge.setAttribute("stroke-width", 4.0);
                edge.setAttribute("fill", "none");
                edge.setAttribute("d", "M " + vx +"," + vy +" Q "+ mX +"," + mY + " " + tmpX + "," + tmpY);
        
                parent_graph.insertBefore(edge, parent_graph.childNodes.item(0));
                if(arrowhead != null)
                    parent_graph.insertBefore(arrowhead, parent_graph.childNodes.item(1));
                    
                    
                if(reverse_edge.getAttribute("d") == null){
                    reverse_edge.parentNode.removeChild(document.getElementById("ea" + reverse_edge.getAttribute("id")));
                    reverse_edge.parentNode.removeChild(reverse_edge);
                    AddEdge(reverse_edge.getAttribute("id"));
                }
                document.getElementById(reverse_edge.getAttribute("id")).setAttribute("stroke", reverse_edge.getAttribute("stroke"));
                document.getElementById("ea" + reverse_edge.getAttribute("id")).setAttribute("fill", reverse_edge.getAttribute("stroke"));
            }else{  //No reverse edge.  Just make a straight line
                                edge = document.createElementNS(svgNS,"line");
                                edge.setAttribute("id", edge_id);
                                edge.setAttribute("stroke", "#EEEEEE");
                                edge.setAttribute("stroke-width", 4.0);
                edge.setAttribute("x1", vx);
                edge.setAttribute("y1", vy);

                var l = Math.sqrt(Math.pow((parseFloat(wx)-parseFloat(vx)),2) + Math.pow((parseFloat(wy)-parseFloat(vy)),2));
               
                if (l < .001)
                    l = .001;

                var c = (l-2*default_vertex_radius)/l + .01;
                var tmpX = parseFloat(vx) + c*(parseFloat(wx) - parseFloat(vx));
                var tmpY = parseFloat(vy) + c*(parseFloat(wy) - parseFloat(vy));
                                
                edge.setAttribute("x2", tmpX);
                edge.setAttribute("y2", tmpY);

                arrowhead = createArrowhead(vx, vy, wx, wy, 4.0, "ea" + edge_id);   
                
                parent_graph.insertBefore(edge, parent_graph.childNodes.item(0));
                if(arrowhead != null)
                    parent_graph.insertBefore(arrowhead, parent_graph.childNodes.item(1));
            }
        }else{ //Undirected edge
                        edge = document.createElementNS(svgNS,"line");
                    edge.setAttribute("id", edge_id);
                    edge.setAttribute("stroke", "#EEEEEE");
                    edge.setAttribute("stroke-width", 4.0);
            edge.setAttribute("x1", vx);
            edge.setAttribute("y1", vy);
            edge.setAttribute("x2", wx);
            edge.setAttribute("y2", wy);
            
            parent_graph.insertBefore(edge, parent_graph.childNodes.item(0));
            if(arrowhead != null)
                parent_graph.insertBefore(arrowhead, parent_graph.childNodes.item(1));
        }

        var graph = document.getElementById(edge_id).parentNode;
        sizeGraphBBox(graph);
    }
    AddToolTip(edge_id, parent_graph);
    fillEdgesArray();
}


//Deletes edge of corresponding id from graph
function DeleteEdge(edge_id){
    var edge =  document.getElementById(edge_id);
    if(edge != null){
        edge.parentNode.removeChild(edge);
    }
    var arrowhead = document.getElementById("ea" + edge_id);
    
    if(arrowhead != null){
        arrowhead.parentNode.removeChild(arrowhead);
    }

    removeToolTip(edge_id);

    var graph_id = edge_id.split("_")[0];
    var vertices = edge_id.split("_")[1].match(/[^,\(\)\s]+/g);
    var reverse_edge = document.getElementById(graph_id + "_(" + vertices[1] + ", " + vertices[0] + ")");
    if(reverse_edge != null){
            DeleteEdge(reverse_edge.getAttribute("id"));
            AddEdge(reverse_edge.getAttribute("id"));
            var new_edge = document.getElementById(reverse_edge.getAttribute("id"));
            new_edge.setAttribute("stroke", reverse_edge.getAttribute("stroke"));
            new_edge.setAttribute("stroke-width", reverse_edge.getAttribute("stroke-width"));
            var arrowhead = document.getElementById("ea" + new_edge.getAttribute("id"));
            if(arrowhead != null){
                arrowhead.setAttribute("fill", new_edge.getAttribute("stroke"));
            }
    }

    var graph = document.getElementById(graph_id);
    sizeGraphBBox(graph);
    fillEdgesArray();
}


//Adds vertex of into specified graph and coordinates in graph.  Optional id argument may be given.
function AddVertex(graph_and_coordinates, id){

    var graph = document.getElementById(graph_and_coordinates.split("_")[0]);
    var next_vertex = 1;
    while(true){
        if(document.getElementById(graph.getAttribute("id") + "_" + next_vertex) == null){
            break;
        }
        next_vertex++;
    }

    
    var coords = graph_and_coordinates.split("(")[1].match(/[\d\.]+/g);
    
    var new_vertex = document.createElementNS(svgNS,"circle");
    new_vertex.setAttribute("cx", coords[0]);
    new_vertex.setAttribute("cy", coords[1]);
    new_vertex.setAttribute("r", default_vertex_radius);
    new_vertex.setAttribute("fill", "#000099");
    new_vertex.setAttribute("stroke", "black");
    new_vertex.setAttribute("stroke-width", 0.0);

    if(id != null){
        new_vertex.setAttribute("id", graph.getAttribute("id") + "_" + id);
        if(document.getElementById(new_vertex.getAttribute("id")) != null)
            return;
    }else{
        new_vertex.setAttribute("id", graph.getAttribute("id") + "_" + next_vertex);
    }

    graph.appendChild(new_vertex);
    

    var new_label = document.createElementNS(svgNS,"text");
    new_label.setAttribute("x", coords[0]);
    new_label.setAttribute("y", parseFloat(coords[1]) + .33*parseFloat(new_vertex.getAttribute("r")));
    new_label.setAttribute("text-anchor", "middle");
    new_label.setAttribute("fill", "white");
    new_label.setAttribute("font-family", "Helvetica");
    new_label.setAttribute("font-size", 14.0);
    new_label.setAttribute("font-style", "normal");
    new_label.setAttribute("font-weight", "bold");
    new_label.setAttribute("id", "vl" + new_vertex.getAttribute("id"));

    if(id != null){
        new_label.appendChild(document.createTextNode(id));
    }else{
        new_label.appendChild(document.createTextNode(next_vertex + ""));
    }
    graph.appendChild(new_label);


        //resnap graph to fit   

    for(k = 0; k < vert_layout[1].group.childNodes.length; k++){
        vert_layout[1].resnapComponent(k);
    
        if(vert_layout[1].group.childNodes.item(x).nodeName == "g"){
            var graph = vert_layout[1].group.childNodes.item(k);
            sizeGraphBBox(graph);
            var translation1 = getTranslate(right_vert_layout.group.getAttribute("transform"));
            var translation2 = getTranslate(vert_layout.group.getAttribute("transform"));
            var translation3 = getTranslate(graph.getAttribute("transform"));
            setTranslate(rect, translation1[0] + translation2[0] + translation3[0], translation1[1] + translation2[1] + translation3[1]);
        }
    }
}


//function SetEdgeAnnotation(self,tail,head,annotation,color="black"):
//def UpdateVertexLabel(self, v, blink=1, color=None):
/**
*
*
*
* iPad functions
*
*
*
*/
//iPad-specific slider event handling
function TouchDrag_SSlider(evt){
    evt.preventDefault();
    Drag_SSlider(evt);
}


function TouchStart_SSlider(evt){
    evt.preventDefault();
    Click_SSlider(evt);
}


function TouchDeactivate_SSlider(evt){
    evt.preventDefault();
    Deactivate_SSlider(evt);
}


//iPad-specific graph translations
function TouchDrag_Graph(evt){
    if(evt.touches == undefined || evt.touches.length != 1)
        return;

    evt.preventDefault();
    TranslateGraph(evt);
}


function TouchStart_Graph(evt){
    if(evt.touches == undefined || evt.touches.length != 1)
        return;
    evt.preventDefault();
    translate_buffer = [evt.touches[0].clientX, evt.touches[0].clientY];
}


function TouchDeactivate_Graph(evt){
    if(evt.touches == undefined || evt.touches.length != 1)
        return;
    evt.preventDefault();
    translate_buffer = [];
}


function TranslateGraph(evt){
    var graph = evt.target;
    var graph_bg = null;
    if(graph.nodeName == "rect"){
        graph_bg = graph;
        graph = document.getElementById(graph.getAttribute("id").split("_")[0]);
    }else{
        graph = graph.parentNode;
        graph_bg = document.getElementById(graph.getAttribute("id") + "_bg");
    }
    
    var x = evt.clientX;
    if(x == undefined)
        x = evt.touches[0].clientX;
    var y = evt.clientX;
    if(y == undefined)
        y = evt.touches[0].clientY;
    
    var translation = getTranslate(graph.getAttribute("transform"));
    var bg_translation = getTranslate(graph_bg.getAttribute("transform"));
    setTranslate(graph, translation[0] + (x-translate_buffer[0]), translation[1] + (y - translate_buffer[1]));
    setTranslate(graph_bg, bg_translation[0] + (x-translate_buffer[0]), bg_translation[1] + (y - translate_buffer[1]));
    graph.setAttribute("transform_buffer", graph.getAttribute("transform"));
    graph_bg.setAttribute("transform_buffer", graph_bg.getAttribute("transform"));
    translate_buffer[0] = x;
    translate_buffer[1] = y;


    document.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
    document.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
}


//iPad-specific functions for rotating and scaling graphs
function GestureStart_TransformGraph(evt){      
    if(evt.touches != undefined)
        return;
    evt.preventDefault();
    
    var graph = evt.target;
    var graph_bg = null;
    if(graph.nodeName == "rect"){
        graph_bg = graph;
        graph = document.getElementById(graph.getAttribute("id").split("_")[0]);
    }else{
        graph = graph.parentNode;
        graph_bg = document.getElementById(graph.getAttribute("id") + "_bg");
    }
    
    
    if(graph.getAttribute("transform_buffer") == null){     
        graph.setAttribute("transform_buffer", graph.getAttribute("transform"));
        graph_bg.setAttribute("transform_buffer", graph_bg.getAttribute("transform"));
    }
    
}


function GestureChange_TransformGraph(evt){
    if(evt.touches != undefined)
        return;
    evt.preventDefault();
    
    var graph = evt.target;
    var graph_bg = null;
    if(graph.nodeName == "rect"){
        graph_bg = graph;
        graph = document.getElementById(graph.getAttribute("id").split("_")[0]);
    }else{
        graph = graph.parentNode;
        graph_bg = document.getElementById(graph.getAttribute("id") + "_bg");
    }

    TransformGraph(graph, graph_bg, evt);
}


function GestureEnd_TransformGraph(evt){
    if(evt.touches != undefined)
        return;
        
    evt.preventDefault();
    
    var graph = evt.target;
    var graph_bg = null;
    if(graph.nodeName == "rect"){
        graph_bg = graph;
        graph = document.getElementById(graph.getAttribute("id").split("_")[0]);
    }else{
        graph = graph.parentNode;
        graph_bg = document.getElementById(graph.getAttribute("id") + "_bg");
    }

    graph.setAttribute("transform_buffer", graph.getAttribute("transform"));
    graph_bg.setAttribute("transform_buffer", graph_bg.getAttribute("transform"));
}


function TransformGraph(graph, graph_bg, evt){
    var scale = evt.scale;
    
    var graph_scale = getScale(graph.getAttribute("transform_buffer"));
    var gbg_scale = getScale(graph_bg.getAttribute("transform_buffer"));
    var graph_scaling_factor = 1 - scale;
    var gbg_scaling_factor = 1 - scale;
    
    var gscf_width = graph_scaling_factor* graph.getBBox().width*graph_scale[0];
    var gscf_height = graph_scaling_factor* graph.getBBox().height*graph_scale[1];  
    var gbgscf_width = gbg_scaling_factor * graph_bg.getBBox().width*gbg_scale[0];
    var gbgscf_height = gbg_scaling_factor * graph_bg.getBBox().height*gbg_scale[1];
    
    setScale(graph, scale * graph_scale[0], scale * graph_scale[1]);
    setScale(graph_bg, scale * gbg_scale[0], scale * gbg_scale[1]);
    
    graph_translation = getTranslate(graph.getAttribute("transform_buffer"));
    gbg_translation = getTranslate(graph_bg.getAttribute("transform_buffer"));
    
    setTranslate(graph, graph_translation[0] + gscf_width/2, graph_translation[1] + gscf_height/2);
    setTranslate(graph_bg, gbg_translation[0] + gbgscf_width/2, gbg_translation[1] + gbgscf_height/2);
    
    document.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
    document.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
}


/*
//
// SCALING FUNCTIONS
//
//
*/
function Scaler(points, width) {
    this.triang_scaler = document.createElementNS(svgNS, "polygon");
    this.triang_scaler.setAttribute("id", "triangle_scaler");
    this.triang_scaler.setAttribute("points", points);
    this.triang_scaler.setAttribute("style", "stroke:#660000; fill:#cc3333");
    the_evt_target.appendChild(this.triang_scaler);

    var graph;
    if (two_graph)
        graph = the_evt_target.getElementById(init_graphs[1].getAttribute("id"));
    else 
        graph = the_evt_target.getElementById(init_graphs[0].getAttribute("id"));

    graph.appendChild(this.triang_scaler);

    // Property that controls whether the scaler will alter the graph or not
    this.scaler_active = false;    

    
    this.triang_scaler.setAttribute("cursor", "move");
    this.triang_scaler.setAttribute("onmousedown", "click_scaler(evt)");
    this.triang_scaler.setAttribute("onmouseup", "deactivate_scaler(evt)");
    this.triang_scaler.setAttribute("onmousemove", "drag_scaler(evt)");
}


// Repositions the scaler to match the 
function repositionScaler(x, y) {
    var scaler_x = x + MAX_GBBOX_WIDTH - 10;
    var scaler_y = y + MAX_GBBOX_HEIGHT - 10;
    var points_val = String(scaler_x) + "," + String(scaler_y) + " " + String(scaler_x-20) + "," + String(scaler_y) + " " + String(scaler_x) + "," + String(scaler_y-20);
    scaler.triang_scaler.setAttribute("points", points_val);
}


// Click-handler for scaler.  Sets scaler_active to true to enable scaling with drags,
// and sets mouse_start to the current cursor position
function click_scaler(evt) {
    scaler.scaler_active = true;
    var graph = document.getElementById(init_graphs[0].getAttribute("id"));
    scale_graph_width = graph.getBBox().width * g_scale_factor.x;
    mouse_start = cursorPoint(evt, null);
}


// Global-mouseup handler that deactivates scaler_active
function deactivate_scaler(evt) {
    if (scaler.scaler_active === false)
        return;
    
    scaler.scaler_active = false;
}

 
// Global-mousemove handler that calls scaleGraph with the current evt if scaler_active is True
function drag_scaler(evt) {
    if (scaler.scaler_active === false)
        return;
        
    var graph = document.getElementById(init_graphs[0].getAttribute("id"));
    var graph_bg = document.getElementById(graph.getAttribute("id") + "_bg");
    scaleGraph( graph, graph_bg, evt, false);
}


// Moves the second graph down in y direction to make room for the top graph scaling
function slide_down_bottom() {
    var graph_one = the_evt_target.getElementById(init_graphs[0].getAttribute("id"));
    var new_height = init_height_g1 * g_scale_factor.y;
    var diff = new_height - init_height_g1;

    var graph_two = the_evt_target.getElementById(init_graphs[1].getAttribute("id"));
    var trans = getTranslate(graph_two.getAttribute("transform"));
    setTranslate(graph_two, trans[0], init_transy_g2.graph + diff);

    // Move down the bounding box as well
    var g2_bg = the_evt_target.getElementById("g2_bg");
    var trans = getTranslate(g2_bg.getAttribute("transform"));
    setTranslate(g2_bg, trans[0], init_transy_g2.bg + diff);
}

 
 // Scales the graph and background.  If use_curr_sf is true then it uses the current
 // g_scale_factor, otherwise it computes one based on scaler position
function scaleGraph(graph, graph_bg, evt, use_curr_sf) {
    
    if (use_curr_sf) {
        setScale(graph, g_scale_factor.x, g_scale_factor.y);
        setScale(graph_bg, g_scale_factor.x, g_scale_factor.y);
        return;
    }

    // Factor the graph_width is multiplied by to get the actual width
    var width_factor = 1;
    if (max_scale_factor < 1)
        width_factor = max_scale_factor;
    
    var cursor_point = cursorPoint(evt);

    var graph_width = graph.getBBox().width * width_factor;
    var cursor_delta = cursor_point.x - mouse_start.x;
    if (cursor_delta === 0)
        return;

    var new_width = scale_graph_width + cursor_delta;
    var temp_scale_factor = new_width / graph_width;

    // If temp_scale_factor is too small then do not do the scaling
    if (temp_scale_factor < MIN_SCALE_FACTOR)
        return;
    
    g_scale_factor.x = temp_scale_factor * width_factor;
    g_scale_factor.y = temp_scale_factor * width_factor;

    //Limit scaling to the maximum scale_factor
    if (g_scale_factor.x > max_scale_factor) {
        g_scale_factor.x = max_scale_factor;
        g_scale_factor.y = max_scale_factor;
    }

    if (two_graph === true) 
            slide_down_bottom();
    
    for (var x in init_graphs) {
        var graph = the_evt_target.getElementById(init_graphs[x].getAttribute("id"));
        var graph_bg = the_evt_target.getElementById(graph_bgs[x]);
        setScale(graph, g_scale_factor.x, g_scale_factor.y);
        setScale(graph_bg, g_scale_factor.x, g_scale_factor.y);
    }
}

//Translate client coordinates to svg coordinates.  If given element then translates to coordinates
//in that elements coordinate system
function cursorPoint(evt, element){
    pt.x = evt.clientX; 
    pt.y = evt.clientY;
    if (element === null || element === undefined)
        return pt.matrixTransform(the_evt_target.getScreenCTM().inverse());
    else
        return pt.matrixTransform(element.getScreenCTM().inverse());
}

//This pushes the graph background too far to the left for some reason
function realignScaler(scaler_x, scaler_y){
    var tri_scaler = the_evt_target.getElementById("triangle_scaler");
    tri_scaler.setAttribute("points", String(scaler_x) + "," + String(scaler_y) + " " + String(scaler_x-20) + "," + String(scaler_y) + " " + String(scaler_x) + "," + String(scaler_y-20));
}

/*
//
//
// "MOVIE" PLAYBACK
//
//
//
*/

function GraphState(graph, step) {
    // An array tuple of (state, elements_present_at_that_time)
    this.state = buildStateArray(graph);
    
    // An array of tuples of the form (edge_id, edge_tooltip_text)
    this.edge_info = buildEdgeInfoArray();
    var info = the_evt_target.getElementById(graph.getAttribute("id") + "_()_info");

    // The graph info at this stage of the animation
    if (info.firstChild)
        this.graph_info = info.firstChild.nodeValue;
    else
        this.graph_info = "";
    this.graph = graph;
    this.step = step;
}


// Builds an array of tuples of form (edge_id, edge_tooltip_text) using the edges global array
function buildEdgeInfoArray() {
    var e_info = [];
    for (var e in edges) {
        for (var i in edges[e]) {
            var text_elem = the_evt_target.getElementById(edges[e][i].getAttribute("id") + "_tt_text");
            var pair = [];
            pair.push(edges[e][i].getAttribute("id"));
            if (text_elem !== null)
                pair.push(text_elem.firstChild.nodeValue);
            else {
                pair.push(null);
            }

            e_info.push(pair);
                
        }
    }
    return e_info;
}


//Builds a state array representation of the graph
//A state array is an array representing the state of the graph at any point during animation, and is of the form
// Array( Array( tag_type_1st_element, attr1, val1, attr2, val2, attr3...), Array( tag_type_2nd_element, attr1, val1, attr2, val2, ...), ...)
// attribute1 and value1 will always pertain to id and its value
function buildStateArray(graph) {

    var graph_elems = graph.childNodes;

    // The total state entity
    var state_holder = new Array(); 

    // The states of the elements that are present
    var states = new Array();

    // The elements that are present at that point in the animation(ie. haven't been deleted)
    var elems_present = new Array();
    
    //Start at one to avoid first, empty element
    for (var i=0; i<graph_elems.length; i++) {
        var elem = graph_elems[i];
        
        //If the element doesn't have any attributes, continue.  For some reason elements are making it in here like [object Text] that have no significance(whitespace maybe?)
        if (!shouldIncludeElement(elem))
            continue;
        var attributes = elem.attributes;
        
        var elem_array = new Array();
        elem_array.push(elem.tagName);
        var id = elem.getAttribute("id");
        
        // Add to elems_present if not seen already
        if (elems_present.indexOf("id") === -1)
            elems_present.push(id);

        elem_array.push(id);
        
        if(document.getElementById(v_ano_id + id) != null){
            ano = document.getElementById(v_ano_id + id);
            elem_array.push(ano.firstChild.nodeValue);
        } else {
            elem_array.push("");
        }
        
        //Loop over all attributes of the element
        for ( ind in attr_array) {
            attr = attr_array[ind];
            //If the attribute is defined and not id(already added), then add it to the array
            if (elem.getAttribute(attr) != null && attr != 'id') {
                elem_array.push(attr);
                elem_array.push(elem.getAttribute(attr));
            }
        }
        states.push(elem_array);
    }
    
    state_holder.push(states);
    state_holder.push(elems_present);

    return state_holder;
}


/* Model this off of AnimateLoop, except translate the graph off the screen before 
doing the animations.  Save the graph state every STEP_INTERVAL commands, and in between
there save the commands */
function fillGraphStates() {
    
    filling_states = true;

    var graphs = new Array();  
    for (var g in init_graphs) {
        graphs.push(the_evt_target.getElementById(init_graphs[g].getAttribute("id")));

        // Call once to get MAX_GBBOX values set, in case it isn't called during algo
        sizeGraphBBox(graphs[g]);
    }

    // Keep track of added and deleted elements for restoration to initial state
    deleted_elements = new Array();
    added_elements = new Array();

    var numAnims = animation.length;
    for ( var step=0; step<numAnims; step++) {
        if ( step %% STEP_INTERVAL === 0) {
            if (two_graph)
                graph_states.push(new Array(new GraphState(graphs[0], step), new GraphState(graphs[1], step)));
            else
                graph_states.push(new Array(new GraphState(graphs[0], step)));
        }
        
        //Do the next command, special case for SetAllVerticesColor
        if(animation[step][1] == SetAllVerticesColor && animation[step].length > 3){
            var vertexArray = new Array();
            for (var i = 3; i < animation[step].length; i++){
                vertexArray[i-3] = animation[step][i];
            }
            animation[step][1](animation[step][2],vertexArray);
        }else{
            // If an edge is going to be deleted save it for later restoration
            var graph_num = 1;

            if (animation[step][1] == DeleteEdge) {
                var add_ind = added_elements.indexOf(animation[step][2]);
                
                if (add_ind !== -1)
                    delete added_elements(add_ind); 
                else
                    deleted_elements.push(animation[step][2]);
                
            } else if (animation[step][1] == AddEdge) {
                var del_ind = deleted_elements.indexOf(animation[step][2]);
                
                // If the added element is in deleted_elements then just remove from deleted_elements.  Otherwise, add to added_elements
                if (del_ind !== -1)
                    delete deleted_elements[del_ind]; 
                else
                    added_elements.push(animation[step][2]);
                
            }

            animation[step][1](animation[step][2],animation[step][3],animation[step][4]);
        }       
        //Need to realign components here??
        
    }
    
    filling_states = false;
    StopAnimation(undefined);
}


/* Sets the attributes of the graph to that of the given graph_state */
/* Sets the attributes of the graph to that of the given graph_state */
function setGraphState(graph_state) {
    if (graph_state === undefined)
        return;

    // Prevent sizegraphbbox from being called on every animation function
    switching_states = true;

    // Keep track of elements found on graph.  
    // The ones not found on graph that are in state_array must be added
    var elements_found = new Array();
    
    for (var x in init_graphs) {
        var graph = the_evt_target.getElementById(init_graphs[x].getAttribute("id"));
        var state_array = graph_state[x].state;

        var temp = new Array(state_array[1].length);
        for (var i=0; i<state_array[1].length; i++)
            temp[i] = false;
        
        elements_found.push(temp);
        
        var children = graph.childNodes;
        var found = 0;
        for (var i=0; i<children.length; i++) {
            var child = children.item(i);
            if (child.attributes == null) {
                child = child.nextSibling;
                continue;
            }
            
            var child_id = child.getAttribute("id");
            var ind = state_array[1].indexOf(child_id);
            
            if (ind == -1) {
                // The element on graph isn't in state array, get rid of it
                var elem_type = is_edge_or_vert(child_id);
                if (elem_type === 0)
                    DeleteEdge(child_id);
                else {
                    //alert("We got a non-edge id: " + child_id);
                    SetVertexAnnotation(1, "s", "black");
                }
            } else {
                // The element on graph is in state array
                found ++;
                elements_found[x][ind] = true;
            }
            
            child = child.nextSibling;
            ind++;
        }
        
        // Go over the elements that haven't been found and add them to the graph
        for (var i=0; i<state_array[1].length; i++) {
            if (elements_found[x][i] == false) {
                // The element in state_array wasn't found-- add it in
                var type = is_edge_or_vert(state_array[1][i]);
                if (type === 0) {
                    AddEdge(state_array[1][i]);
                    elements_found[x][ind] = true;
                } else {
                    //alert("We got a non-edge!! " + state_array[1][i]);
                }
            }
        }
    
    }
    

    //
    for (var g in graph_state) {
        var state_array = graph_state[g].state;

        //Set attributes of elements one at a time
        for ( var i=0; i<state_array[0].length; i++) {
            id = state_array[0][i][1];
            var elem = the_evt_target.getElementById(id);
            if (elem === null) {
                continue;
            }
            
            //Check for vertex annotation
            if (state_array[0][i][2] != "") {
                SetVertexAnnotation(id, state_array[0][i][2], undefined);
            } else if (the_evt_target.getElementById(v_ano_id + id) != null)  {
                var ano = the_evt_target.getElementById(v_ano_id + id);
                ano.parentNode.removeChild(ano);
            }
            
            for ( var j=3; j<state_array[0][i].length; j+=2) {
                elem.setAttribute(state_array[0][i][j], state_array[0][i][j+1]);
            }
        }

        // Update all the edge infos and graph info
        var edge_infos = graph_state[g].edge_info;
        for (var i=0; i<edge_infos.length; i++) 
            UpdateEdgeInfo(edge_infos[i][0], edge_infos[i][1]);
        UpdateGraphInfo(graph_state[g].graph.getAttribute("id"), graph_state[g].graph_info);
    }

    switching_states = false;
    for (var x in init_graphs) {
        var graph = document.getElementById(init_graphs[x].getAttribute("id"));
        var graph_bg = document.getElementById(graph.getAttribute("id") + "_bg");
        scaleGraph(graph, graph_bg, undefined, true);   
        sizeGraphBBox(graph);
    }
}


function fillAttributeArray() {
    attr_array = new Array("tagName", "id", "x1", "y1", "x2", "y2", "stroke", 
                        "stroke-width", "fill", "x", "y", "cx", "cy", "r",
                        "text-anchor", "font-family", "font-size", "font-style",
                        "font-weight", "nodeValue", "points", "style", "blank", "dx");
}


function jumpToStep(n) {
    //graph state to which animations will be applied
    var base_state;     
    step = n;
    
    //Find the graph_state to build off of
    for ( i in graph_states) {
        if (graph_states[i][0].step > n) {
            base_state = graph_states[i-1];
            break;
        }
    }
    if (base_state === undefined)
        base_state = graph_states[graph_states.length-1];
    
    setGraphState(base_state);
        
    //Apply steps base_state.step -> n
    for ( var i=base_state[0].step; i<n; i++) {
    
        //Do the next command, special case for SetAllVerticesColor
        if(animation[i][1] == SetAllVerticesColor && animation[i].length > 3){
            var vertexArray = new Array();
            
            for(var j = 3; j < animation[i].length; j++)
                vertexArray[j-3] = animation[i][j];
            
                animation[i][1](animation[i][2],vertexArray);
        }else{
            animation[i][1](animation[i][2],animation[i][3],animation[i][4]);
        }    
         
    }// end for
}



/*
//
//Movie Slider
//
*/
// Creates a simple slider that controls the position of the animation in the full "movie"
function MovieSlider(id, slider_width, thumb_height, offset, end_time, end_step, actions) {

    this.slider = null;
    this.slider_bar = null;
    this.slider_thumb = null;
    this.low_bound = 0;
    this.up_bound_time = end_time;
    this.up_bound_step = end_step;
    this.thumb_active = false;
    this.current_step = 0;  // formerly current_setting
    this.current_time = 0;
    this.offset = offset;
    
    this.thumb_width = 10;
    var font_size = 10;
    
    this.slider = document.createElementNS(svgNS, 'g');
    this.slider.setAttribute("id", id);
    
    this.slider_bar = document.createElementNS(svgNS, "rect");
    this.slider_bar.setAttribute("width", slider_width);
    this.slider_bar.setAttribute("height", this.thumb_width);
    this.slider_bar.setAttribute("x", this.thumb_width/2);
    this.slider_bar.setAttribute("y",(thumb_height-this.thumb_width)/2);
    //this.slider_bar.setAttribute("rx", this.thumb_width/2);
    //this.slider_bar.setAttribute("ry", this.thumb_width/2);
    //this.slider_bar.setAttribute("stroke", "black");
    this.slider_bar.setAttribute("fill", "url(#slider_bar_lg)");
    //this.slider_bar.setAttribute("stroke-width", 1);
    this.slider_bar.setAttribute("cursor", "pointer");
    this.slider_bar.setAttribute("id", id + "_slider_bar");
    this.slider.appendChild(this.slider_bar);
    
    this.slider_thumb = document.createElementNS(svgNS, "rect");
    this.slider_thumb.setAttribute("width", this.thumb_width);
    this.slider_thumb.setAttribute("height", thumb_height);
    this.slider_thumb.setAttribute("rx", this.thumb_width/2);
    this.slider_thumb.setAttribute("ry", this.thumb_width/2);
    this.slider_thumb.setAttribute("x", 0);
    this.slider_thumb.setAttribute("y", 0);
    this.slider_thumb.setAttribute("stroke", "black");
    this.slider_thumb.setAttribute("fill", "url(#slider_thumb_lg)");
    this.slider_thumb.setAttribute("stroke-width", 1);
    this.slider_thumb.setAttribute("cursor", "pointer");
    this.slider_thumb.setAttribute("id", id + "_slider_thumb");
    this.slider.appendChild(this.slider_thumb);
            
    for (var i in actions){
        this.slider.setAttribute(actions[i][0], actions[i][1]);
    }
    
    the_evt_target.appendChild(this.slider);
}


// Click-handler for movie_slider, sets thumb_active if there's a drag, or calls Move_MovieSlider if there is only a click
function Click_MovieSlider(evt) {
    if (evt.target.getAttribute("id") === "movie_slider_slider_thumb")
        movie_slider.thumb_active = true;
    else if (evt.target.getAttribute("id") === "movie_slider_slider_bar") 
        Move_MovieSlider(evt);
}


// Called on mouse-up, deactivates movie_slider from any use
function Deactivate_MovieSlider(evt){
    movie_slider.thumb_active = false;
}


// Click-handler for the movie_slider.
// Changes the position and step setting of the movie_slider when the mouse is clicked on a given position
function Move_MovieSlider(evt) {
    var bbox = movie_slider.slider_bar.getBBox();
    var x_pos = cursorPoint(evt, movie_slider.slider_thumb).x;
    if (evt.clientX == undefined)
        x_pos = evt.touches[0].clientX;

    movie_slider.slider_thumb.setAttribute("x", x_pos - movie_slider.thumb_width/2);
    var pos_factor = (movie_slider.slider_thumb.getAttribute("x")/movie_slider.slider_bar.getAttribute("width"));
    movie_slider.current_step = Math.floor(movie_slider.low_bound + (movie_slider.up_bound_step - movie_slider.low_bound)*pos_factor);
    movie_slider.current_time = Math.floor(movie_slider.low_bound + (movie_slider.up_bound_time - movie_slider.low_bound)*pos_factor);
    jumpToStep(movie_slider.current_step);
}


// Drag-handler for movie_slider
// Changes the position of the movie_slider bar and the current step when the bar is dragged
function Drag_MovieSlider(evt) {
    if (movie_slider.thumb_active) {
        var x_pos = cursorPoint(evt, movie_slider.slider_bar).x;
        
        if (x_pos === undefined) 
            x_pos = evt.touches[0].clientX;

        var pos_factor = (movie_slider.slider_thumb.getAttribute("x")/movie_slider.slider_bar.getAttribute("width"));
        if (x_pos >= movie_slider.slider_bar.getBBox().x && x_pos < (movie_slider.slider_bar.getBBox().width + movie_slider.thumb_width/2)){
            movie_slider.slider_thumb.setAttribute("x", x_pos - movie_slider.thumb_width/2);
            movie_slider.current_step = Math.floor(movie_slider.low_bound + (movie_slider.up_bound_step - movie_slider.low_bound)*pos_factor);
            movie_slider.current_time = Math.floor(movie_slider.low_bound + (movie_slider.up_bound_time - movie_slider.low_bound)*pos_factor);
        } else if (x_pos >= (movie_slider.slider_bar.getBBox().width + movie_slider.thumb_width/2)) {
            //If slider bar is all the way to right set to up_bound-1
            movie_slider.current_step = movie_slider.up_bound_step-1;
            movie_slider.current_time = movie_slider.up_bound_time-1;
        } else {
            //If slider bar is all the way to left set to 0
            movie_slider.current_step = 0;
            movie_slider.current_time = 0;
        }   
        jumpToStep(movie_slider.current_step);
    }
}


// Changes the position of the movie slider handle to reflect the given step_num
function Refresh_MovieSlider(step_num, time_num) {
    if (step_num !== null)
        movie_slider.current_step = step_num;
    if (time_num !== null)
        movie_slider.current_time = time_num;
    var thumb_pos = (movie_slider.current_step/movie_slider.up_bound_step) * movie_slider.slider_bar.getAttribute("width");
    movie_slider.slider_thumb.setAttribute('x', thumb_pos);
}


// Adds a bounding box to the action controls at the bottom of the screen
function addControlBoundingBox(color) {
    var llc_box = horiz_layout[1].group.getBBox();
    var rect = document.createElementNS(svgNS, "rect");
    rect.setAttribute("id", "controlBBox");
    rect.setAttribute("opacity", .8);
    rect.setAttribute("width", llc_box.width + 20);
    rect.setAttribute("height", llc_box.height + 10);
    rect.setAttribute("x", llc_box.x - 10);
    rect.setAttribute("y", llc_box.y - 5);
    rect.setAttribute("rx", "4");
    rect.setAttribute("ry", "4");
    rect.setAttribute("fill", "url(#control_box_lg)");
    rect.setAttribute("stroke", color);
    rect.setAttribute("stroke-width", "2px");
    
    horiz_layout[1].group.insertBefore(rect, action_panel.llc.group);
}


// Position the action_panel and movie_slider controls at the bottom-center of the screen
function positionControls() {
    var bbox = the_evt_target.getElementById("controlBBox").getBBox();
    var x_trans = (viewbox_x - bbox.width)/2 + bbox.x;
    var y_trans = viewbox_y - 10 - horiz_layout[1].group.getBBox().height*2;

    /*
    while((window.innerHeight - (y_trans + horiz_layout[1].group.getBBox().height)) > (20 + horiz_layout[1].group.getBBox().height))
        y_trans += 10;

    while ((y_trans + horiz_layout[1].group.getBBox().height) > window.innerHeight) 
        y_trans -= 10;
    */
    setTranslate(horiz_layout[1].group, x_trans, y_trans); 
}


// Retrieve the viewbox value set in the svg document
function getViewboxVals() {
    viewbox_str = the_evt_target.getAttribute("viewBox").split(" ");
    viewbox_x = viewbox_str[2];
    viewbox_y = viewbox_str[3];
}


// Sets the maximum scale factor the graph can apply before going off the screen
// Sets the maximum scale factor the graph can apply before going off the screen
function set_max_scale_factor() {
    
    function max_factor_y(graph) {
        // Graph Dimensions
        var height = graph.getBBox().height;
        var graph_y = graph.getBBox().y;

        // Translation of right_vert_layout, the vert_layout, and the graph itself
        var translation1 = getTranslate(right_vert_layout.group.getAttribute("transform"));
        var translation2 = getTranslate(vert_layout.group.getAttribute("transform"));
        var translation3 = getTranslate(graph.getAttribute("transform"));
        var translate = translation1[1] + translation2[1] + translation3[1];

        var bottom_height = horiz_layout[1].group.getBBox().height + 30;    // Height of the bottom action bar
        if (two_graph)
            bottom_height += 10;

        var total_sans_height = y_offset + graph_y + translate + bottom_height;

        // Find how much larger the graph could be before the total becomes greater than the viewbox_y
        var max_height = viewbox_y - total_sans_height;
        var max_factor_y = max_height / height;
        return max_factor_y;
    }

    function max_factor_x(graph) {
        // Graph Dimensions
        var width = graph.getBBox().width;
        var graph_x = graph.getBBox().x;

        // Translation of right_vert_layout, the vert_layout, and the graph itself
        var translation1 = getTranslate(right_vert_layout.group.getAttribute("transform"));
        var translation2 = getTranslate(vert_layout.group.getAttribute("transform"));
        var translation3 = getTranslate(graph.getAttribute("transform"));
        var translate = translation1[0] + translation2[0] + translation3[0];

        var total_sans_width = x_offset + graph_x + translate;

        // Find how much larger the graph could be before the total becomes greater than the viewbox_x
        var max_width = viewbox_x - total_sans_width;
        var max_factor_x = max_width / width;
        return max_factor_x;
    }


    var curr_max = 999999;
    for (var i in init_graphs) {    
        var graph = document.getElementById(init_graphs[i].getAttribute("id"));
        curr_max = Math.min(curr_max, Math.min(max_factor_y(graph), max_factor_x(graph)));
    }
    max_scale_factor = curr_max;
}


// Scales the graph to fit the screen.  
// Only really matters in cases where the graph is too large for the screen initially
function scale_to_fit() {
    var graph = document.getElementById(init_graphs[0].getAttribute("id"));
    var graph_bg = document.getElementById(graph.getAttribute("id") + "_bg");
    if (max_scale_factor < 1) {
        g_scale_factor.x = max_scale_factor;
        g_scale_factor.y = max_scale_factor;
        scaleGraph(graph, graph_bg, undefined, true);
    }
}

function fill_initArrays() {
    init_edges = new Array();
    init_verts = new Array();

    // Put in as many arrays as there are graphs
    for (var g in init_graphs) {
        init_edges.push(new Array());
        init_verts.push(new Array());
    }

    for (var g in init_graphs) {
        var child = the_evt_target.getElementById(init_graphs[g].getAttribute("id")).firstChild;

        while (child != null) {
            // Skip over textnodes and other such nonsense
            if (!shouldIncludeElement(child)) {
                child = child.nextSibling;
                continue;
            }

            var id = child.getAttribute("id");
            
            var type = is_edge_or_vert(id);
            
            if (type === 0) {
                // It's an edge
                init_edges[g].push(id);
            } else if (type === 1) {
                // It's an edge
                init_verts[g].push(id);
            }

            child = child.nextSibling;
        }
    }
}

// Returns -1 if neither, 0 for edge, 1 for vertex
function is_edge_or_vert(id) {
    var prefixes = new Array("g1", "g2");
    if (prefixes.indexOf(id.substring(0,2)) != -1) {
        if (id.charAt(3) === '(') {
            // It's an edge    
            return 0;
        } else {
            // It's a vertex
            return 1;
        }
    }
    return -1;
}


function sendClick(evt) {
    if (window.parent.beenClicked) 
        window.parent.beenClicked();
}


function ShowAlgoInfo(evt) {
    algo_info_active = true;
    showPopWin('./infos/BFS-BFS.html', viewbox_x*1/2, viewbox_y*1/2, 
        function() { algo_info_active = false; }
        );
}

// Returns the total time, which is the sum of the durations of each step
function get_total_animation_time() {
    var sum = 0;
    for (var i in animation) {
        sum += animation[i][0];
    }
    return sum;
}

// Tests whether we should include an element in the state array
function shouldIncludeElement(elem) {
    if (elem.attributes !== null && elem.nodeName !== "#text") {
        return true;
    }
    return false;
}


/**
*
*
*
* Main program
*
*
*/
function Initialize(evt) {
    initPopUp();    // Initialize the algorithm info

    // Initialize variables related to the document.  Why the hell do we have the_evt_target and the_evt_target?
    the_evt = evt;
    the_evt_target = evt.target;

    // Object Prototype initialization
    HTB_prototypeInit();
    LLC_prototypeInit();
    BP_prototypeInit();
    SS_prototypeInit();

    fillAttributeArray();   // Fills the array of attributes that svg elements may contain
    getViewboxVals();       // Set the viewbox_x and viewbox_y global vars
    
    //Create a point for translating svg coords to mouse coords
    pt = the_evt_target.createSVGPoint();       
    
    // Set global event handlers
    the_evt_target.addEventListener("mousemove", drag_scaler, false);
    the_evt_target.addEventListener("mouseup", deactivate_scaler, false);
    the_evt_target.addEventListener("mouseup", Deactivate_MovieSlider, false);
    the_evt_target.addEventListener("mousemove", Drag_MovieSlider, false);
    the_evt_target.addEventListener("mousemove", positionTooltip, false);
    the_evt_target.addEventListener("mousemove", sendClick, false);

    //Create code layout
    code = new HighlightableTextBlock(20, 0, "code", 14, "vertical");

    // Insert lines of code into the HighlightableTextBlock
    var linenum = 1;
    while(document.getElementById("l_" + linenum) != null){
        code.insertLine("l_" + linenum, linenum-1);
        linenum++;
    }

    // Add transparent breakpoints
    AddBreakpoints(code);

    code.addBoundingBoxAndAlgoButton("#8888AA");
    
    //speed_select = new SpeedSelector("speedSelect", 20, "blue", "red");

    //Make code lines interactive
    var code_lines = code.line_llc.group.childNodes;
    for (var i = 0; i < code_lines.length; i++){
            if(code_lines.item(i).nodeName == "text"){
                code_lines.item(i).setAttribute("cursor", "pointer");
                code_lines.item(i).setAttribute("onclick", "SetBreakpoint(evt)");
            }
    }

    
    //Clone initial graphs and keep references to them
    init_graphs = new Array();
    var i = 1;
    var tree = document.getElementById("g" + i);
    while(tree != null){
        if (i === 2)
            two_graph = true;

        init_graphs[i-1] = tree.cloneNode(true);
        i++;
        tree = document.getElementById("g" + i);
    }
        
    // Fill the array of all edges
    fillEdgesArray();

    //Create buttons
    action_panel = new ButtonPanel(15, 2, "actions", "horizontal");
    action_panel.createButton("start_button", "M0,0 0,30 20,15 Z", button_color, 0, "StartAnimation(evt)");
    action_panel.createButton("step_button", "M0,0 0,30 20,15 Z M20,0 20,30 30,30 30,0 Z", button_color, 1, "StepAnimation(evt)");
    action_panel.createButton("continue_button", "M0,0 0,30 10,30 10,0 Z M15,0 15,30 35,15 Z", button_color, 2, "ContinueAnimation(evt)");
    action_panel.createButton("stop_button", "M0,0 0,30 30,30 30,0 Z", button_color, 3, "StopAnimation(evt)");
    action_panel.deactivateButton("continue_button");
    action_panel.deactivateButton("stop_button");
    action_panel.deactivateButton("step_button");
    
    var graph = document.getElementById("g1");
    var total_time = get_total_animation_time();
    var total_steps = animation.length;
    movie_slider = new MovieSlider('movie_slider', 1000-x_offset-getTranslate(action_panel.llc.group.getAttribute("transform"))[0]-action_panel.llc.group.getBBox().width, 30, x_offset, total_time, total_steps, [['onmousedown', 'Click_MovieSlider(evt)']]);

    timeout = 200;

    //Lay out code, speed slider, and graphs 
    vert_layout = new LinearLayoutComponent(20, 30, "vert_layout", "vertical");
    horiz_layout = new Array(new LinearLayoutComponent(20, 10, "horiz_layout_0", "horizontal"), new LinearLayoutComponent(20, 10, "horiz_layout_1", "horizontal"));
    
    left_vert_layout = new LinearLayoutComponent(20, 10, "vert_layout_left", "vertical");
    left_vert_layout.insertComponent(code.line_llc.group.getAttribute("id"), 0);
    right_vert_layout = new LinearLayoutComponent(20, 10, "right_vert_layout", "vertical");
    horiz_layout[1].insertComponent(action_panel.llc.group.getAttribute("id"), 0);
    horiz_layout[1].insertComponent('movie_slider', 1);
   /// horiz_layout[1].insertComponent('speedSelect', 2);
    horiz_layout[0].insertComponent(left_vert_layout.group.getAttribute("id"), 0);
    
    //speed_select.addBoundingBox("#8888AA");

    for (var x in init_graphs){
        right_vert_layout.insertComponent(init_graphs[x].getAttribute("id"), x);
    }
    
    horiz_layout[0].insertComponent(right_vert_layout.group.getAttribute("id"), 1);
    vert_layout.insertComponent(horiz_layout[0].group.getAttribute("id"), 0);
    vert_layout.insertComponent(horiz_layout[1].group.getAttribute("id"), 1);
    
    //offset to make everything visible
    vert_layout.group.setAttribute("transform", "translate(" + x_offset + " " + y_offset + ")");
    code.highlight_group.setAttribute("transform","translate(" + x_offset + " " + y_offset + ")");

    var scaler_y, scaler_x;

    graph_bgs = new Array();

    //Make rectangles behind graphs, for intuitive iPad usage
    for (var x in init_graphs){
        var rect = document.createElementNS(svgNS, "rect");
        var graph = document.getElementById(init_graphs[x].getAttribute("id"));
        var bg_id = graph.getAttribute("id") + "_bg";

        // Keep track of the backgrounds in use(background being the bbox)
        graph_bgs.push(bg_id);
        init_height_g1 = graph.getBBox().height;

        // Set attributes of graph background
        rect.setAttribute("id", bg_id);
        rect.setAttribute("width",graph.getBBox().width+10);
        rect.setAttribute("height",graph.getBBox().height+10);
        rect.setAttribute("fill", "white");
        rect.setAttribute("fill-opacity", 1);
        rect.setAttribute("stroke-width",1);
        rect.setAttribute("stroke",  "#bcbcbc");
        rect.setAttribute("stroke-dasharray", "5 2");
        rect.setAttribute("x", graph.getBBox().x-10);
        rect.setAttribute("y", graph.getBBox().y-10);
        rect.setAttribute("ongesturestart", "GestureStart_TransformGraph(evt)");
        rect.setAttribute("ongesturechange","GestureChange_TransformGraph(evt)");
        rect.setAttribute("ongestureend","GestureEnd_TransformGraph(evt)");
        rect.setAttribute("ontouchstart", "TouchStart_Graph(evt)");
        rect.setAttribute("ontouchmove", "TouchDrag_Graph(evt)");
        rect.setAttribute("ontouchend", "TouchDeactivate_Graph(evt)");

        var translation1 = getTranslate(right_vert_layout.group.getAttribute("transform"));
        var translation2 = getTranslate(vert_layout.group.getAttribute("transform"));
        var translation3 = getTranslate(graph.getAttribute("transform"));
        setTranslate(rect, translation1[0] + translation2[0] + translation3[0], translation1[1] + translation2[1] + translation3[1]);
        the_evt_target.insertBefore(rect, the_evt_target.childNodes.item(0));
        scaler_x = graph.getBBox().x + graph.getBBox().width + 10;
        scaler_y = graph.getBBox().y + graph.getBBox().height + 10;

        // If the second graph is being looked at, keep track of the initial translates associated with it
        if (x == 1) 
            init_transy_g2 = {"graph":getTranslate(graph.getAttribute("transform"))[1], "bg":(translation1[1] + translation2[1] + translation3[1])};
    } 

    // Add tooltips and graphinfo
    AddToolTips();
    loadInitialInfo();
    positionGraphInfo();

    // Scale the components to fit the screen
    set_max_scale_factor();
    scale_to_fit();

    // Create the scaler
    var points_val = String(scaler_x) + "," + String(scaler_y) + " " + String(scaler_x-20) + "," + String(scaler_y) + " " + String(scaler_x) + "," + String(scaler_y-20);
    scaler = new Scaler(points_val, 20);

    // Initialize the array containing all original elements
    fill_initArrays();

    // Initialize the array of graph states
    fillGraphStates();

    // Reposition scaler
    for (var x in init_graphs) {
        var graph = the_evt_target.getElementById(init_graphs[x].getAttribute("id"));
        repositionScaler(graph.getBBox().x, graph.getBBox().y);
    }

    document.documentElement.setAttribute("width", 2*x_offset + vert_layout.group.getBBox().x + vert_layout.group.getBBox().width);
    document.documentElement.setAttribute("height", 2*y_offset + vert_layout.group.getBBox().y + vert_layout.group.getBBox().height);
    
    // Set global vars
    browser_width = window.innerWidth;
    browser_height = window.innerHeight;
    
    // Position action controls at bottom-center of the screen
    screen_ctm = the_evt_target.getScreenCTM();
    
    //Create the option dropdown that will be positioned at top right of screen
    option_menu = new OptionMenu('option_menu', 20, 35, [{'function':BackLink, 'args':['backlink', 'Click me', link_color]}, {'function':AlgorithmInfoButton, 'args':[]}, {'function':SpeedSelector, 'args':['speed_select', 20, 'blue', border_color]}]);
    horiz_layout[1].insertComponent(option_menu.cog.getAttribute("id"), 2);

    // Add bounding box to action controls, and then position them correctly
    addControlBoundingBox("#333333");
    positionControls();

    option_menu.translate_dropdown();
}

var anim_array = Array(%(animation)s
);

]]></script>
"""

head = """<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:ev="http://www.w3.org/2001/xml-events" version="1.1" baseProfile="full"
viewbox="%(x)d %(y)d %(width)d %(height)d" width="30cm" height="30cm">
<defs>  
    <linearGradient id="slider_bar_lg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="skyblue" >
        </stop>
        <stop offset="1" stop-color="black">
        </stop>
    </linearGradient>
    
    <linearGradient id="slider_thumb_lg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#C0C0C0">
        </stop>
        <stop offset="1" stop-color="black">
        </stop>
    </linearGradient>
</defs>
"""