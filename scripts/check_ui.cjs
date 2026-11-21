/* DOM flow checks with a mocked local API: no browser service or model launch. */
const {JSDOM}=require('jsdom');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const dom=new JSDOM(fs.readFileSync(path.join(root,'studio/static/index.html'),'utf8'),{url:'http://127.0.0.1:8511/',runScripts:'outside-only'});
const w=dom.window,$=id=>w.document.getElementById(id),requests=[];
w.TextDecoder=TextDecoder;w.setInterval=()=>0;w.scrollTo=()=>{};
w.HTMLElement.prototype.scrollIntoView=function(){};w.HTMLMediaElement.prototype.pause=function(){};
let state={settings:{theme:'dark',duration:90,format:'reel',voice:'Narrateur-Homme-01'},jobs:[],batches:[]};
let sequence=0,releasePreview=null,delayPreview=false;
function summarize(batch){const jobs=batch.job_ids.map(id=>state.jobs.find(j=>j.id===id));const counts=Object.fromEntries(['queued','running','done','failed','cancelled','interrupted'].map(s=>[s,jobs.filter(j=>j.status===s).length]));batch.counts=counts;batch.total=jobs.length;batch.finished=jobs.length-counts.queued-counts.running;batch.progress=Math.round((batch.finished*100+jobs.filter(j=>j.status==='running').reduce((n,j)=>n+j.progress,0))/jobs.length);batch.status=counts.running?'running':counts.queued?'queued':counts.done===jobs.length?'done':'finished';}
function response(data,status=200){return {ok:status<400,status,json:async()=>structuredClone(data)};}
w.fetch=async(url,options={})=>{
 const body=options.body?JSON.parse(options.body):null;requests.push({url,body});
 if(url==='/api/state'){state.batches.forEach(summarize);return response(state);}
 if(url==='/api/health')return response({ready:true,llm:true,voice:true,whisper:true});
 if(url==='/api/batches/preview'){
  if(delayPreview){delayPreview=false;await new Promise(resolve=>releasePreview=resolve);}
  if(body.csv.includes('INVALID'))return response({detail:'Ligne 3 : vérifier duration.'},422);
  return response({total:2,lines:[2,3],items:['Premier CSV','Second CSV'].map(title=>({title,description:'Une explication concrète et simple.',...body.defaults}))});
 }
 if(url==='/api/batches'){
  const id='batch-'+(++sequence),items=body.items||['Premier CSV','Second CSV'].map(title=>({title,description:'Une explication concrète et simple.'}));
  const jobs=items.map((item,i)=>({id:'job-'+(++sequence),...body.defaults,...item,status:'queued',stage:'queued',progress:0,message:'En attente',created:Date.now()/1000,batch_id:id,batch_index:i+1}));
  const batch={id,name:body.name||'Lot de test',job_ids:jobs.map(j=>j.id),created:Date.now()/1000};state.jobs.unshift(...jobs);state.batches.unshift(batch);state.settings=body.defaults;summarize(batch);return response(batch,201);
 }
 if(url.endsWith('/cancel-pending')){const id=url.split('/')[3];state.jobs.filter(j=>j.batch_id===id&&j.status==='queued').forEach(j=>j.status='cancelled');const batch=state.batches.find(b=>b.id===id);summarize(batch);return response(batch);}
 throw new Error('Requête inattendue : '+url);
};
const settle=async()=>{for(let i=0;i<8;i++)await new Promise(resolve=>setImmediate(resolve));};
const event=(node,type)=>node.dispatchEvent(new w.Event(type,{bubbles:true,cancelable:true}));
async function upload(text){const bytes=new TextEncoder().encode(text);Object.defineProperty($('csv-file'),'files',{configurable:true,value:[{name:'videos.csv',size:bytes.length,arrayBuffer:async()=>bytes.buffer}]});event($('csv-file'),'change');await settle();}

