// Drag-and-drop upload area
document.addEventListener('DOMContentLoaded', () => {
    const area = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resumeFile');
    const fileNameEl = document.getElementById('fileName');

    if (!area || !fileInput) return;

    area.addEventListener('click', () => fileInput.click());

    area.addEventListener('dragover', (e) => { e.preventDefault(); area.classList.add('drag-over'); });
    area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
    area.addEventListener('drop', (e) => {
        e.preventDefault();
        area.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            showFileName(e.dataTransfer.files[0].name);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) showFileName(fileInput.files[0].name);
    });

    function showFileName(name) {
        fileNameEl.textContent = '📄 ' + name;
        fileNameEl.style.display = 'block';
    }
    
    const savedRole = sessionStorage.getItem('targetRole');
    if (savedRole) {
        const input = document.getElementById('jobDescription');
        if (input) input.value = savedRole;
    }
});

document.getElementById('resumeForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();

    const fileInput = document.getElementById('resumeFile');
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please select a file to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('resumeFile', fileInput.files[0]);
    formData.append('jobDescription', document.getElementById('jobDescription').value);

    document.getElementById('resumeLoader').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';

    try {
        const response = await fetch('/api/analyze-resume', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.error || 'Network response was not ok');
        }

        const data = await response.json();
        const ats = data.deterministic_ats;

        const pills = (arr, cls) => {
            if (!arr || arr.length === 0) return '<span class="pill">None</span>';
            return arr.map(i => `<span class="pill ${cls}">${escapeHTML(i)}</span>`).join('');
        };

        let improvHTML = (data.areas_for_improvement || []).map(i => `<li>${escapeHTML(i)}</li>`).join('') || '<li>None identified</li>';
        let strengthHTML = (data.strengths || []).map(i => `<li>${escapeHTML(i)}</li>`).join('') || '<li>None identified</li>';

        let portalsHTML = '';
        if (data.job_portals && data.job_portals.length > 0) {
            portalsHTML = data.job_portals.map(p => `
                <div class="glass-static" style="padding:1rem; margin-bottom:0.75rem; border-radius:12px;">
                    <h5 style="margin-bottom:0.2rem;"><a href="${escapeHTML(p.url)}" target="_blank" style="color:var(--primary-dark);">${escapeHTML(p.name)} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:0.7rem;"></i></a></h5>
                    <p style="font-size:0.85rem; margin:0;">${escapeHTML(p.description)}</p>
                </div>`).join('');
        } else {
            portalsHTML = '<p style="color:var(--text-light);">No specific portals found.</p>';
        }

        let certsHTML = '';
        if (data.certifications && data.certifications.length > 0) {
            certsHTML = data.certifications.map(c => `
                <div class="glass-static" style="padding:1rem; margin-bottom:0.75rem; border-radius:12px;">
                    <h5 style="margin-bottom:0.2rem;"><a href="${escapeHTML(c.url)}" target="_blank" style="color:var(--primary-dark);">${escapeHTML(c.name)} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:0.7rem;"></i></a></h5>
                    <p style="font-size:0.8rem; color:var(--text); font-weight:500; margin-bottom:0.15rem;">Provider: ${escapeHTML(c.provider)}</p>
                    <p style="font-size:0.85rem; margin:0;">${escapeHTML(c.description)}</p>
                </div>`).join('');
        } else {
            certsHTML = '<p style="color:var(--text-light);">No specific certifications found.</p>';
        }

        document.getElementById('resumeResults').innerHTML = `
            <!-- ATS Score Circle -->
            <div class="glass-strong" style="padding:2rem; text-align:center; margin-bottom:2rem;">
                <h3 style="color:var(--primary-dark); margin-bottom:0.5rem;">Estimated ATS Compatibility</h3>
                <div class="ats-circle-wrap">
                    <div class="ats-circle" style="--ats-pct:${ats.score}%;">
                        <div class="ats-circle-inner">
                            <span class="big">${ats.score}</span>
                            <span class="small">/ 100</span>
                        </div>
                    </div>
                </div>
                <p style="font-size:0.8rem; color:var(--text-muted); font-style:italic; margin-top:0.5rem;">
                    * Estimated score based on keywords and sections. Not a company ATS score.
                </p>
            </div>

            <!-- Skills Analysis -->
            <div class="card-grid" style="margin-bottom:2rem;">
                <div class="glass-static" style="padding:1.5rem; text-align:left;">
                    <h4><i class="fa-solid fa-check-double" style="color:#10B981;"></i> Matching Skills</h4>
                    <div class="pill-container" style="margin-top:0.75rem;">${pills(ats.matching_skills, 'success')}</div>
                </div>
                <div class="glass-static" style="padding:1.5rem; text-align:left;">
                    <h4><i class="fa-solid fa-xmark" style="color:#EF4444;"></i> Missing Skills</h4>
                    <div class="pill-container" style="margin-top:0.75rem;">${pills(ats.missing_skills, 'danger')}</div>
                </div>
                <div class="glass-static" style="padding:1.5rem; text-align:left;">
                    <h4><i class="fa-solid fa-lightbulb" style="color:#F59E0B;"></i> Recommended</h4>
                    <div class="pill-container" style="margin-top:0.75rem;">${pills(ats.recommended_skills, 'warning')}</div>
                </div>
                <div class="glass-static" style="padding:1.5rem; text-align:left;">
                    <h4><i class="fa-solid fa-file-lines" style="color:#6366F1;"></i> Detected Sections</h4>
                    <div class="pill-container" style="margin-top:0.75rem;">${pills(ats.detected_sections, 'info')}</div>
                </div>
            </div>

            <!-- AI Feedback -->
            <div class="glass-strong" style="padding:2rem; margin-bottom:2rem; text-align:left;">
                <h3 style="margin-bottom:1rem;">AI Qualitative Feedback</h3>
                <p style="font-size:1.05rem; margin-bottom:1.5rem;">${escapeHTML(data.feedback)}</p>
                <div class="card-grid" style="grid-template-columns:1fr 1fr;">
                    <div>
                        <h4 style="color:#DC2626; margin-bottom:0.75rem;"><i class="fa-solid fa-circle-xmark"></i> Areas for Improvement</h4>
                        <ul style="margin-left:1.5rem; color:var(--text-light);">${improvHTML}</ul>
                    </div>
                    <div>
                        <h4 style="color:var(--primary-dark); margin-bottom:0.75rem;"><i class="fa-solid fa-circle-check"></i> Strengths</h4>
                        <ul style="margin-left:1.5rem; color:var(--text-light);">${strengthHTML}</ul>
                    </div>
                </div>
            </div>

            <!-- Portals & Certs -->
            <div class="glass-strong" style="padding:2rem; text-align:left;">
                <h3 style="margin-bottom:1.5rem;">Recommended Resources</h3>
                <div class="card-grid" style="grid-template-columns:1fr 1fr;">
                    <div>
                        <h4 style="margin-bottom:0.75rem;"><i class="fa-solid fa-briefcase"></i> Job Portals</h4>
                        ${portalsHTML}
                    </div>
                    <div>
                        <h4 style="margin-bottom:0.75rem;"><i class="fa-solid fa-certificate"></i> Certifications</h4>
                        ${certsHTML}
                    </div>
                </div>
            </div>
            
            <!-- Next Steps -->
            <div style="text-align:center; margin-top:3rem; margin-bottom:1rem;">
                <h3 style="margin-bottom:1.5rem;">Take the Next Step</h3>
                <div style="display:flex; justify-content:center; gap:1rem; flex-wrap:wrap;">
                    <a href="/interview" class="btn btn-primary"><i class="fa-solid fa-clipboard-question"></i> Practice Interview</a>
                    <a href="/career" class="btn btn-outline"><i class="fa-solid fa-compass"></i> Improve My Skills</a>
                </div>
            </div>
        `;
        
        const targetRole = document.getElementById('jobDescription').value;
        sessionStorage.setItem('targetRole', targetRole);

        document.getElementById('resumeLoader').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';

    } catch (error) {
        alert(error.message || 'Failed to analyze resume. Please try again.');
        document.getElementById('resumeLoader').style.display = 'none';
    }
});
