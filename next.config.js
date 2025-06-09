// next.config.js
/** @type {import('next').NextConfig} */
module.exports = {
  async headers() {
    return [
      {
        // apply to all routes
        source: "/(.*)",
        headers: [
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              // allow WebSocket connections to your API hosts
              "connect-src 'self' ws://127.0.0.1:8000 wss://algomin-ui-production.up.railway.app",
              "script-src 'self'",
              "style-src 'self' 'unsafe-inline'",
            ].join("; "),
          },
        ],
      },
    ];
  },
};
