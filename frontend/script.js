let activeTab = 'transcript';

function onFileSelect(input) {
  const file = input.files[0];
  if (!file) return;

  document.getElementById('fileNameText').textContent = file.name;
  document.getElementById('fileName').style.display = 'flex';
  document.getElementById('uploadBtn').disabled = false;
  document.getElementById('uploadError').style.display = 'none';

  const mc = document.getElementById('mediaContainer');
  mc.innerHTML = '';
  const url = URL.createObjectURL(file);
  const isVideo = file.type.startsWith('video/');
  const el = document.createElement(isVideo ? 'video' : 'audio');
  el.src = url;
  el.controls = true;
  mc.appendChild(el);
  mc.style.display = 'block';

  document.getElementById('emptyState').style.display = 'flex';
  document.getElementById('transcript').style.display = 'none';
  document.getElementById('notes').style.display = 'none';
  document.getElementById('answerBox').style.display = 'none';
}

function switchTab(tab) {
  activeTab = tab;
  document.querySelectorAll('.tab').forEach((t, i) => {
    t.classList.toggle('active', (i === 0 && tab === 'transcript') || (i === 1 && tab === 'notes'));
  });

  const transcript = document.getElementById('transcript');
  const notes = document.getElementById('notes');

  // only switch if content is actually loaded
  if (transcript.textContent || notes.textContent) {
    transcript.style.display = tab === 'transcript' ? 'block' : 'none';
    notes.style.display = tab === 'notes' ? 'block' : 'none';
  }
}

async function uploadFile() {
  const file = document.getElementById('fileInput').files[0];
  if (!file) return;

  const btn = document.getElementById('uploadBtn');
  const status = document.getElementById('uploadStatus');
  const errEl = document.getElementById('uploadError');

  btn.disabled = true;
  status.style.display = 'flex';
  errEl.style.display = 'none';
  document.getElementById('emptyState').style.display = 'flex';
  document.getElementById('transcript').style.display = 'none';
  document.getElementById('notes').style.display = 'none';

  try {
    const fd = new FormData();
    fd.append('file', file);
    const res = await fetch('http://127.0.0.1:8000/upload', { method: 'POST', body: fd });
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || 'Upload failed. Please try again.');

    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('transcript').textContent = data.transcript || 'No transcript returned.';
    document.getElementById('notes').textContent = data.notes || 'No notes returned.';
    document.getElementById('transcript').style.display = activeTab === 'transcript' ? 'block' : 'none';
    document.getElementById('notes').style.display = activeTab === 'notes' ? 'block' : 'none';

  } catch (err) {
    errEl.textContent = err.message || 'Something went wrong. Is the server running?';
    errEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    status.style.display = 'none';
  }
}

async function askQuestion() {
  const query = document.getElementById('query').value.trim();
  const errEl = document.getElementById('askError');
  const answerBox = document.getElementById('answerBox');
  const answerEl = document.getElementById('answer');
  const btn = document.getElementById('askBtn');

  errEl.style.display = 'none';

  if (!query) {
    errEl.textContent = 'Please enter a question.';
    errEl.style.display = 'block';
    return;
  }

  btn.disabled = true;
  answerBox.style.display = 'block';
  answerEl.textContent = 'Thinking...';

  try {
    const res = await fetch(`http://127.0.0.1:8000/ask?query=${encodeURIComponent(query)}`, { method: 'POST' });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    answerEl.textContent = data.answer || 'No answer returned.';
  } catch (err) {
    answerEl.textContent = '';
    errEl.textContent = err.message || 'Could not get answer. Is the server running?';
    errEl.style.display = 'block';
    answerBox.style.display = 'none';
  } finally {
    btn.disabled = false;
  }
}

async function uploadYoutube() {
  const url = document.getElementById('ytUrl').value.trim();
  const errEl = document.getElementById('uploadError');
  const btn = document.getElementById('ytBtn');
  const status = document.getElementById('uploadStatus');

  if (!url) {
    errEl.textContent = 'Please paste a YouTube URL.';
    errEl.style.display = 'block';
    return;
  }

  btn.disabled = true;
  status.style.display = 'flex';
  errEl.style.display = 'none';

  try {
    const res = await fetch(`http://127.0.0.1:8000/upload-youtube?url=${encodeURIComponent(url)}`, {
      method: 'POST'
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to process YouTube video.');

    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('transcript').textContent = data.transcript || 'No transcript returned.';
    document.getElementById('notes').textContent = data.notes || 'No notes returned.';
    document.getElementById('transcript').style.display = activeTab === 'transcript' ? 'block' : 'none';
    document.getElementById('notes').style.display = activeTab === 'notes' ? 'block' : 'none';

  } catch (err) {
    errEl.textContent = err.message || 'Something went wrong.';
    errEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    status.style.display = 'none';
  }
}