(async()=>{
 w.eval(fs.readFileSync(path.join(root,'studio/static/app.js'),'utf8'));await settle();
 assert.equal($('generate').disabled,false);
 $('mode-batch').click();assert.equal($('title').required,false);assert.equal($('batch-items').children.length,2);
 const rows=[...$('batch-items').children];rows[0].querySelector('.item-title').value='<svg onload=alert(1)> Sujet A';rows[1].querySelector('.item-title').value='Sujet B';
 for(const row of rows)row.querySelector('textarea').value='Une description suffisamment détaillée.';
 rows[0].querySelector('.move-down').click();assert.equal($('batch-items').firstElementChild,rows[1]);
 w.document.querySelector('input[name=theme][value=light]').checked=true;event(w.document.querySelector('input[name=theme][value=light]'),'change');
 w.document.querySelector('input[name=format][value=standard]').checked=true;$('duration').value=45;
 assert.equal($('form').checkValidity(),true);event($('form'),'submit');await settle();
 const sent=requests.find(r=>r.url==='/api/batches').body;assert.deepEqual(sent.items.map(i=>i.title),['Sujet B','<svg onload=alert(1)> Sujet A']);assert.equal(sent.defaults.duration,45);assert.equal(sent.defaults.theme,'light');assert.equal(sent.defaults.voice,'Narrateur-Homme-01');
 assert.equal($('batch-monitor').classList.contains('hidden'),false);assert.equal($('batch-rows').children.length,2);assert.equal(w.document.querySelector('svg'),null);
 const first=state.jobs[0];first.status='running';first.stage='voice';first.progress=50;await w.refresh();assert.match($('batch-summary').textContent,/1 en cours/);assert.equal($('batch-rows').firstElementChild.querySelector('progress').value,50);
 $('batch-rows').children[1].querySelector('button').click();assert.equal($('follow-batch').checked,false);await w.refresh();assert.equal($('preview-title').textContent,state.jobs[1].title);
 $('cancel-batch').click();await settle();assert.equal(first.status,'running');assert.equal(state.jobs[1].status,'cancelled');
 first.status='done';first.stage='done';first.progress=100;await w.refresh();assert.match($('batch-summary').textContent,/2 \/ 2 traitées/);
 $('mode-csv').click();assert.equal(rows[0].querySelector('input').required,false);
 await upload('titre;description\nPremier;Une description assez longue');$('validate-csv').click();await settle();assert.equal($('csv-preview').querySelectorAll('tbody tr').length,2);assert.equal($('generate').disabled,false);
 $('duration').value=60;event($('duration'),'input');assert.equal($('generate').disabled,true);assert.equal($('csv-preview').classList.contains('hidden'),true);
 $('validate-csv').click();await settle();assert.equal($('generate').disabled,false);event($('form'),'submit');await settle();const csvRequest=requests.filter(r=>r.url==='/api/batches').at(-1);assert.ok(csvRequest.body.csv);assert.equal(csvRequest.body.defaults.duration,60);
 await upload('INVALID');$('validate-csv').click();await settle();assert.match($('csv-message').textContent,/Ligne 3/);assert.equal($('generate').disabled,true);
 await upload('titre;description\nAutre;Une autre description longue');delayPreview=true;$('validate-csv').click();await settle();$('duration').value=75;event($('duration'),'input');releasePreview();await settle();assert.equal($('generate').disabled,true);
 // Changing common settings must automatically validate again, even on the final step.
 const batchesBeforeAuto=requests.filter(r=>r.url==='/api/batches').length;
 await new Promise(resolve=>w.setTimeout(resolve,350));await settle();
 assert.equal($('generate').disabled,false,'Changed defaults must not leave CSV permanently disabled');
 assert.equal(requests.filter(r=>r.url==='/api/batches/preview').at(-1).body.defaults.duration,75);
 assert.equal(requests.filter(r=>r.url==='/api/batches').length,batchesBeforeAuto,'Validation must never start production');
 w.studioSocial={generationSettings:()=>({auto_publish:true,publish_platforms:[]})};w.invalidateCSV();
 await new Promise(resolve=>w.setTimeout(resolve,350));await settle();
 assert.equal($('generate').disabled,false,'Optional publication without a network must not block CSV generation');
 w.studioSocial={generationSettings:()=>({auto_publish:true,publish_platforms:['tiktok']})};w.invalidateCSV();
 await new Promise(resolve=>w.setTimeout(resolve,350));await settle();assert.equal($('generate').disabled,false);
 await upload('titre;description\nAutomatique;Une description suffisamment détaillée');
 await new Promise(resolve=>w.setTimeout(resolve,350));await settle();assert.equal($('generate').disabled,false,'Imported CSV validates automatically');
 await upload('INVALID');await new Promise(resolve=>w.setTimeout(resolve,350));await settle();assert.equal($('generate').disabled,true);assert.match($('generate').title,/Ligne 3/);assert.equal($('generate').getAttribute('aria-busy'),'false');assert.equal($('submit-note').classList.contains('generation-blocked'),true);
 $('mode-batch').click();$('mode-batch').focus();$('mode-batch').dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));assert.equal($('mode-csv').getAttribute('aria-selected'),'true');assert.equal($('mode-batch').tabIndex,-1);
 $('voice').value='Duo-Homme-Femme';assert.equal(w.settings().voice,'Duo-Homme-Femme');w.studioSocial.setDefaults=()=>{};w.setForm({...w.settings(),theme:'carnet'});assert.equal(w.settings().theme,'carnet');assert.equal($('preview-film').classList.contains('carnet-film'),true);assert.equal($('preview-theme').textContent,'Carnet animé');w.selectJob(state.jobs[0]);$('follow-batch').checked=true;event(w.document.querySelector('[name=theme][value=carnet]'),'change');await w.refresh();assert.equal($('follow-batch').checked,false);assert.equal($('preview-theme').textContent,'Carnet animé');assert.equal($('video').classList.contains('hidden'),true);
 console.log('OK : saisie, ordre, réglages communs, CSV, erreurs, suivi, annulation, protection DOM et navigation clavier.');dom.window.close();
})().catch(error=>{console.error(error);dom.window.close();process.exitCode=1;});
