// Small wrapper to save/load designs via the Django backend
async function apiSaveDesign(name, json, id=null){
  const payload = {name: name, json: json, id: id};
  const resp = await fetch('/admin/templates/api/save/',{
    method:'POST',headers:{'Content-Type':'application/json','X-Requested-With':'XMLHttpRequest'},body:JSON.stringify(payload)
  });
  return resp.json();
}

async function apiListDesigns(){
  const resp = await fetch('/admin/templates/api/list/');
  return resp.json();
}

async function apiLoadDesign(id){
  const resp = await fetch(`/admin/templates/api/load/${id}/`);
  return resp.json();
}

async function apiBatchExport(designId, users){
  const resp = await fetch('/admin/templates/api/batch-export/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({design_id:designId,users:users})});
  return resp.json();
}
