const express = require("express");
const http = require("http");
const socketIO = require("socket.io");
const path = require("path");

// Initialize the Express app and the HTTP server
const app = express();
const server = http.createServer(app);
const io = socketIO(server);

let hosts = [];

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, "public")));

// Handle a client connecting to the server
io.on("connection", (socket) => {
  console.log("Client connected", socket.id);
  socket.emit("control_id", socket.id);
  socket.emit('AUI', hosts);

  socket.on("host", (data) => {
    socket.to(data.host).emit("host", { clint: socket.id, password: data.password });
  });

  socket.on("host_info", (data) => {
    hosts.push(data);
    socket.broadcast.emit('AUI', hosts);
  });

  // Emit screen share data to the client
  socket.on("screen_share", (data) => {
    io.to(data.to).emit("screen_share", data);
  });

  // Emit audio share data to the client
  socket.on("audio_share", (data) => {
    io.to(data.to).emit("audio_share", data);
  });

  // Handle remote control events
  socket.on("remote_control", (data) => {
    // Process the remote control data here
    data['me'] = socket.id
    socket.to(data["to"]).emit("remote_control", data);
    socket.emit("control_ack", { status: "done" });
  });

  socket.on("screen_size", (data) => {
    socket.to(data.to).emit("screen_size", data);
  });

  // Handle client disconnection
  socket.on("disconnect", () => {
    // Find the index of the element to remove
    const indexToRemove = hosts.findIndex((item) => item[0] === socket.id);

    if (indexToRemove !== -1) {
      // Remove the element at the specified index
      hosts.splice(indexToRemove, 1);
    }
    console.log("Client disconnected", socket.id);
    socket.broadcast.emit('AUI', hosts);
    socket.broadcast.emit('clint_left', socket.id)
  });
});

// Start the server on port 3000
server.listen(3000, '0.0.0.0', () => {
  console.log("Server listening on port 3000");
});
