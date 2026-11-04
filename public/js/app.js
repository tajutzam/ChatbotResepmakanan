(() => {
  'use strict';
  let recipes = window.recipeData || [];
  const page = document.body.dataset.page;
  const titles = {home:'Beranda',chatbot:'Chatbot resep',recommendations:'Rekomendasi resep',planner:'Rencana masak',dashboard:'Dashboard',recipes:'Menu resep',history:'Riwayat pencarian',login:'Masuk',signup:'Daftar',admin:'Kelola resep'};
  const read = (key, fallback) => { try { return JSON.parse(localStorage.getItem(`keenvado.${key}`)) ?? fallback; } catch { return fallback; } };
  const write = (key, value) => { try { localStorage.setItem(`keenvado.${key}`, JSON.stringify(value)); } catch { toast('Penyimpanan browser tidak tersedia.'); } };
  let saved = read('saved', []), history = read('history', []), plan = read('plan', {}), category = 'Semua resep', query = new URLSearchParams(location.search).get('q') || '', onlySaved = false, toastTimer;
  let chatHistory = [], chatConversationId = null, recipesLoading = true, userDataLoading = Boolean(document.body.dataset.authenticated === '1');
  const userData = async () => { if (!userDataLoading) return; try { const response = await fetch('/api/user-data', { headers: { Accept: 'application/json' } }); if (!response.ok) return; const data = await response.json(); saved = (data.favorites || []).map(String); history = data.history || []; } finally { userDataLoading = false; } };
  const saveUserData = async (url, options = {}) => { if (!document.body.dataset.authenticated) return; await fetch(url, { ...options, headers: { Accept: 'application/json', 'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]')?.content || '', ...(options.headers || {}) } }); };
  if (!Array.isArray(saved)) saved = [];
  saved = saved.map(String);
  if (!Array.isArray(history)) history = [];
  if (!plan || Array.isArray(plan) || typeof plan !== 'object') plan = {};
  const toast = message => { const node = document.querySelector('#toast'); if (!node) return; node.textContent = message; node.classList.add('visible'); clearTimeout(toastTimer); toastTimer = setTimeout(() => node.classList.remove('visible'), 3000); };
  const record = text => { history = history.filter(item => item.query !== text); history.unshift({ query: text, date: new Date().toISOString() }); history = history.slice(0, 50); if (document.body.dataset.authenticated !== '1') write('history', history); saveUserData('/api/history', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: text }) }); };
  const ingredients = recipe => Array.isArray(recipe.ingredients) ? recipe.ingredients : String(recipe.ingredients || '').split(/[,;\n]+/).map(item => item.trim()).filter(Boolean);
  const card = recipe => { const items = ingredients(recipe); return `<article class="recipe-card" data-detail="${recipe.id}" tabindex="0" role="button" aria-label="Lihat detail ${recipe.title}">${recipe.photo_url ? `<img class="recipe-photo" src="${recipe.photo_url}" alt="${recipe.title || 'Foto resep'}" loading="lazy">` : ''}<div class="card-top"><span></span><button class="save ${saved.includes(String(recipe.id)) ? 'saved' : ''}" data-save="${recipe.id}" aria-label="Simpan resep">${saved.includes(String(recipe.id)) ? '♥' : '♡'}</button></div><h3><span class="title-button">${recipe.title}</span></h3><p>${recipe.description || recipe.document || ''}</p><div class="ingredients">${items.slice(0, 3).join(' · ')} <span>+${Math.max(0, items.length - 3)} bahan</span></div><div class="card-meta"></div></article>`; };
  const filtered = () => recipes.filter(recipe => (category === 'Semua resep' || recipe.category === category) && (!onlySaved || saved.includes(String(recipe.id))) && (!query || `${recipe.title} ${ingredients(recipe).join(' ')} ${recipe.category} ${recipe.time}`.toLowerCase().includes(query.toLowerCase())));
  const loadingMarkup = '<div class="recipe-loading" role="status" aria-live="polite"><span></span><span></span><span></span><p>Memuat resep dari dapur...</p></div>';
  const renderCards = () => { const list = document.querySelector('#recipe-list'); if (!list) return; if (recipesLoading) { list.innerHTML = loadingMarkup; return; } const rows = filtered(); list.innerHTML = rows.length ? rows.map(card).join('') : '<div class="empty">Belum ada resep yang cocok.</div>'; const count = document.querySelector('#result-count'); if (count) count.textContent = `${rows.length} resep tersedia`; };
  const renderDashboard = () => { if (page !== 'dashboard') return; const list = document.querySelector('#recipe-list'); if (list) list.innerHTML = recipesLoading ? loadingMarkup : (saved.length ? recipes.filter(recipe => saved.includes(String(recipe.id))).map(card).join('') : '<div class="empty">Koleksi favoritmu masih kosong.</div>'); document.querySelector('#saved-count')?.replaceChildren(document.createTextNode(saved.length)); document.querySelector('#plan-count')?.replaceChildren(document.createTextNode(Object.keys(plan).length)); document.querySelector('#history-count')?.replaceChildren(document.createTextNode(history.length)); };
  const renderPlanner = () => { const list = document.querySelector('#planner-list'); if (!list) return; list.innerHTML = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu'].map(day => { const recipe = recipes.find(item => String(item.id) === String(plan[day])); return `<section class="day"><div class="eyebrow">MENU HARIAN</div><h3>${day}</h3>${recipe ? `<button class="planned planned-clickable" data-detail="${recipe.id}" type="button"><span class="eyebrow">RESEP TERPILIH</span><strong>${recipe.title}</strong></button>` : '<p class="subtitle">Belum ada rencana. Mau masak apa?</p>'}<select data-day="${day}"><option value="">Pilih resep…</option>${recipes.map(item => `<option value="${item.id}" ${recipe?.id === item.id ? 'selected' : ''}>${item.title}</option>`).join('')}</select></section>`; }).join(''); };
  const renderHistory = () => { const list = document.querySelector('#history-list'); if (!list) return; document.querySelector('#history-count-label').textContent = `${history.length} pencarian tersimpan di browser ini`; list.innerHTML = history.map((item, index) => `<div class="history-row"><div><strong>⌕ ${item.query}</strong><small>${new Date(item.date).toLocaleString('id-ID')}</small></div><a class="button secondary" href="/rekomendasi?q=${encodeURIComponent(item.query)}">Cari lagi ↗</a><button class="text-button" data-delete-history="${index}">Hapus</button></div>`).join('') || '<div class="empty">Belum ada riwayat pencarian.</div>'; };
  const detail = id => { const recipe = recipes.find(item => String(item.id) === String(id)); if (!recipe) return; const items = ingredients(recipe); const steps = Array.isArray(recipe.steps) ? recipe.steps : String(recipe.steps || '').split(/\d+[.)]\s*|\n+/).map(item => item.trim()).filter(Boolean); document.querySelector('#recipe-detail').innerHTML = `${recipe.photo_url ? `<img class="dialog-photo" src="${recipe.photo_url}" alt="${recipe.title || 'Foto resep'}">` : ''}<h2 id="recipe-title">${recipe.title}</h2><p>${recipe.description || ''}</p><div class="detail-meta">◷ ${recipe.time || '-'} menit · ${recipe.servings || '-'} porsi · ${recipe.level || 'Mudah'}</div><h3>Bahan-bahan</h3><ul>${items.map(item => `<li>${item}</li>`).join('')}</ul><h3>Cara memasak</h3><ol>${steps.map(item => `<li>${item}</li>`).join('')}</ol>`; document.querySelector('#recipe-dialog').showModal(); };
  const saveChat = () => saveUserData('/api/chat-history', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ conversation_id: chatConversationId, messages: chatHistory }) }).then(async response => { if (response.ok) chatConversationId = (await response.json()).conversation_id; });
  const loadChatHistory = async () => { const panel = document.querySelector('#chat-history-panel'); const list = document.querySelector('#chat-history-list'); if (!panel || !list || document.body.dataset.authenticated !== '1') return; const response = await fetch('/api/chat-history', { headers: { Accept: 'application/json' } }); const data = await response.json(); list.innerHTML = data.conversations?.length ? data.conversations.map(item => `<button class="chat-history-item" type="button" data-chat-conversation="${item.id}"><strong>${item.title || 'Percakapan baru'}</strong><small>${new Date(item.updated_at).toLocaleString('id-ID')}</small></button>`).join('') : '<p class="empty">Belum ada percakapan tersimpan.</p>'; panel.hidden = false; };
  const openChat = async id => { const response = await fetch(`/api/chat-history/${id}`, { headers: { Accept: 'application/json' } }); if (!response.ok) return; const data = await response.json(); chatConversationId = data.conversation.id; chatHistory = data.conversation.messages.map(item => ({ role: item.role, content: item.content })); const messages = document.querySelector('#messages'); messages.innerHTML = ''; chatHistory.forEach(item => { const node = document.createElement('div'); node.className = `message${item.role === 'user' ? ' user' : ''}`; node.textContent = item.content; messages.append(node); }); document.querySelector('#chat-history-panel').hidden = true; };
  const chat = async text => {
    const message = text.trim();
    if (!message) return;
    const messages = document.querySelector('#messages');
    const form = document.querySelector('#chat-form');
    if (!messages || !form) return;
    const userMessage = document.createElement('div');
    userMessage.className = 'message user';
    userMessage.textContent = message;
    messages.append(userMessage);
    const pending = document.createElement('div');
    pending.className = 'message';
    pending.textContent = 'Sedang mencari resep di koleksi KeenVado Meals…';
    messages.append(pending);
    messages.scrollTop = messages.scrollHeight;
    try {
      const payload = new FormData(form);
      payload.set('message', message);
      chatHistory.slice(-8).forEach((turn, index) => {
        payload.set(`history[${index}][role]`, turn.role);
        payload.set(`history[${index}][content]`, turn.content);
      });
      const response = await fetch(form.action, {
        method: 'POST',
        headers: { Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
        body: payload,
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Permintaan belum berhasil.');
      pending.remove();
      const reply = document.createElement('div');
      reply.className = 'message';
      const intro = document.createElement('p');
      intro.className = 'chat-reply-text';
      const renderReply = value => String(value).replace(/[&<>"]/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[character]).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\*(.+?)\*/g, '<em>$1</em>').replace(/\n/g, '<br>');
      intro.innerHTML = renderReply(result.message);
      reply.append(intro);
      chatHistory.push({ role: 'user', content: message }, { role: 'assistant', content: result.message });
      if ((result.recipes || []).length) {
        const relatedTitle = document.createElement('h3');
        relatedTitle.className = 'chat-related-title';
        relatedTitle.textContent = 'Resep terkait';
        reply.append(relatedTitle);
      }
      (result.recipes || []).forEach(recipe => {
        const card = document.createElement('article');
        card.className = 'chat-recipe';
        const title = document.createElement('h3');
        title.textContent = recipe.title;
        card.append(title);
        const sourceLabel = document.createElement('small');
        sourceLabel.className = 'chat-source-label';
        sourceLabel.textContent = `Sumber: ${recipe.source}`;
        card.append(sourceLabel);
        const ingredientsHeading = document.createElement('strong');
        ingredientsHeading.className = 'chat-recipe-label';
        ingredientsHeading.textContent = 'Bahan';
        card.append(ingredientsHeading);
        const ingredients = document.createElement('p');
        ingredients.className = 'chat-recipe-text';
        ingredients.textContent = recipe.ingredients;
        card.append(ingredients);
        const planControl = document.createElement('div');
        planControl.className = 'chat-plan-control';
        planControl.innerHTML = `<select data-plan-recipe="${recipe.id}" aria-label="Pilih hari untuk ${recipe.title}"><option value="">Pilih hari...</option>${['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu'].map(day => `<option value="${day}">${day}</option>`).join('')}</select><button class="text-button" type="button" data-plan-recipe="${recipe.id}">Simpan ke rencana</button>`;
        card.append(planControl);
        if (recipe.steps) {
          const details = document.createElement('details');
          const summary = document.createElement('summary');
          summary.textContent = 'Cara memasak';
          const steps = document.createElement('p');
          steps.className = 'chat-recipe-text';
          steps.textContent = recipe.steps;
          details.append(summary, steps);
          card.append(details);
        }
        reply.append(card);
      });
      messages.append(reply);
      await saveChat();
    } catch (error) {
      pending.textContent = error.message || 'Chatbot belum bisa dihubungi. Coba lagi.';
    }
    messages.scrollTop = messages.scrollHeight;
  };
  document.querySelector('#breadcrumb').textContent = titles[page]; document.title = `${titles[page]} — KeenVado Meals`;
  const searchRecipes = async value => {
    const list = document.querySelector('#recipe-list');
    if (list) list.innerHTML = loadingMarkup;
    try {
      const response = await fetch(`/api/recipes/search?q=${encodeURIComponent(value)}`, { headers: { Accept: 'application/json' } });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Pencarian resep gagal.');
      recipes = result.recipes || [];
      recipesLoading = false;
      renderCards();
    } catch (error) {
      toast(error.message || 'Pencarian resep gagal.');
      renderCards();
    }
  };
  const loadRecipes = async () => {
    await userData();
    try {
      const response = await fetch('/api/recipes', { headers: { Accept: 'application/json' } });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Resep belum bisa dimuat.');
      recipes = result.recipes || [];
    } catch (error) {
      recipes = window.recipeData || [];
      toast(error.message || 'Resep belum bisa dimuat.');
    }
    recipesLoading = false;
    renderCards(); renderDashboard(); renderPlanner(); renderHistory();
  };
  loadRecipes();
  document.addEventListener('click', event => { const recipeCard = event.target.closest('.recipe-card[data-detail]'); if (recipeCard && !event.target.closest('button')) detail(recipeCard.dataset.detail); });
  document.addEventListener('keydown', event => { if ((event.key === 'Enter' || event.key === ' ') && event.target.matches('.recipe-card[data-detail]')) { event.preventDefault(); detail(event.target.dataset.detail); } });
  document.addEventListener('click', event => { const button = event.target.closest('button'); if (!button) return; if (button.dataset.detail) detail(button.dataset.detail); if (button.classList.contains('close')) document.querySelector('#recipe-dialog').close(); if (button.dataset.save) { const id = String(button.dataset.save); saved = saved.includes(id) ? saved.filter(item => item !== id) : [...saved, id]; if (document.body.dataset.authenticated !== '1') write('saved', saved); saveUserData('/api/favorites/toggle', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ recipe_id: id }) }); renderCards(); renderDashboard(); } if (button.dataset.category) { category = button.dataset.category; document.querySelectorAll('[data-category]').forEach(item => item.classList.toggle('active', item.dataset.category === category)); renderCards(); }     if (button.dataset.quick) { record(button.dataset.quick); location.href = `/rekomendasi?q=${encodeURIComponent(button.dataset.quick)}`; } if (button.dataset.chat) { chat(button.dataset.chat); } if (button.dataset.planRecipe) { const select = document.querySelector(`select[data-plan-recipe="${button.dataset.planRecipe}"]`); if (!select?.value) { toast('Pilih hari terlebih dahulu.'); return; } plan[select.value] = button.dataset.planRecipe; write('plan', plan); toast(`${select.value} ditambahkan ke rencana masak.`); } if (button.id === 'open-chat-history') { loadChatHistory(); } if (button.id === 'close-chat-history') { document.querySelector('#chat-history-panel').hidden = true; } if (button.dataset.chatConversation) { openChat(button.dataset.chatConversation); } if (button.id === 'reset-chat') { chatConversationId = null; chatHistory = []; document.querySelector('#messages').innerHTML = '<div class="message">Halo, Teman Dapur!<br>Ada bahan apa di dapurmu hari ini?</div>'; } if (button.id === 'mobile-more') { const menu = document.querySelector('#mobile-more-menu'); const open = menu.hidden; menu.hidden = !open; button.setAttribute('aria-expanded', String(open)); } if (button.id === 'clear-history') { history = []; if (document.body.dataset.authenticated !== '1') write('history', history); saveUserData('/api/history', { method: 'DELETE' }); renderHistory(); } if (button.dataset.deleteHistory !== undefined) { const historyIndex = Number(button.dataset.deleteHistory); const historyItem = history[historyIndex]; history.splice(historyIndex, 1); if (document.body.dataset.authenticated !== '1') write('history', history); if (historyItem?.id) saveUserData(`/api/history/${historyItem.id}`, { method: 'DELETE' }); renderHistory(); } });
  document.addEventListener('submit', async event => { const form = event.target; if (form.id === 'auth-form' || form.classList.contains('logout-form')) return; event.preventDefault(); if (form.id === 'search-form') { query = form.elements.q.value.trim(); if (query) record(query); if (page === 'home') location.href = `/rekomendasi?q=${encodeURIComponent(query)}`; else if (query.length >= 2) searchRecipes(query); else loadRecipes(); } if (form.id === 'chat-form') { chat(form.elements.message.value); form.reset(); } });
  document.addEventListener('change', event => { const element = event.target; if (element.id === 'saved-filter') { onlySaved = element.value === 'saved'; renderCards(); } if (element.dataset.day) { if (element.value) plan[element.dataset.day] = Number(element.value); else delete plan[element.dataset.day]; write('plan', plan); renderPlanner(); } });
  document.querySelector('#recipe-dialog')?.addEventListener('click', event => { if (event.target === event.currentTarget) event.currentTarget.close(); });
})();
