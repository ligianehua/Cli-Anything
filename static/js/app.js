/* ===== VeraPOS Core ===== */

const API = {
    token: () => localStorage.getItem('token'),
    headers: () => ({
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
    }),
    async get(url) {
        const res = await fetch(url, { headers: this.headers() });
        if (res.status === 401) { logout(); return null; }
        return res.json();
    },
    async post(url, data) {
        const res = await fetch(url, { method: 'POST', headers: this.headers(), body: JSON.stringify(data) });
        if (res.status === 401) { logout(); return null; }
        return { ok: res.ok, status: res.status, data: await res.json() };
    },
    async put(url, data) {
        const res = await fetch(url, { method: 'PUT', headers: this.headers(), body: JSON.stringify(data) });
        if (res.status === 401) { logout(); return null; }
        return { ok: res.ok, status: res.status, data: await res.json() };
    },
    async del(url) {
        const res = await fetch(url, { method: 'DELETE', headers: this.headers() });
        if (res.status === 401) { logout(); return null; }
        return { ok: res.ok };
    },
};

// Pages registry
const Pages = {};
let currentPage = null;

function initApp() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    document.getElementById('userName').textContent = user.name || 'User';
    document.getElementById('userRole').textContent = user.role || '';
    document.getElementById('userAvatar').textContent = (user.name || 'U')[0].toUpperCase();

    // Hide users nav for non-admins
    if (user.role !== 'admin') {
        const usersNav = document.getElementById('nav-users');
        if (usersNav) usersNav.style.display = 'none';
    }

    // Nav click handlers
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navigate(link.dataset.page);
        });
    });

    // Default page
    navigate('dashboard');
}

function navigate(page) {
    if (!Pages[page]) return;
    currentPage = page;

    // Update sidebar
    document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
    const activeLink = document.querySelector(`[data-page="${page}"]`);
    if (activeLink) activeLink.classList.add('active');

    // Update pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const pageEl = document.getElementById(`page-${page}`);
    pageEl.innerHTML = Pages[page].render();
    pageEl.classList.add('active');
    Pages[page].init();
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// Modal helpers
function showModal(html) {
    document.getElementById('modal-content').innerHTML = html;
    document.getElementById('modal').classList.remove('hidden');
}

function hideModal() {
    document.getElementById('modal').classList.add('hidden');
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
    if (e.target.id === 'modal') hideModal();
});

// Format currency
function money(n) {
    return '₱' + Number(n || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Format date
function fmtDate(iso) {
    if (!iso) return '-';
    const d = new Date(iso);
    return d.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// Toast notification
function toast(msg, type = 'success') {
    const t = document.createElement('div');
    t.className = `fixed top-4 right-4 z-[100] px-5 py-3 rounded-xl shadow-lg text-white text-sm font-medium transition-all duration-300 ${
        type === 'success' ? 'bg-green-600' : type === 'error' ? 'bg-red-600' : 'bg-blue-600'
    }`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; setTimeout(() => t.remove(), 300); }, 3000);
}
