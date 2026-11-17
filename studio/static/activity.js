/* Shared activity uses the existing state poll, across every application view. */
(()=>{
 const $=id=>document.getElementById(id), dock=$('activity-dock'), panel=$('activity-panel');
 const stages={scenario:'Scénario',voice:'Voix',alignment:'Sous-titres',render:'Animation et rendu',verify:'Contrôle de l’export',metadata:'Kit de publication'};
 const status={queued:'En attente',running:'En cours',preparing:'Préparation',sending:'Envoi en cours',uploading:'Transfert en cours',processing:'Traitement par le réseau',submitted:'Acceptée, à confirmer',scheduled:'Dans la file distante',published:'Publication confirmée',failed:'Échec',error:'Échec',partial:'Résultat partiel',uncertain:'Résultat incertain',interrupted:'Interrompue',needs_attention:'À contrôler',blocked:'Bloquée',waiting:'Planifiée',overdue:'Échéance dépassée',dispatching:'Transmission',cancelled:'Annulée'};
 const networks={youtube:'YouTube',instagram:'Instagram',tiktok:'TikTok / Buffer'};
 const live=new Set(['queued','preparing','sending','uploading','processing','submitted','scheduled','dispatching']);
 const errors=new Set(['failed','error','partial','uncertain','interrupted','needs_attention','blocked','overdue']);
 let previous=new Map(),seeded=false,snapshot=null,expanded=false,connected=true,unread=0,toastTimer;
 let notices=[];
 try{const stored=JSON.parse(sessionStorage.getItem('bobine-notices')||'[]');if(Array.isArray(stored))notices=stored.filter(n=>typeof n.text==='string'&&typeof n.at==='number').slice(0,30);}catch{}
 function make(tag,cls,text){const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node;}
 function persist(){try{sessionStorage.setItem('bobine-notices',JSON.stringify(notices));}catch{}}
 function notify(text,kind,jobId,calendar=false){
  notices.unshift({text,kind,jobId,calendar,at:Date.now()});notices=notices.slice(0,30);persist();if(!expanded)unread++;
  $('activity-toast').textContent=text;$('activity-toast').hidden=false;clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>{$('activity-toast').hidden=true;},8000);
 }
 function observe(next,key,value,text,jobId,calendar=false){
  next.set(key,value);
  if(seeded&&previous.get(key)!==value&&(value==='done'||value==='published'||errors.has(value)))notify(text,errors.has(value)?'error':'success',jobId,calendar);
 }
 function openJob(jobId,calendar){
  setExpanded(false);
  if(calendar){location.hash='#publications';return;}
  location.hash='#create';window.dispatchEvent(new CustomEvent('studio-open-job',{detail:jobId}));
 }
 function row(title,detail,jobId,calendar=false,kind=''){
  const button=make('button','activity-row '+kind);button.type='button';button.append(make('strong','',title),make('span','',detail));
  button.addEventListener('click',()=>openJob(jobId,calendar));return button;
 }
 function setExpanded(value){expanded=value;panel.hidden=!value;$('activity-toggle').setAttribute('aria-expanded',String(value));if(value)unread=0;render();}
 function update(data){
  snapshot=data;const next=new Map();
  for(const job of data.jobs||[]){
   observe(next,'generation:'+job.id,job.status,job.status==='done'?`Vidéo prête : ${job.title}`:`${status[job.status]||job.status} : ${job.title}`,job.id);
   const report=job.publication||{};
   for(const [platform,target] of Object.entries(report.targets||{}))observe(next,`publication:${job.id}:${platform}`,target.status,`${networks[platform]||platform} · ${status[target.status]||target.status} : ${job.title}`,job.id);
   if(!Object.keys(report.targets||{}).length&&report.status&&report.status!=='not_sent')observe(next,'publication:'+job.id,report.status,`Publication · ${status[report.status]||report.status} : ${job.title}`,job.id);
  }
  for(const plan of data.publication_plans||[])if(['overdue','error','needs_attention'].includes(plan.status))observe(next,'plan:'+plan.id,plan.status,`Planification · ${status[plan.status]} : ${plan.title}`,plan.job_id,true);
  previous=next;seeded=true;render();
 }
 function render(){
  const jobs=snapshot?.jobs||[],running=jobs.find(j=>j.status==='running'),queued=jobs.filter(j=>j.status==='queued');
  const publications=jobs.filter(j=>live.has(j.publication?.status)||Object.values(j.publication?.targets||{}).some(t=>live.has(t.status)));
  const plans=(snapshot?.publication_plans||[]).filter(p=>['waiting','overdue','error','needs_attention','dispatching'].includes(p.status));
  const paused=snapshot?.production?.paused??snapshot?.production_paused??false;
  dock.classList.toggle('is-active',!!running||publications.length>0);dock.classList.toggle('is-offline',!connected);
  $('activity-heading').textContent=!connected?'Connexion interrompue':running?running.title:publications.length?'Publications en cours':queued.length?(paused?'Production en pause':'Vidéos en attente'):'Bobine · activité';
  $('activity-detail').textContent=!connected?'Dernier état connu. Reconnexion automatique.':running?`${stages[running.stage]||'Production'} · ${Math.max(0,Math.min(100,Math.round(Number(running.progress)||0)))} %`:'Génération et diffusion';
  $('activity-counts').textContent=[queued.length?`${queued.length} en attente${paused?' · pause':''}`:'',publications.length?`${publications.length} diffusion(s)`:'',plans.length?`${plans.length} planification(s)`:''].filter(Boolean).join(' · ')||'Aucun traitement en cours';
  const progress=$('activity-progress');progress.hidden=!running;progress.value=Math.max(0,Math.min(100,Number(running?.progress)||0));progress.setAttribute('aria-label',running?'Progression de '+running.title:'Progression de la vidéo');
  $('activity-unread').textContent=unread?String(unread):'';$('activity-unread').hidden=!unread;
  if(!expanded)return;
  // Preserve keyboard focus while a progress snapshot refreshes the open panel.
  const focusIndex=[...$('activity-tasks').children].indexOf(document.activeElement);
  const tasks=$('activity-tasks');tasks.replaceChildren();
  for(const job of jobs.filter(j=>['running','queued'].includes(j.status))){const active=job.status==='running';tasks.append(row(job.title,`Production · ${active?(stages[job.stage]||'En cours')+' · '+Math.round(Number(job.progress)||0)+' %':paused?'En attente · production en pause':'En attente'}`,job.id));}
  for(const job of publications){const report=job.publication;const targets=Object.entries(report.targets||{}).map(([p,t])=>`${networks[p]||p} : ${status[t.status]||t.status}`).join(' · ');tasks.append(row(job.title,'Diffusion · '+(targets||status[report.status]||report.status),job.id));}
  for(const plan of plans){const date=new Date(plan.at*1000).toLocaleString('fr-FR',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'});tasks.append(row(plan.title,`Calendrier · ${status[plan.status]} · ${date}`,plan.job_id,true,errors.has(plan.status)?'error':''));}
  if(!tasks.children.length)tasks.append(make('p','activity-empty','Aucun traitement en cours.'));
  if(focusIndex>=0)tasks.children[focusIndex]?.focus({preventScroll:true});
  const history=$('activity-notices');history.replaceChildren();
  for(const notice of notices){const time=new Date(notice.at).toLocaleTimeString('fr-FR',{hour:'2-digit',minute:'2-digit'});history.append(row(notice.text,time,notice.jobId,notice.calendar,notice.kind));}
  if(!notices.length)history.append(make('p','activity-empty','Les fins de production et résultats de publication apparaîtront ici.'));
  $('activity-clear').disabled=!notices.length;
 }
 $('activity-toggle').addEventListener('click',()=>setExpanded(!expanded));
 $('activity-close').addEventListener('click',()=>{setExpanded(false);$('activity-toggle').focus();});
 $('activity-clear').addEventListener('click',()=>{notices=[];unread=0;persist();render();});
 document.addEventListener('keydown',event=>{if(event.key==='Escape'&&expanded){setExpanded(false);$('activity-toggle').focus();}});
 window.addEventListener('studio-state',event=>{connected=true;update(event.detail);});
 window.addEventListener('studio-connection',event=>{connected=event.detail;render();});
 render();
})();
