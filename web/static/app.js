/* ==========================================================================
   BAAY-FAAL COMMAND CENTER FRONTEND JS (Vanilla Native)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Navigation Tabs
  const navItems = document.querySelectorAll('.nav-item');
  const tabPages = document.querySelectorAll('.tab-page');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetTab = item.getAttribute('data-tab');

      navItems.forEach(i => i.classList.remove('active'));
      tabPages.forEach(p => p.classList.remove('active'));

      item.classList.add('active');
      const targetElement = document.getElementById(targetTab);
      if (targetElement) {
        targetElement.classList.add('active');
      }

      if (targetTab === 'tab-memory') {
        loadMemoryLogs();
      }
      if (targetTab === 'tab-learn') {
        loadLearnStatus();
      }
    });
  });

  // Controls & Elements
  const cmdInput = document.getElementById('cmd-input');
  const btnSubmit = document.getElementById('btn-submit');
  const btnClear = document.getElementById('btn-clear');
  const voiceToggle = document.getElementById('voice-toggle');
  const consoleStream = document.getElementById('console-stream');
  const btnRefreshMemory = document.getElementById('btn-refresh-memory');

  // Learn Tech Elements & 2-Step Workflow
  const btnVerifyCode = document.getElementById('btn-verify-code');
  const codeEditor = document.getElementById('code-editor');
  const verifyResultBox = document.getElementById('verify-result-box');
  const btnStartPython = document.getElementById('btn-start-python');
  const courseCardBox = document.getElementById('course-card-box');
  const courseModuleBadge = document.getElementById('course-module-badge');
  const courseHtmlContent = document.getElementById('course-html-content');
  const btnPassToCode = document.getElementById('btn-pass-to-code');
  const editorWorkspaceBox = document.getElementById('editor-workspace-box');
  const exerciseSubjectTitle = document.getElementById('exercise-subject-title');
  const exerciseObjectiveBox = document.getElementById('exercise-objective-box');
  const lessonSelectDropdown = document.getElementById('lesson-select-dropdown');

  let currentLessonData = null;

  // Étape 1 : Chargement et affichage du Cours Flash & Théorie (avec révision par index)
  async function loadActiveLesson(requestedIndex = null) {
    try {
      let url = '/api/learn/lesson?tech=python';
      if (requestedIndex !== null) {
        url += `&index=${requestedIndex}`;
      }
      const res = await fetch(url);
      const data = await res.json();
      if (data.success && data.lesson) {
        currentLessonData = data.lesson;
        displayFlashCourse(currentLessonData);

        if (lessonSelectDropdown && data.all_lessons) {
          lessonSelectDropdown.innerHTML = '';
          data.all_lessons.forEach(l => {
            const opt = document.createElement('option');
            opt.value = l.index;
            const statusTag = l.unlocked ? '[DÉBLOQUÉ]' : '[VERROUILLÉ]';
            opt.textContent = `${statusTag} ${l.title || l.exercise_title}`;
            opt.style.background = '#1e293b';
            opt.style.color = l.unlocked ? '#f8fafc' : '#64748b';
            opt.disabled = !l.unlocked;
            if (l.index === (data.lesson.exercise_number - 1 + (data.lesson.module_number - 1)*3)) {
              opt.selected = true;
            }
            lessonSelectDropdown.appendChild(opt);
          });
        }
      }
    } catch (e) {
      console.warn('Erreur de chargement de la leçon :', e);
    }
  }

  if (lessonSelectDropdown) {
    lessonSelectDropdown.addEventListener('change', (e) => {
      const selectedIdx = parseInt(e.target.value, 10);
      loadActiveLesson(selectedIdx);
    });
  }

  function displayFlashCourse(lesson) {
    if (!lesson) return;
    if (courseModuleBadge) courseModuleBadge.textContent = lesson.module_title || "MODULE 1";
    if (courseHtmlContent) courseHtmlContent.innerHTML = lesson.course_content || `<h3>${escapeHtml(lesson.title)}</h3><p>${escapeHtml(lesson.objective)}</p>`;
    if (btnPassToCode) {
      btnPassToCode.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg> <span>Passer au Code (${escapeHtml(lesson.exercise_title || 'Exercice')})</span>`;
    }
    if (courseCardBox) courseCardBox.style.display = 'block';
    if (editorWorkspaceBox) editorWorkspaceBox.style.display = 'none';
    if (courseCardBox) courseCardBox.scrollIntoView({ behavior: 'smooth' });
  }

  // Étape 2 : Transition du Cours Flash vers l'Éditeur de Code Vierge
  if (btnPassToCode) {
    btnPassToCode.addEventListener('click', () => {
      if (!currentLessonData) return;
      if (exerciseSubjectTitle) exerciseSubjectTitle.textContent = currentLessonData.exercise_title || currentLessonData.title;
      if (exerciseObjectiveBox) {
        exerciseObjectiveBox.innerHTML = `<strong>CAHIER DES CHARGES :</strong> ${escapeHtml(currentLessonData.objective)}`;
      }
      if (codeEditor) codeEditor.value = currentLessonData.starter_code || "# Écrivez votre code Python ci-dessous :\n\n";
      if (editorWorkspaceBox) editorWorkspaceBox.style.display = 'block';
      if (verifyResultBox) {
        verifyResultBox.innerHTML = '<div style="color: var(--text-muted)">Rédigez votre solution ci-dessus puis cliquez sur <strong>"Vérifier mon Code"</strong>.</div>';
      }
      if (editorWorkspaceBox) editorWorkspaceBox.scrollIntoView({ behavior: 'smooth' });
    });
  }

  // Support Indentation Tab (4 espaces) dans les zones de texte
  function enableTabIndentation(textarea) {
    if (!textarea) return;
    textarea.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const val = textarea.value;
        textarea.value = val.substring(0, start) + "    " + val.substring(end);
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      }
    });
  }

  if (codeEditor) enableTabIndentation(codeEditor);
  if (cmdInput) enableTabIndentation(cmdInput);

  if (btnStartPython) {
    btnStartPython.addEventListener('click', loadActiveLesson);
  }

  // Clic sur les cartes verrouillées -> Rappel Règle d'Acier Jëf Jël
  const lockedCards = document.querySelectorAll('.locked-card');
  lockedCards.forEach(card => {
    card.addEventListener('click', () => {
      alert("[RÈGLE D'ACIER JËF JËL]\n\nTant que le parcours Python n'est pas validé à 100% par le Boss de Fin de Parcours, il est STRICTEMENT INTERDIT de bifurquer sur d'autres technologies !");
    });
  });

  // Module KADDOU (Commande Vocale par Micro Web Speech API)
  const btnMicListen = document.getElementById('btn-mic-listen');
  const micBtnLabel = document.getElementById('mic-btn-label');
  let recognition = null;
  let isListening = false;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.lang = 'fr-FR';
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onstart = () => {
      isListening = true;
      if (micBtnLabel) micBtnLabel.textContent = "Écoute en cours...";
      if (btnMicListen) {
        btnMicListen.style.borderColor = "var(--accent-rose)";
        btnMicListen.style.color = "var(--accent-rose)";
      }
    };

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      // Correction phonétique automatique pour Yité Cleaner et termes Baay-Faal
      let normalized = transcript;
      if (/youtube|l'idée|ité|unité|yite/i.test(normalized)) {
        normalized = normalized.replace(/youtube|l'idée|ité|unité|yite/gi, "Yité Cleaner");
      }
      if (cmdInput) {
        cmdInput.value = normalized;
      }
    };

    recognition.onerror = (event) => {
      console.warn("Erreur reconnaissance vocale :", event.error);
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        alert("Permission micro refusée. Veuillez cliquer sur l'icône de cadenas / microphone dans la barre d'adresse de votre navigateur pour autoriser le micro sur http://localhost:8000.");
      } else if (event.error === 'no-speech') {
        console.log("Aucune parole détectée.");
      } else if (event.error !== 'aborted') {
        alert("Erreur de reconnaissance vocale : " + event.error);
      }
      stopListening();
    };

    recognition.onend = () => {
      stopListening();
      if (cmdInput && cmdInput.value.trim().length > 0) {
        submitInstruction();
      }
    };
  } else {
    console.warn("API Web Speech non disponible sur ce navigateur.");
  }

  function stopListening() {
    isListening = false;
    if (micBtnLabel) micBtnLabel.textContent = "Commande Vocale (Kaddou)";
    if (btnMicListen) {
      btnMicListen.style.borderColor = "var(--accent-cyan)";
      btnMicListen.style.color = "var(--accent-cyan)";
    }
  }

  if (btnMicListen) {
    btnMicListen.addEventListener('click', async () => {
      if (!SpeechRecognition || !recognition) {
        alert("Reconnaissance vocale non disponible sur ce navigateur. Veuillez utiliser Google Chrome ou Microsoft Edge.");
        return;
      }
      if (isListening) {
        recognition.stop();
      } else {
        try {
          if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            await navigator.mediaDevices.getUserMedia({ audio: true });
          }
          recognition.start();
        } catch (err) {
          console.warn("Accès au microphone refusé ou indisponible :", err);
          alert("Accès au microphone refusé. Autorisez le micro dans la barre d'adresse de votre navigateur.");
        }
      }
    });
  }

  // Load Learn Status
  async function loadLearnStatus() {
    try {
      const res = await fetch('/api/learn/status');
      const data = await res.json();
      if (data.success && data.techs) {
        data.techs.forEach(t => {
          if (t.tech === 'python') {
            const fill = document.getElementById('python-progress-fill');
            const txt = document.getElementById('python-progress-text');
            if (fill) fill.style.width = `${t.percent}%`;
            if (txt) txt.textContent = `${t.percent}% (Exercice ${t.level}/12)`;
          }
        });
      }
    } catch (e) {
      console.warn('Erreur chargement statut apprentissage :', e);
    }
  }

  const btnReviewCode = document.getElementById('btn-review-code');

  function renderCodeReviewCard(review) {
    if (!review) return '';
    const score = review.score !== undefined ? review.score : 0;
    let scoreColor = '#10b981';
    let scoreBg = 'rgba(16, 185, 129, 0.15)';
    if (score < 5.0) {
      scoreColor = '#ef4444';
      scoreBg = 'rgba(239, 68, 68, 0.15)';
    } else if (score < 8.0) {
      scoreColor = '#f59e0b';
      scoreBg = 'rgba(245, 158, 11, 0.15)';
    }

    let pep8Html = '';
    if (review.pep8_issues && review.pep8_issues.length > 0) {
      pep8Html = `<div style="margin-top: 6px; color: var(--accent-amber);">
        <strong>Formotage & Conventions PEP 8 :</strong>
        <ul style="margin: 4px 0 0 16px; padding: 0;">
          ${review.pep8_issues.map(i => `<li>${escapeHtml(i)}</li>`).join('')}
        </ul>
      </div>`;
    }

    let secHtml = '';
    if (review.security_issues && review.security_issues.length > 0) {
      secHtml = `<div style="margin-top: 6px; color: #ef4444;">
        <strong>Sécurité / Failles :</strong>
        <ul style="margin: 4px 0 0 16px; padding: 0;">
          ${review.security_issues.map(i => `<li>${escapeHtml(i)}</li>`).join('')}
        </ul>
      </div>`;
    }

    let recomHtml = '';
    if (review.recommendations && review.recommendations.length > 0) {
      recomHtml = `<div style="margin-top: 6px; color: var(--text-secondary);">
        <strong>Conseils Tech Lead :</strong> ${review.recommendations.map(r => escapeHtml(r)).join(' ')}
      </div>`;
    }

    return `
      <div style="margin-top: 12px; padding: 12px; background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border-color); border-radius: 6px; text-align: left;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 6px; margin-bottom: 8px;">
          <span style="font-weight: 700; color: var(--accent-cyan); display: flex; align-items: center; gap: 6px;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            REVUE DE CODE & NOTE D'INGÉNIEUR
          </span>
          <span style="font-size: 1rem; font-weight: 800; padding: 3px 12px; border-radius: 12px; background: ${scoreBg}; color: ${scoreColor}; border: 1px solid ${scoreColor};">
            Note : ${score} / 10
          </span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.85rem; color: var(--text-primary); margin-bottom: 6px;">
          <div>⚡ <strong>Complexité :</strong> <code style="color: var(--accent-amber); font-weight: 700;">${escapeHtml(review.complexity || 'O(1)')}</code></div>
          <div>📊 <strong>Métriques :</strong> ${review.metrics?.lines_count || 0} lignes, Profondeur boucles : ${review.metrics?.max_loop_depth || 0}</div>
        </div>
        ${pep8Html}
        ${secHtml}
        ${recomHtml}
      </div>
    `;
  }

  // Action dédiée : Seule la Revue de Code & Note /10
  if (btnReviewCode) {
    btnReviewCode.addEventListener('click', async () => {
      const userCode = codeEditor.value.trim();
      if (!userCode) return;

      verifyResultBox.innerHTML = '<div style="color: var(--accent-cyan)">[ANALYSE STATIQUE] Exécution du Code Reviewer par l\'Agent Baay-Faal...</div>';

      try {
        const res = await fetch('/api/learn/review', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ language: 'python', code: userCode })
        });
        const data = await res.json();

        if (data.success && data.review) {
          verifyResultBox.innerHTML = renderCodeReviewCard(data.review);
        } else {
          verifyResultBox.innerHTML = `<div class="verify-error">Erreur de revue de code : ${escapeHtml(data.error || 'Erreur inconnue')}</div>`;
        }
      } catch (e) {
        verifyResultBox.innerHTML = `<div class="verify-error">Erreur réseau : ${escapeHtml(e.message)}</div>`;
      }
    });
  }

  // Verify Code Submission + Auto Review Score
  if (btnVerifyCode) {
    btnVerifyCode.addEventListener('click', async () => {
      const userCode = codeEditor.value.trim();
      if (!userCode) return;

      verifyResultBox.innerHTML = '<div style="color: var(--accent-indigo)">[VÉRIFICATION & REVIEW] Exécution du banc de tests et du Code Reviewer...</div>';

      try {
        const lessonIdx = currentLessonData ? ((currentLessonData.exercise_number - 1) + (currentLessonData.module_number - 1) * 3) : 0;
        const [verifyRes, reviewRes] = await Promise.all([
          fetch('/api/learn/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tech: 'python', code: userCode, index: lessonIdx })
          }),
          fetch('/api/learn/review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ language: 'python', code: userCode })
          })
        ]);

        const data = await verifyRes.json();
        const reviewData = await reviewRes.json();
        const reviewCardHtml = reviewData.success ? renderCodeReviewCard(reviewData.review) : '';

        if (data.success) {
          let nextHtml = '';
          if (data.next_lesson) {
            currentLessonData = data.next_lesson;
            nextHtml = `<div style="margin-top: 10px; padding: 10px; background: rgba(99, 102, 241, 0.15); border-radius: 4px;">
              <strong>[NOUVELLE ÉTAPE DÉVERROUILLÉE] : ${escapeHtml(data.next_lesson.exercise_title || data.next_lesson.title)}</strong><br>
              <em>Le cours de la prochaine étape est prêt ci-dessus !</em>
            </div>`;
            displayFlashCourse(currentLessonData);
          }
          verifyResultBox.innerHTML = `
            <div class="verify-success">
              <strong>[TESTS PASSÉS AU VERT — ACCORD DU MENTOR]</strong><br>
              Sortie du programme :<br>
              <pre>${escapeHtml(data.stdout || 'Programme exécuté avec succès.')}</pre>
              <div style="margin-top: 8px; font-weight: 600;">Progression globale mise à jour : ${data.new_percent}%</div>
              ${nextHtml}
            </div>
            ${reviewCardHtml}
          `;
          loadLearnStatus();
        } else {
          let hintHtml = data.hint ? `<div style="margin-top: 8px; color: var(--accent-amber);"><strong>Indice du Mentor :</strong> ${escapeHtml(data.hint)}</div>` : '';
          verifyResultBox.innerHTML = `
            <div class="verify-error">
              <strong>[BANC DE TESTS ÉCHOUÉ — CODE REVIEW]</strong><br>
              <pre>${escapeHtml(data.stderr || data.error || 'Erreur d\'exécution.')}</pre>
              ${hintHtml}
            </div>
            ${reviewCardHtml}
          `;
        }
      } catch (e) {
        verifyResultBox.innerHTML = `<div class="verify-error">Erreur réseau : ${escapeHtml(e.message)}</div>`;
      }
    });
  }

  // Submit Execution
  async function submitInstruction() {
    const goal = cmdInput.value.trim();
    if (!goal) return;

    // Clear empty state if present
    const emptyState = consoleStream.querySelector('.empty-state');
    if (emptyState) {
      consoleStream.innerHTML = '';
    }

    // Append Goal Block
    const goalEl = document.createElement('div');
    goalEl.className = 'log-step';
    goalEl.innerHTML = `
      <div class="log-thought">OBJECTIF SOUMIS : ${escapeHtml(goal)}</div>
      <div class="log-action">Réflexion autonome de l'agent en cours...</div>
    `;
    consoleStream.appendChild(goalEl);
    consoleStream.scrollTop = consoleStream.scrollHeight;

    btnSubmit.disabled = true;
    btnSubmit.style.opacity = '0.5';

    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal: goal,
          voice: voiceToggle.checked
        })
      });

      const data = await response.json();

      if (data.success) {
        const finalEl = document.createElement('div');
        finalEl.className = 'log-final';
        finalEl.innerHTML = `
          <strong>[RÉPONSE FINALE BAAY-AGENT]</strong><br>
          <pre>${escapeHtml(data.answer)}</pre>
        `;
        consoleStream.appendChild(finalEl);
      } else {
        const errEl = document.createElement('div');
        errEl.className = 'log-step';
        errEl.style.borderLeftColor = 'var(--accent-rose)';
        errEl.innerHTML = `<div class="log-action" style="color: var(--accent-rose)">ERREUR : ${escapeHtml(data.error)}</div>`;
        consoleStream.appendChild(errEl);
      }
    } catch (err) {
      const errEl = document.createElement('div');
      errEl.className = 'log-step';
      errEl.style.borderLeftColor = 'var(--accent-rose)';
      errEl.innerHTML = `<div class="log-action" style="color: var(--accent-rose)">ÉCHEC RÉSEAU : ${escapeHtml(err.message)}</div>`;
      consoleStream.appendChild(errEl);
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.style.opacity = '1';
      consoleStream.scrollTop = consoleStream.scrollHeight;
    }
  }

  btnSubmit.addEventListener('click', submitInstruction);

  cmdInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
      submitInstruction();
    }
  });

  // Quick Pillar Buttons (5 Piliers Baay-Faal)
  const pillarBtns = document.querySelectorAll('.btn-quick-pillar');
  pillarBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.getAttribute('data-cmd');
      if (cmd && cmdInput) {
        cmdInput.value = cmd;
        submitInstruction();
      }
    });
  });

  btnClear.addEventListener('click', () => {
    consoleStream.innerHTML = `
      <div class="empty-state">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <p>Console nettoyée. Saisissez une commande ci-dessus pour lancer la boucle autonome.</p>
      </div>
    `;
  });

  // Fetch Status
  async function loadSystemStatus() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      if (data.success) {
        document.getElementById('val-memory-engine').textContent = data.memory_engine === 'mysql' ? 'MySQL XAMPP' : 'SQLite Hybrid';
        document.getElementById('val-nodes-count').textContent = `${data.nodes_registered} Registered`;

        document.getElementById('spec-os').textContent = `${data.system.os} (${data.system.os_version})`;
        document.getElementById('spec-arch').textContent = data.system.architecture;
        document.getElementById('spec-python').textContent = `Python ${data.system.python_version}`;
        document.getElementById('spec-dir').textContent = data.system.current_directory;
      }
    } catch (e) {
      console.warn('Impossible de charger les métriques de statut :', e);
    }
  }

  // Load Memory Vault Logs
  async function loadMemoryLogs() {
    const memoryList = document.getElementById('memory-list');
    if (!memoryList) return;

    memoryList.innerHTML = '<div style="color: var(--text-muted)">Chargement de la mémoire persistante...</div>';

    try {
      const res = await fetch('/api/memory');
      const data = await res.json();

      if (data.success) {
        memoryList.innerHTML = '';
        if (data.knowledge && data.knowledge.length > 0) {
          data.knowledge.forEach(item => {
            const itemEl = document.createElement('div');
            itemEl.className = 'log-step';
            itemEl.style.borderLeftColor = 'var(--accent-cyan)';
            itemEl.innerHTML = `
              <div class="log-thought">FAIT APPRIS : ${escapeHtml(item.key)}</div>
              <div class="log-result">${escapeHtml(item.value)} (Catégorie: ${escapeHtml(item.category)})</div>
            `;
            memoryList.appendChild(itemEl);
          });
        } else {
          memoryList.innerHTML = '<div style="color: var(--text-muted)">Aucune connaissance enregistrée en mémoire pour l\'instant.</div>';
        }
      }
    } catch (e) {
      memoryList.innerHTML = `<div style="color: var(--accent-rose)">Erreur de chargement de la mémoire : ${escapeHtml(e.message)}</div>`;
    }
  }

  if (btnRefreshMemory) {
    btnRefreshMemory.addEventListener('click', loadMemoryLogs);
  }

  // Utility HTML Escape
  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
  }

  // Initial Load
  loadSystemStatus();
});
