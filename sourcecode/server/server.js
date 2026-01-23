const WebSocket = require("ws");

// Tạo WebSocket server tại cổng 8080
const wss = new WebSocket.Server({ port: 8080 });

console.log("WebSocket server running at ws://localhost:8080");

// Khi có client kết nối
wss.on("connection", (ws) => {
    console.log("Client connected");

    // Khi server nhận tin nhắn từ client
    ws.on("message", (message) => {
        console.log("Received:", message.toString());

        // Gửi tin nhắn cho tất cả client
        wss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN) {
                client.send("Server broadcast: " + message.toString());
            }
        });
    });

    ws.on("close", () => {
        console.log("Client disconnected");
    });
});
