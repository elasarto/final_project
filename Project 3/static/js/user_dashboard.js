// getting references from the html file
var selPlaylist = document.getElementById("selPlaylist");

// var username = document.getElementById('query').value;


// create a variable that correspond to my text input field
function searchUsername() {
    console.log(document.getElementById('query').value)
};

// send it to the route
// JSON.get to the route and the route should include the name
// (flask add something to the end to the route)
// when I get it back I can render it into a graph

// Creating drop down with all the playlists names
// var dataURL = '/spotify_user_playlists/' + String(username.value);

// d3.json(dataURL, function(error, response) {
//     if (error) return console.log(error);

//     console.log(response);

//     var items = response;
//     console.log(items);

//     // for (var i = 0; i < items.length; i++) {

//     //     // Create option elemeent
//     //     var option = document.createElement("option");
//     //     option.setAttribute("value", items[i]);
//     //     option.innerHTML = items[i];

//     //     // Append to select tag
//     //     selDataset.appendChild(option);
//     // };
// });

//Getting the names from app route
// function getJSON(dataURL) {
//     var resp ;
//     var xmlHttp ;
//     resp  = '' ;
//     xmlHttp = new XMLHttpRequest();
//     if(xmlHttp != null)
//     {
//         xmlHttp.open( 'GET', dataURL, false );
//         xmlHttp.send( null );
//         resp = xmlHttp.responseText;
//     }
//     return resp ;
// }

// data = JSON.parse(getJSON('/spotify_user_dashboard/' + username));