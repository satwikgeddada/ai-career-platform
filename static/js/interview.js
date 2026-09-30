let quizData = null;
let currentIdx = 0;
let userAnswers = {};
let quizMeta = {};

document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    
    const savedRole = sessionStorage.getItem('targetRole');
    if (savedRole) {
        const select = document.getElementById('role');
        if (select) {
            let exists = false;
            for(let i=0; i<select.options.length; i++) {
                if(select.options[i].value.toLowerCase() === savedRole.toLowerCase()) {
                    select.selectedIndex = i;
                    exists = true;
                    break;
                }
            }
            if(!exists) {
                const opt = document.createElement('option');
                opt.value = savedRole;
                opt.text = savedRole;
                opt.selected = true;
                select.add(opt);
            }
        }
    }

    // Start test
    document.getElementById('interviewForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        quizMeta = {
            role: document.getElementById('role').value,
            type: document.getElementById('type').value,
            difficulty: document.getElementById('difficulty').value,
            num_questions: document.getElementById('num_questions').value
        };
        
        sessionStorage.setItem('targetRole', quizMeta.role);

        const payload = {
            ...quizMeta,
            resume_context: document.getElementById('resume_context').value,
            weak_topics_focus: document.getElementById('weak_topics_focus').value
        };

        document.getElementById('interviewLoader').style.display = 'block';

        try {
            const res = await fetch('/api/generate-interview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.error || 'Failed to generate quiz.');
            }

            quizData = await res.json();
            currentIdx = 0;
            userAnswers = {};

            document.getElementById('setupView').style.display = 'none';
            document.getElementById('interviewLoader').style.display = 'none';
            document.getElementById('quizView').style.display = 'block';

            document.getElementById('metaRole').innerHTML = `<i class="fa-solid fa-bullseye"></i> ${quizMeta.role}`;
            document.getElementById('metaType').innerHTML = `<i class="fa-solid fa-clipboard-question"></i> ${quizMeta.type}`;
            document.getElementById('metaDiff').innerHTML = `<i class="fa-solid fa-signal"></i> ${quizMeta.difficulty}`;

            renderQuestion();

        } catch (err) {
            alert(err.message);
            document.getElementById('interviewLoader').style.display = 'none';
        }
    });

    // Nav
    document.getElementById('prevBtn').addEventListener('click', () => { if (currentIdx > 0) { currentIdx--; renderQuestion(); } });
    document.getElementById('nextBtn').addEventListener('click', () => { if (currentIdx < quizData.questions.length - 1) { currentIdx++; renderQuestion(); } });
    document.getElementById('submitBtn').addEventListener('click', () => {
        const unanswered = quizData.questions.length - Object.keys(userAnswers).length;
        if (unanswered > 0 && !confirm(`You have ${unanswered} unanswered question(s). Submit anyway?`)) return;
        
        // Show evaluating loader
        document.getElementById('evaluatingLoader').style.display = 'block';
        document.querySelector('.quiz-body').style.display = 'none';
        document.querySelector('.quiz-footer').style.display = 'none';
        
        setTimeout(() => {
            document.getElementById('evaluatingLoader').style.display = 'none';
            document.querySelector('.quiz-body').style.display = 'block';
            document.querySelector('.quiz-footer').style.display = 'flex';
            showResults();
        }, 1500);
    });

    document.getElementById('retakeBtn').addEventListener('click', backToSetup);
    document.getElementById('practiceWeakBtn').addEventListener('click', () => {
        const topics = [];
        document.querySelectorAll('#weakTopicsList li').forEach(li => topics.push(li.textContent.replace('→ ', '').trim()));
        backToSetup();
        document.getElementById('weak_topics_focus').value = topics.join(', ');
        alert('Weak topics loaded! Click "Start Mock Test" to practice them.');
    });
});

function backToSetup() {
    document.getElementById('resultView').style.display = 'none';
    document.getElementById('quizView').style.display = 'none';
    document.getElementById('setupView').style.display = 'block';
    document.getElementById('weak_topics_focus').value = '';
    loadHistory();
    window.scrollTo(0, 0);
}

function renderQuestion() {
    const q = quizData.questions[currentIdx];
    const total = quizData.questions.length;
    const pct = Math.round(((currentIdx + 1) / total) * 100);

    document.getElementById('quizProgress').style.width = pct + '%';
    document.getElementById('quizProgressText').textContent = `Question ${currentIdx + 1} of ${total}`;
    document.getElementById('questionNumber').textContent = `QUESTION ${currentIdx + 1}`;
    document.getElementById('questionText').textContent = q.question;

    const list = document.getElementById('optionsContainer');
    list.innerHTML = '';

    q.options.forEach(opt => {
        const letter = opt.charAt(0);
        const li = document.createElement('li');
        li.className = 'option-item';

        const radio = document.createElement('input');
        radio.type = 'radio'; radio.name = 'qopt'; radio.value = letter;
        radio.id = 'opt_' + letter; radio.className = 'option-radio';
        if (userAnswers[currentIdx] === letter) radio.checked = true;
        radio.addEventListener('change', () => { userAnswers[currentIdx] = letter; });

        const label = document.createElement('label');
        label.htmlFor = 'opt_' + letter;
        label.className = 'option-label';
        label.innerHTML = `<span class="option-dot"></span> ${escapeHTML(opt)}`;

        li.appendChild(radio);
        li.appendChild(label);
        list.appendChild(li);
    });

    document.getElementById('prevBtn').disabled = (currentIdx === 0);
    const isLast = (currentIdx === total - 1);
    document.getElementById('nextBtn').style.display = isLast ? 'none' : 'inline-flex';
    document.getElementById('submitBtn').style.display = isLast ? 'inline-flex' : 'none';
}

