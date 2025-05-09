import { useEffect, useState } from "react";
import io from "socket.io-client";

export default function LiveChart() {
    const [marketData, setMarketData] = useState(null);

    useEffect(() => {
        const socket = io("http://localhost:5000");

        socket.on("market_data", (data) => {
            console.log("📩 Market Data:", data);
            setMarketData(JSON.parse(data));
        });

        socket.on("disconnect", () => {
            console.log("⚠️ WebSocket Disconnected");
        });

        return () => socket.disconnect(); // Cleanup
    }, []);

    return (
        <div>
            <h2>📊 Live Market Data</h2>
            {marketData ? (
                <pre>{JSON.stringify(marketData, null, 2)}</pre>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
}
