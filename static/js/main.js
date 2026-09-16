// Default region shown before geolocation resolves or when no coordinates exist.
const DEFAULT_CENTER = [-33.6494, 151.0503]; // Galston, Sydney
const DEFAULT_ZOOM = 12;

function addTiles(map){
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:''}).addTo(map);
}

document.addEventListener('DOMContentLoaded', ()=>{
  // home mini map: fit to all reported items that have coordinates
  const mm = document.getElementById('mini-map');
  if(mm){
    const map = L.map(mm).setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    addTiles(map);
    const items = window.homeItems || [];
    if(items.length){
      const markers = items.map(it => L.marker([it.lat, it.lng]).bindPopup(it.title));
      const group = L.featureGroup(markers).addTo(map);
      if(items.length === 1){
        map.setView([items[0].lat, items[0].lng], 14);
      } else {
        map.fitBounds(group.getBounds().pad(0.2));
      }
    }
  }

  // item detail map: center on this item's location if known
  const im = document.getElementById('item-map');
  if(im){
    const lat = parseFloat(im.dataset.lat);
    const lng = parseFloat(im.dataset.lng);
    const hasCoords = !isNaN(lat) && !isNaN(lng);
    const map = L.map(im).setView(hasCoords ? [lat, lng] : DEFAULT_CENTER, hasCoords ? 14 : DEFAULT_ZOOM);
    addTiles(map);
    if(hasCoords){
      L.marker([lat, lng]).addTo(map).bindPopup(im.dataset.title || '');
    }
  }

  // draggable location picker for the report form
  const lp = document.getElementById('location-picker');
  if(lp){
    const latInput = document.getElementById('lat-input');
    const lngInput = document.getElementById('lng-input');
    const coordsLabel = document.getElementById('picked-coords');
    const map = L.map(lp).setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    addTiles(map);

    function updateCoords(){
      const c = map.getCenter();
      latInput.value = c.lat.toFixed(6);
      lngInput.value = c.lng.toFixed(6);
      coordsLabel.textContent = 'Selected: ' + c.lat.toFixed(5) + ', ' + c.lng.toFixed(5);
    }
    map.on('move', updateCoords);
    updateCoords();

    if(navigator.geolocation){
      navigator.geolocation.getCurrentPosition(pos=>{
        map.setView([pos.coords.latitude, pos.coords.longitude], 14);
      });
    }
  }
});
