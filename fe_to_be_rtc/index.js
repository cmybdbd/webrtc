var express = require("express")
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var port = process.env.PORT || 3000;
var path = require("path")


app.use(express.static(__dirname + 'river_footage/'));
app.use(express.static(__dirname + '/public/'))

app.get('/', function(req, res){
  // res.sendFile(path.join(__dirname+'/index.html'));
  res.sendFile(__dirname+'index.html')

});

io.on('connection', function(socket){
  socket.on('chat message', function(msg){
  	console.log("the mesage is", msg)
    io.emit('chat message', msg);
  });



  socket.on('offer broadcast', function(msg){
  	io.emit('offer broadcast', msg)
  })


  socket.on('answer broadcast', function(msg){
  	io.emit('answer broadcast', msg)
  })

  socket.on('trigger2', function(msg){
  	io.emit('trigger2', msg)
  })


  socket.on("candidate", function(msg){
  	io.emit('candidate', msg)
  })



});

http.listen(port, function(){
  console.log('listening on *:' + port);
});
