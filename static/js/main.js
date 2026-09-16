document.addEventListener('DOMContentLoaded', ()=>{
  // mini map
  const mm = document.getElementById('mini-map');
  if(mm){
    const map = L.map(mm).setView([20,0],2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:''}).addTo(map);
  }
  const im = document.getElementById('item-map');
  if(im){
    const map = L.map(im).setView([20,0],2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:''}).addTo(map);
  }

  // draggable location picker for the report form
  const lp = document.getElementById('location-picker');
  if(lp){
    const latInput = document.getElementById('lat-input');
    const lngInput = document.getElementById('lng-input');
    const coordsLabel = document.getElementById('picked-coords');
    const map = L.map(lp).setView([20,0],2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:''}).addTo(map);

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
