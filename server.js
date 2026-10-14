import express from 'express';
import { createServer } from 'http';
import { parse } from 'url';
import next from 'next/dist/server/next.js';
import dotenv from 'dotenv';

dotenv.config();

const dev = process.env.NODE_ENV !== 'production';
const hostname = process.env.HOSTNAME || 'localhost';
const port = parseInt(process.env.PORT || '3000', 10);

const app = next({ dev, hostname, port });
const handle = app.getRequestHandler();

app.prepare().then(() => {
  const server = express();

  // Health check endpoint
  server.get('/_health', (req, res) => {
    res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  // Agent inspector endpoint
  server.get('/_agent', (req, res) => {
    res.status(200).json({
      name: 'taghdisilabs',
      version: '0.2.0',
      status: 'running',
      uptime: process.uptime(),
      environment: process.env.NODE_ENV,
      timestamp: new Date().toISOString()
    });
  });

  // All other routes
  server.all('*', (req, res) => {
    const parsedUrl = parse(req.url, true);
    handle(req, res, parsedUrl);
  });

  server.listen(port, hostname, () => {
    console.log(`🚀 Server ready at http://${hostname}:${port}`);
    console.log(`📊 Agent Inspector: http://${hostname}:${port}/_agent`);
    console.log(`❤️  Health Check: http://${hostname}:${port}/_health`);
  });
});