async function showResults() {
    document.getElementById('quizView').style.display = 'none';
    document.getElementById('resultView').style.display = 'block';
    window.scrollTo(0, 0);

    const total = quizData.questions.length;
    let correct = 0;
    const topicMap = {};
    let reviewHTML = '';

    quizData.questions.forEach((q, i) => {
        const userAns = userAnswers[i] || null;
        const isRight = (userAns === q.correct_answer);
        if (isRight) correct++;

        const topic = q.topic || 'General';
        if (!topicMap[topic]) topicMap[topic] = { total: 0, correct: 0 };
        topicMap[topic].total++;
        if (isRight) topicMap[topic].correct++;

        const userOptText = userAns ? (q.options.find(o => o.charAt(0) === userAns) || 'Not Answered') : 'Not Answered';
        const correctOptText = q.options.find(o => o.charAt(0) === q.correct_answer) || q.correct_answer;

        reviewHTML += `
            <div class="review-card glass-static ${isRight ? 'is-correct' : 'is-wrong'}">
                <div class="review-q">Q${i + 1}. ${escapeHTML(q.question)}</div>
                <p style="margin:0 0 0.25rem;"><strong>Your Answer:</strong>
                    <span style="color:${isRight ? '#059669' : '#DC2626'};">${escapeHTML(userOptText)}</span>
                </p>
                ${!isRight ? `<p style="margin:0 0 0.5rem;"><strong>Correct Answer:</strong> ${escapeHTML(correctOptText)}</p>` : ''}
                <span class="review-badge ${isRight ? 'correct' : 'wrong'}">
                    ${isRight ? '<i class="fa-solid fa-check"></i> Correct' : '<i class="fa-solid fa-xmark"></i> Incorrect'}
                </span>
                <div class="review-explain"><strong>Explanation:</strong> ${escapeHTML(q.explanation)}</div>
            </div>`;
    });

    const pct = Math.round((correct / total) * 100);
    let perf = 'Needs Improvement';
    if (pct >= 90) perf = 'Excellent';
    else if (pct >= 70) perf = 'Good';
    else if (pct >= 50) perf = 'Average';

    document.getElementById('resBig').textContent = `${correct}/${total}`;
    document.getElementById('resPerf').textContent = perf;
    document.getElementById('resPct').textContent = `${pct}%`;
    document.getElementById('resCorrect').textContent = correct;
    document.getElementById('resWrong').textContent = total - correct;
    document.getElementById('resAcc').textContent = `${pct}%`;

    let topicHTML = '';
    const weakTopics = [];
    for (const [topic, s] of Object.entries(topicMap)) {
        const tPct = Math.round((s.correct / s.total) * 100);
        const barColor = tPct >= 70 ? '#34D399' : (tPct >= 40 ? '#FBBF24' : '#F87171');
        topicHTML += `
            <div class="topic-row">
                <div class="topic-row-head"><span>${escapeHTML(topic)}</span><span>${tPct}%</span></div>
                <div class="topic-bar"><div class="topic-bar-fill" style="width:${tPct}%;background:${barColor};"></div></div>
            </div>`;
        if (tPct < 60) weakTopics.push(topic);
    }
    document.getElementById('topicPerformance').innerHTML = topicHTML;

    const weakCard = document.getElementById('weakCard');
    if (weakTopics.length > 0) {
        weakCard.style.display = 'block';
        document.getElementById('weakTopicsList').innerHTML = weakTopics.map(t => `<li>${escapeHTML(t)}</li>`).join('');
        document.getElementById('weakRecommend').textContent = `Revise: ${weakTopics.join(', ')} to strengthen your preparation.`;
    } else {
        weakCard.style.display = 'none';
    }

    document.getElementById('reviewContainer').innerHTML = reviewHTML;

    fetch('/api/save-interview-result', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            target_role: quizMeta.role, interview_type: quizMeta.type,
            difficulty: quizMeta.difficulty, total_questions: total,
            score: correct, percentage: pct, weak_topics: weakTopics
        })
    });
}

async function loadHistory() {
    try {
        const res = await fetch('/api/interview-history');
        const history = await res.json();
        const box = document.getElementById('historyContainer');
        if (!history || history.length === 0) {
            box.innerHTML = '<p style="color:var(--text-light);">No previous attempts yet. Take your first test!</p>';
            return;
        }
        box.innerHTML = history.slice(0, 5).map(h => `
            <div class="history-row glass-static">
                <div>
                    <strong>${escapeHTML(h.target_role)}</strong> <span style="color:var(--text-muted); font-size:0.85rem;">(${escapeHTML(h.difficulty)})</span>
                    <p style="margin:0; font-size:0.8rem; color:var(--text-muted);">${escapeHTML(h.date)} · ${escapeHTML(h.interview_type)}</p>
                </div>
                <div style="text-align:right;">
                    <strong style="color:${h.percentage >= 60 ? '#10B981' : '#EF4444'}; font-size:1.1rem;">${h.score}/${h.total_questions}</strong>
                    <span style="font-size:0.85rem; color:var(--text-muted);"> (${h.percentage}%)</span>
                </div>
            </div>`).join('');
    } catch (e) { console.error(e); }
}
