(function () {
  'use strict';
  const root = document.querySelector('[data-lesson-demo]');
  if (!root) return;
  const views = [...root.querySelectorAll('[data-demo-view]')];
  const panels = [...root.querySelectorAll('[data-demo-panel]')];
  const stages = [
    {title:'1. Your instructor demonstrates', source:'instructor', caption:'Screen A is shared with you. You watch the demonstration while keeping your own model open.', route:'The instructor’s model appears on your first monitor.', note:'The second screen at each desk keeps the other person’s work in view.'},
    {title:'2. You practise in your own model', source:'student', caption:'Screen B is shared with your instructor. They can follow your actions and help while you work.', route:'Your model appears on the instructor’s second monitor.', note:'You repeat the steps in Tekla. Your instructor watches your shared screen and answers questions.'},
    {title:'3. You review the work together', source:'both', caption:'Both shared screens remain available. Compare the demonstration with your model and get feedback.', route:'Two-way sharing makes feedback part of the lesson.', note:'Your instructor can explain a correction in their model while checking how you apply it in yours.'}
  ];
  let step = 0, playbackFrame = null, stageStarted = 0, currentView = 'map', perspective = 'student';
  function cables() {
    if (currentView !== 'map') return;
    const stage = root.querySelector('[data-cable-stage]');
    const rect = stage.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const svg = root.querySelector('[data-demo-cables]');
    svg.setAttribute('viewBox', '0 0 ' + rect.width + ' ' + rect.height);
    function point(port, right) {
      const box = root.querySelector('[data-port="' + port + '"]').getBoundingClientRect();
      return {x:(right ? box.right : box.left)-rect.left,y:box.top-rect.top+box.height/2};
    }
    const a = point('instructor-own', false), b = point('student-watches', false);
    const c = point('student-own', true), d = point('instructor-watches', true);
    root.querySelector('[data-cable="instructor"]').setAttribute('d',`M ${a.x} ${a.y} C 1 ${a.y}, 1 ${b.y}, ${b.x} ${b.y}`);
    root.querySelector('[data-cable="student"]').setAttribute('d',`M ${c.x} ${c.y} C ${rect.width-1} ${c.y}, ${rect.width-1} ${d.y}, ${d.x} ${d.y}`);
  }
  function paint() {
    const state = stages[step];
    root.querySelector('[data-lesson-title]').textContent = state.title;
    root.querySelector('[data-lesson-caption]').textContent = state.caption;
    root.querySelector('[data-demo-route]').textContent = state.route;
    root.querySelector('[data-demo-guided-note]').textContent = state.note;
    root.querySelector('[data-step-count]').textContent = (step+1) + ' / 3';
    root.querySelector('[data-step-previous]').disabled = step === 0;
    root.querySelector('[data-step-next]').disabled = step === stages.length-1;
    root.querySelectorAll('[data-lesson-step]').forEach(button => {
      if (Number(button.dataset.lessonStep) === step) button.setAttribute('aria-current','step');
      else button.removeAttribute('aria-current');
    });
    root.querySelectorAll('[data-trace]').forEach(button => button.setAttribute('aria-pressed',String(state.source==='both'||button.dataset.trace===state.source)));
    root.querySelectorAll('[data-cable]').forEach(path => path.classList.toggle('is-active',state.source==='both'||path.dataset.cable===state.source));
    requestAnimationFrame(cables);
  }
  function stop() {
    if (playbackFrame !== null) cancelAnimationFrame(playbackFrame);
    playbackFrame = null;
    root.classList.remove('is-playing');
    const button = root.querySelector('[data-play-lesson]');
    button.setAttribute('aria-pressed','false');
    button.querySelector('span').textContent = 'Play explanation';
    button.querySelector('i').className = 'bi bi-play-fill';
  }
  function chooseStep(value) { stop(); step = value; paint(); }
  function view(name, focus=false) {
    currentView = name;
    views.forEach(button => {
      const active = button.dataset.demoView === name;
      button.setAttribute('aria-selected',String(active));
      button.tabIndex = active ? 0 : -1;
      if (active && focus) button.focus();
    });
    panels.forEach(panel => { panel.hidden = panel.dataset.demoPanel !== name; });
    paint();
  }
  views.forEach((button,index) => {
    button.addEventListener('click',() => view(button.dataset.demoView));
    button.addEventListener('keydown',event => {
      let next;
      if(event.key==='ArrowRight') next=(index+1)%views.length;
      else if(event.key==='ArrowLeft') next=(index+views.length-1)%views.length;
      else if(event.key==='Home') next=0;
      else if(event.key==='End') next=views.length-1;
      else return;
      event.preventDefault(); view(views[next].dataset.demoView,true);
    });
  });
  root.querySelectorAll('[data-trace]').forEach(button => button.addEventListener('click',()=>chooseStep(button.dataset.trace==='instructor'?0:1)));
  root.querySelectorAll('[data-lesson-step]').forEach(button => button.addEventListener('click',()=>chooseStep(Number(button.dataset.lessonStep))));
  root.querySelector('[data-step-previous]').addEventListener('click',()=>chooseStep(Math.max(0,step-1)));
  root.querySelector('[data-step-next]').addEventListener('click',()=>chooseStep(Math.min(2,step+1)));
  root.querySelector('[data-play-lesson]').addEventListener('click',()=>{
    if (playbackFrame !== null) { stop(); return; }
    const button=root.querySelector('[data-play-lesson]');
    root.classList.add('is-playing'); button.setAttribute('aria-pressed','true');
    button.querySelector('span').textContent='Pause explanation'; button.querySelector('i').className='bi bi-pause-fill';
    stageStarted=performance.now();
    function advance(now) {
      if (now-stageStarted>=4500) {
        step=(step+1)%stages.length;
        stageStarted=now;
        paint();
      }
      playbackFrame=requestAnimationFrame(advance);
    }
    playbackFrame=requestAnimationFrame(advance);
  });
  const perspectiveCards=[...root.querySelector('[data-perspective-screens]').querySelectorAll('.demo-screen')];
  root.querySelectorAll('[data-perspective]').forEach(button => button.addEventListener('click',()=>{
    perspective=button.dataset.perspective;
    root.querySelectorAll('[data-perspective]').forEach(item=>item.setAttribute('aria-pressed',String(item.dataset.perspective===perspective)));
    const teacher=perspective==='instructor';
    root.querySelector('[data-perspective-title]').textContent=teacher?'At the instructor’s desk':'At your desk';
    root.querySelector('[data-perspective-note]').textContent=teacher?'Your instructor demonstrates in their own model on one monitor and follows your shared screen on the other.':'Watch the demonstration on one monitor and work in your own model on the other.';
    const labels=teacher?['Their own Tekla model','Watching your shared screen']:['Instructor’s shared screen','Your own Tekla model'];
    perspectiveCards.forEach((card,index)=>{card.querySelector('.demo-screen__heading > span:not(.demo-source)').textContent=labels[index];card.setAttribute('aria-label',labels[index]+'. Trace this shared screen');});
  }));
  new ResizeObserver(()=>requestAnimationFrame(cables)).observe(root.querySelector('[data-cable-stage]'));
  new IntersectionObserver(entries=>{if(!entries[0].isIntersecting)stop();}).observe(root);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  view('map');
})();
