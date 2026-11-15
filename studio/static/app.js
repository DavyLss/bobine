const $=id=>document.getElementById(id),form=$('form');let state={jobs:[],settings:{}},selected=null,lastVideo=null,ready=false,busy=false,historySignature='';
const stages=['scenario','voice','alignment','render','verify'];
const names={queued:'En attente',running:'En cours',scenario:'Scénario',voice:'Voix masculine',alignment:'Sous-titres',render:'Animation & rendu',verify:'Contrôle de l’export',done:'Terminée',failed:'Échec',cancelled:'Annulée',interrupted:'Interrompue'};
const duration=s=>s>=60?`${Math.floor(s/60)} min${Math.round(s%60)?' '+Math.round(s%60):''}`:`${Math.round(s)} s`;
const themeName=t=>t==='dark'?'Atelier sombre':'Éditorial clair';
function element(tag,className,text){const e=document.createElement(tag);if(className)e.className=className;if(text!==undefined)e.textContent=text;return e;}
function parameters(){return {title:$('title').value.trim(),description:$('description').value.trim(),theme:form.elements.theme.value,duration:Number($('duration').value),format:form.elements.format.value};}
function preview(){
 const p=parameters();$('duration-label').textContent=duration(p.duration);$('characters').textContent=$('description').value.length.toLocaleString('fr-FR')+' / 6 000';
 if(selected)return;
 $('aspect').textContent=p.format==='reel'?'9:16':'16:9';$('preview-film').className='preview-film '+(p.theme==='dark'?'dark-film':'light-film')+(p.format==='standard'?' wide':'');
 $('preview-title').textContent=p.title||'Votre idée prend forme.';$('preview-signature').textContent=themeName(p.theme).toUpperCase();$('preview-theme').textContent=themeName(p.theme);$('preview-duration').textContent='≈ '+duration(p.duration);
}
function setForm(p){$('title').value=p.title||'';$('description').value=p.description||'';form.elements.theme.value=p.theme||'dark';form.elements.format.value=p.format||'reel';$('duration').value=p.duration||90;preview();}
function clearSelection(){selected=null;lastVideo=null;$('video').pause();$('video').removeAttribute('src');$('video').classList.add('hidden');$('preview-film').classList.remove('hidden');$('downloads').classList.add('hidden');$('preview-heading').textContent='Votre prochain film';renderStatus(null);preview();renderHistory();}
async function api(path,options={}){const r=await fetch(path,{...options,headers:{'Content-Type':'application/json','X-Studio-Request':'1',...options.headers}});if(!r.ok){let data;try{data=await r.json()}catch{data={detail:'Le studio ne répond pas.'}};throw new Error(typeof data.detail==='string'?data.detail:'Vérifiez les champs du formulaire.')}return r.json();}
function renderStatus(job){
 const running=job&&job.status==='running',pending=job&&job.status==='queued',done=job&&job.status==='done',failed=job&&['failed','interrupted'].includes(job.status),cancelled=job&&job.status==='cancelled';
 $('status-heading').textContent=!job?'Prêt à créer':done?'Votre vidéo est prête':failed?'La génération s’est arrêtée':cancelled?'Génération annulée':pending?'Dans la file de création':'Votre idée prend vie';
 $('status-description').textContent=job?(job.warning||job.message):'Votre génération apparaîtra ici, étape par étape.';
 $('stage-name').textContent=job?(names[job.stage]||names[job.status]):'En attente de votre idée';$('percent').textContent=(job?Math.round(job.progress):0)+' %';$('progress-fill').style.width=(job?job.progress:0)+'%';$('live').classList.toggle('hidden',!running);
 const index=job?stages.indexOf(job.stage):-1;
 $('steps').querySelectorAll('li').forEach((li,i)=>{const complete=done||(job&&i<index);li.classList.toggle('complete',!!complete);li.classList.toggle('current',!!running&&i===index);li.querySelector('span').textContent=complete?'✓':i+1;li.querySelector('b').textContent=complete?'Terminé':running&&i===index?'En cours':'';});
 $('job-actions').classList.toggle('hidden',!running&&!pending);$('retry').classList.toggle('hidden',!failed&&!cancelled);$('logs').href=job?`/api/jobs/${job.id}/files/generation.log`:'#';
 $('review-note').textContent=done?'Avant de publier, relisez le scénario et écoutez votre vidéo.':failed?'Les détails sont conservés dans le journal de génération.':'Le calcul peut prendre plusieurs minutes. Vous pouvez laisser cette page ouverte.';
 if(failed){$('downloads').classList.remove('hidden');$('download').classList.add('hidden');$('script').classList.add('hidden');$('subtitles').classList.add('hidden');}
 if(done){
  $('downloads').classList.remove('hidden');['download','script','subtitles'].forEach(id=>$(id).classList.remove('hidden'));$('preview-heading').textContent=job.title;
  const base=`/api/jobs/${job.id}/files/`;$('download').href=base+'Video.mp4?download=true';$('script').href=base+'Scenario.json';$('subtitles').href=base+'Sous-titres.srt?download=true';
  if(lastVideo!==job.id){$('video').src=base+'Video.mp4';$('video').poster=base+'Poster.jpg';lastVideo=job.id;}
  $('video').classList.remove('hidden');$('preview-film').classList.add('hidden');
 }
 if(job){$('preview-theme').textContent=themeName(job.theme);$('preview-duration').textContent=job.actual_duration?duration(job.actual_duration):'≈ '+duration(job.duration);$('aspect').textContent=job.format==='reel'?'9:16':'16:9';
  if(!done){$('preview-film').className='preview-film '+(job.theme==='dark'?'dark-film':'light-film')+(job.format==='standard'?' wide':'');$('preview-title').textContent=job.title;$('preview-signature').textContent=themeName(job.theme).toUpperCase();}
 }
}
function renderHistory(){
 const signature=JSON.stringify([selected,state.jobs.map(j=>[j.id,j.status,j.title,j.theme,j.format,j.duration,j.actual_duration])]);if(historySignature===signature)return;historySignature=signature;
 const grid=$('history-grid');$('job-count').textContent=state.jobs.length;if(!state.jobs.length)return;grid.replaceChildren();
 state.jobs.forEach(job=>{const card=element('button','history-item'+(selected===job.id?' selected':''));card.type='button';const top=element('div','history-item-top');top.append(element('span','',new Date(job.created*1000).toLocaleDateString('fr-FR',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'})),element('span','status-pill '+job.status,names[job.status]||job.status));card.append(top,element('h3','',job.title));const meta=element('p');meta.append(element('span','',themeName(job.theme)+' · '+(job.format==='reel'?'9:16':'16:9')),element('span','',job.actual_duration?duration(job.actual_duration):'≈ '+duration(job.duration)));card.append(meta);card.addEventListener('click',()=>{selected=job.id;lastVideo=null;$('video').pause();$('video').classList.add('hidden');$('downloads').classList.add('hidden');renderStatus(job);renderHistory();$('preview-heading').scrollIntoView({behavior:'smooth',block:'center'});});grid.append(card);});
}
async function refresh(){
 try{state=await api('/api/state');if(selected){const job=state.jobs.find(j=>j.id===selected);renderStatus(job);}renderHistory();}catch(e){$('health').textContent='Studio déconnecté';$('health').className='connection offline';}
}
form.addEventListener('input',preview);form.addEventListener('change',()=>{if(selected)clearSelection();preview();});
form.addEventListener('submit',async e=>{e.preventDefault();if(busy)return;busy=true;$('generate').disabled=true;$('form-error').classList.add('hidden');
 try{const job=await api('/api/jobs',{method:'POST',body:JSON.stringify(parameters())});selected=job.id;lastVideo=null;$('video').pause();$('video').classList.add('hidden');$('downloads').classList.add('hidden');$('last-dark').classList.toggle('hidden',job.theme!=='dark');$('last-light').classList.toggle('hidden',job.theme!=='light');await refresh();$('status-heading').scrollIntoView({behavior:'smooth',block:'center'});}catch(error){$('form-error').textContent=error.message;$('form-error').classList.remove('hidden');}finally{busy=false;$('generate').disabled=!ready;}});
$('new').addEventListener('click',()=>{clearSelection();setForm(state.settings);$('title').focus();window.scrollTo({top:0,behavior:'smooth'});});
$('cancel').addEventListener('click',async()=>{if(!selected)return;$('cancel').disabled=true;try{await api(`/api/jobs/${selected}/cancel`,{method:'POST'});await refresh();}catch(e){$('status-description').textContent=e.message;}finally{$('cancel').disabled=false;}});
$('retry').addEventListener('click',()=>{const job=state.jobs.find(j=>j.id===selected);clearSelection();setForm(job);$('title').focus();window.scrollTo({top:0,behavior:'smooth'});});
async function health(){try{const h=await api('/api/health');ready=h.ready;$('health').className='connection '+(ready?'ready':'offline');$('health').replaceChildren(element('i'),document.createTextNode(ready?'Outils locaux prêts':!h.llm?'Modèle de texte indisponible':'Voix locale indisponible'));$('generate').disabled=!ready||busy;}catch{ready=false;$('generate').disabled=true;}}
setInterval(()=>{const job=state.jobs.find(j=>j.id===selected);$('elapsed').textContent=job?'Écoulé : '+duration((Date.now()/1000)-job.created):'';},1000);
(async()=>{await refresh();setForm(state.settings);$('last-dark').classList.toggle('hidden',state.settings.theme!=='dark');$('last-light').classList.toggle('hidden',state.settings.theme!=='light');const current=state.jobs.find(j=>['running','queued'].includes(j.status));if(current){selected=current.id;renderStatus(current);}await health();setInterval(refresh,2500);setInterval(health,20000);})();
