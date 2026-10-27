"""Interactive explanation of the real two-monitor training workflow."""
MODEL = '/local/templates/top_com/assets/img/portfolio/03.png.webp'


def screen(source, label, monitor, port='', small=False):
    return f'''<button type="button" class="demo-screen demo-screen--{source}" data-trace="{source}" {f'data-port="{port}"' if port else ''} aria-label="{label}. Trace this shared screen" aria-pressed="false">
      <span class="demo-screen__heading"><i class="bi bi-display" aria-hidden="true"></i><span>{label}</span><span class="demo-source" aria-hidden="true">{'A' if source == 'instructor' else 'B'}</span></span>
      <span class="demo-screen__picture"><img src="{MODEL}" width="913" height="359" loading="lazy" decoding="async" alt="Structural model from the TopEngineer Tekla Structures project portfolio"></span>
      <span class="demo-screen__monitor">Monitor {monitor}</span>
    </button>'''


def markup():
    return f'''<section class="lesson-demo" data-lesson-demo aria-label="Explore two-way screen sharing">
    <nav class="lesson-demo__tabs" role="tablist" aria-label="Ways to explore the lesson">
      <button type="button" role="tab" id="lesson-view-map" aria-controls="lesson-panel-map" aria-selected="true" data-demo-view="map">Two-way view</button>
      <button type="button" role="tab" id="lesson-view-steps" aria-controls="lesson-panel-steps" aria-selected="false" tabindex="-1" data-demo-view="steps">Step by step</button>
      <button type="button" role="tab" id="lesson-view-perspective" aria-controls="lesson-panel-perspective" aria-selected="false" tabindex="-1" data-demo-view="perspective">My view</button>
    </nav>
    <div id="lesson-panel-map" class="lesson-demo__panel" role="tabpanel" aria-labelledby="lesson-view-map" data-demo-panel="map">
      <div class="demo-map" data-cable-stage>
        <svg class="demo-cables" aria-hidden="true" focusable="false" data-demo-cables><defs>
          <marker id="lesson-blue-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#1764a3"/></marker>
          <marker id="lesson-teal-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#187b70"/></marker>
        </defs><path class="demo-cable demo-cable--instructor" data-cable="instructor" marker-end="url(#lesson-blue-arrow)"/><path class="demo-cable demo-cable--student" data-cable="student" marker-end="url(#lesson-teal-arrow)"/></svg>
        <section class="demo-workspace"><h3><i class="bi bi-person-video3" aria-hidden="true"></i> Your instructor <span>2 monitors</span></h3><div class="demo-workspace__screens">
          {screen('instructor', 'Their own Tekla model', 1, 'instructor-own')}
          {screen('student', 'Watching your screen', 2, 'instructor-watches')}
        </div></section>
        <div class="demo-map__connection"><i class="bi bi-arrow-down-up" aria-hidden="true"></i><span>Both screens are shared</span></div>
        <section class="demo-workspace"><h3><i class="bi bi-person-workspace" aria-hidden="true"></i> You <span>2 monitors</span></h3><div class="demo-workspace__screens">
          {screen('instructor', 'Watching the instructor', 1, 'student-watches')}
          {screen('student', 'Your own Tekla model', 2, 'student-own')}
        </div></section>
      </div>
      <p class="lesson-demo__hint">Select a screen to follow its matching view.</p>
    </div>
    <div id="lesson-panel-steps" class="lesson-demo__panel" role="tabpanel" aria-labelledby="lesson-view-steps" data-demo-panel="steps" hidden>
      <div class="demo-stepper" aria-label="Lesson stages">
        <button type="button" data-lesson-step="0" aria-current="step"><i class="bi bi-eye" aria-hidden="true"></i>Watch</button>
        <button type="button" data-lesson-step="1"><i class="bi bi-mouse" aria-hidden="true"></i>Practise</button>
        <button type="button" data-lesson-step="2"><i class="bi bi-chat-dots" aria-hidden="true"></i>Review</button>
      </div>
      <div class="demo-guided" data-guided-stage>
        <p class="demo-guided__route" data-demo-route>The instructor’s model appears on your first monitor.</p>
        <div class="demo-guided__screens">
          <div><p class="demo-guided__owner"><i class="bi bi-person-video3" aria-hidden="true"></i> Instructor</p>{screen('instructor', 'Demonstrating in Tekla', 1)}</div>
          <div><p class="demo-guided__owner"><i class="bi bi-person-workspace" aria-hidden="true"></i> You</p>{screen('student', 'Repeating the steps', 2)}</div>
        </div>
        <div class="demo-guided__sharing"><i class="bi bi-arrow-left-right" aria-hidden="true"></i><p data-demo-guided-note>The second screen at each desk keeps the other person’s work in view.</p></div>
      </div>
      <div class="demo-step-controls"><button type="button" class="btn btn-outline-primary btn-sm" data-step-previous>Previous</button><span data-step-count>1 / 3</span><button type="button" class="btn btn-outline-primary btn-sm" data-step-next>Next</button></div>
    </div>
    <div id="lesson-panel-perspective" class="lesson-demo__panel" role="tabpanel" aria-labelledby="lesson-view-perspective" data-demo-panel="perspective" hidden>
      <div class="demo-perspective-switch" role="group" aria-label="Whose monitors to show"><button type="button" data-perspective="student" aria-pressed="true">Your view</button><button type="button" data-perspective="instructor" aria-pressed="false">Instructor’s view</button></div>
      <h3 class="demo-perspective-title" data-perspective-title>At your desk</h3>
      <div class="demo-perspective-screens" data-perspective-screens>
        {screen('instructor', 'Instructor’s shared screen', 1)}
        {screen('student', 'Your own Tekla model', 2)}
      </div>
      <p class="demo-perspective-note" data-perspective-note>Watch the demonstration on one monitor and work in your own model on the other.</p>
    </div>
    <div class="lesson-demo__explanation" aria-live="polite" aria-atomic="true"><strong data-lesson-title>1. Your instructor demonstrates</strong><p data-lesson-caption>Screen A is shared with you. You watch the demonstration while keeping your own model open.</p></div>
    <div class="lesson-demo__controls"><button type="button" class="btn btn-outline-primary btn-sm" data-play-lesson aria-pressed="false"><i class="bi bi-play-fill" aria-hidden="true"></i><span>Play explanation</span></button><span class="lesson-demo__legend"><span><b class="demo-key demo-key--instructor">A</b> Instructor</span><span><b class="demo-key demo-key--student">B</b> You</span></span></div>
    <p class="lesson-demo__disclaimer">Interactive illustration using a TopEngineer project model.</p>
    </section>'''
