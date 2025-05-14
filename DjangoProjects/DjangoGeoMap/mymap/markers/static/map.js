const href = "https://www.openstreetmap.org/copyright";
const link = `© <a href='${href}'>OpenStreetMap</a>`;
const tiles = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const layer = L.tileLayer(tiles, { attribution: link });
const map = L.map("map", { layers: [layer] });

map.fitWorld();