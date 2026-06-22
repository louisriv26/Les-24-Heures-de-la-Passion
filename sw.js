/* Stage 7D/R41A — prototype-101r58-stage7d-r41a-evidence-integrity-repair */
const CACHE_NAME = 'luisa-24h-r41a-20260621';
const CACHE_PREFIX = 'luisa-24h-';
const ASSETS = ['./','./index.html','./luisa_24_heures.html','./manifest.json','./version.json','./icon-180.png','./icon-192.png','./icon-512.png'];
self.addEventListener('install', event => { event.waitUntil((async()=>{ const cache=await caches.open(CACHE_NAME); await cache.addAll(ASSETS); await self.skipWaiting(); })()); });
self.addEventListener('activate', event => { event.waitUntil((async()=>{ const keys=await caches.keys(); await Promise.all(keys.filter(k=>k.startsWith(CACHE_PREFIX)&&k!==CACHE_NAME).map(k=>caches.delete(k))); await self.clients.claim(); })()); });
self.addEventListener('fetch', event => { if(event.request.method!=='GET') return; event.respondWith((async()=>{ const cache=await caches.open(CACHE_NAME); const cached=await cache.match(event.request); if(cached) return cached; try { const response=await fetch(event.request); if(response&&response.status===200&&response.type!=='opaque') cache.put(event.request,response.clone()); return response; } catch(error) { if(event.request.mode==='navigate') return cache.match('./index.html'); throw error; } })()); });
