const API = 'http://localhost:8000'

document.getElementById('login').onclick = ()=>{
  alert('Please login to the website to obtain your token.')
}

async function getCurrentTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function addGift(jwt, gift) {
  const registryId = localStorage.getItem("registry_id");
  const resp = await fetch(`${API_BASE}/api/registries/${registryId}/items/`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${jwt}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(gift),
  });
  return resp.json();
}

document.getElementById('add').onclick = async ()=>{
  const [tab] = getCurrentTab();
  const token = localStorage.getItem('token')
  if (!token){
    alert('Login required');
    return
  }
  const body = {
    title: tab.title,
    url: tab.url,
    bought: false
  }
  const res = await addGift(token, body);
  const j = await res.json()
  document.getElementById('status').textContent = j.id ? 'Added!' : JSON.stringify(j)
}
