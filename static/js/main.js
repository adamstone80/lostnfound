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
});
