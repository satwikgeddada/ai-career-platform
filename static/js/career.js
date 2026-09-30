document.addEventListener('DOMContentLoaded', () => {
    const savedRole = sessionStorage.getItem('targetRole');
    if (savedRole) {
        const input = document.getElementById('targetRole');
        if (input) input.value = savedRole;
    }
});

document.getElementById('careerForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();

    const data = {
        name: document.getElementById('name').value,
        targetRole: document.getElementById('targetRole').value,
        currentSkills: document.getElementById('currentSkills').value,
        experienceLevel: document.getElementById('experienceLevel').value,
        preferredDomain: document.getElementById('preferredDomain').value
    };

    document.getElementById('careerLoader').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';

    try {
        const response = await fetch('/api/career-plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.error || 'Network response was not ok');
        }

        const plan = await response.json();

        document.getElementById('res-summary').innerText = plan.career_summary || "Summary not available.";

        const pills = (arr, cls) => {
            if (!arr || arr.length === 0) return '<span class="pill">None</span>';
            return arr.map(i => `<span class="pill ${cls}">${escapeHTML(i)}</span>`).join('');
        };

        document.getElementById('res-existing-skills').innerHTML = pills(plan.existing_skills, 'success');
        document.getElementById('res-skill-gaps').innerHTML = pills(plan.skill_gaps, 'warning');
        document.getElementById('res-priority-skills').innerHTML = pills(plan.priority_skills, 'danger');

        // Roadmap
        let rmHTML = '';
        if (plan.roadmap && plan.roadmap.length > 0) {
            let curWeek = 0;
            plan.roadmap.forEach((day, idx) => {
                const wk = Math.ceil(day.day / 7);
                if (wk !== curWeek) {
                    if (curWeek !== 0) rmHTML += '</div></div>';
                    curWeek = wk;
                    rmHTML += `
                        <div class="roadmap-week ${idx === 0 ? 'active' : ''}">
                            <div class="roadmap-week-header" onclick="this.parentElement.classList.toggle('active')">
                                <span><i class="fa-solid fa-calendar-week"></i> Week ${curWeek}</span>
                                <i class="fa-solid fa-chevron-down"></i>
                            </div>
                            <div class="roadmap-week-content">`;
                }
                rmHTML += `
                    <div class="roadmap-day">
                        <h4>Day ${day.day}: ${escapeHTML(day.topic)}</h4>
                        <p style="margin-bottom:0.75rem;">${escapeHTML(day.description)}</p>
                        <div class="glass-static" style="padding:1rem; border-radius:12px; margin-bottom:0.5rem;">
                            <strong>Task:</strong> ${escapeHTML(day.task)}<br>
                            <small style="color:var(--text-muted);"><i class="fa-regular fa-clock"></i> ${escapeHTML(day.time)}</small>
                        </div>
                        ${day.resources && day.resources.length > 0 ? `
                            <div style="margin-top:0.5rem;">
                                <strong>Resources:</strong>
                                <ul style="margin-left:1.5rem; margin-top:0.25rem; color:var(--text-light);">
                                    ${day.resources.map(r => `<li>${escapeHTML(r)}</li>`).join('')}
                                </ul>
                            </div>` : ''}
                    </div>`;
            });
            if (curWeek !== 0) rmHTML += '</div></div>';
        } else {
            rmHTML = '<p style="text-align:center; color:var(--text-light);">No roadmap generated.</p>';
        }
        document.getElementById('res-roadmap').innerHTML = rmHTML;

        const listItems = (arr) => {
            if (!arr || arr.length === 0) return '<li>None specified</li>';
            return arr.map(i => `<li>${escapeHTML(i)}</li>`).join('');
        };
        document.getElementById('res-projects').innerHTML = listItems(plan.projects);
        document.getElementById('res-interview').innerHTML = listItems(plan.interview_topics);
        
        const targetRole = document.getElementById('targetRole').value;
        sessionStorage.setItem('targetRole', targetRole);

        // Add Next Step button
        let nextStepDiv = document.getElementById('careerNextStep');
        if (!nextStepDiv) {
            nextStepDiv = document.createElement('div');
            nextStepDiv.id = 'careerNextStep';
            nextStepDiv.style.textAlign = 'center';
            nextStepDiv.style.marginTop = '3rem';
            nextStepDiv.innerHTML = `
                <h3 style="margin-bottom:1.5rem;">Next Step in Your Journey</h3>
                <a href="/resume" class="btn btn-primary"><i class="fa-solid fa-file-lines"></i> Analyze My Resume</a>
            `;
            document.getElementById('resultsSection').appendChild(nextStepDiv);
        }

        document.getElementById('careerLoader').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';

    } catch (error) {
        alert(error.message || 'Failed to generate career plan. Please try again.');
        document.getElementById('careerLoader').style.display = 'none';
    }
});
