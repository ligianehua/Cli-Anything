/* ===== Users Page (Admin Only) ===== */

Pages.users = {
    users: [],

    render() {
        return `
        <div class="p-6 space-y-6">
            <div class="flex items-center justify-between">
                <h1 class="text-2xl font-bold text-white">Users</h1>
                <button onclick="Pages.users.showAddModal()" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm transition flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                    Add User
                </button>
            </div>

            <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-slate-700">
                            <th class="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Name</th>
                            <th class="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Email</th>
                            <th class="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Role</th>
                            <th class="text-center px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Status</th>
                            <th class="text-center px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="users-tbody">
                        <tr><td colspan="5" class="text-center py-8 text-slate-500 text-sm">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>`;
    },

    async init() {
        await this.load();
    },

    async load() {
        const data = await API.get('/api/users');
        this.users = data || [];
        this.renderTable();
    },

    renderTable() {
        const tbody = document.getElementById('users-tbody');
        if (this.users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8 text-slate-500 text-sm">No users</td></tr>';
            return;
        }

        tbody.innerHTML = this.users.map(u => `
            <tr class="border-b border-slate-700/50 hover:bg-slate-700/30 transition">
                <td class="px-5 py-3">
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center text-sm font-bold text-white">${u.name[0].toUpperCase()}</div>
                        <span class="text-sm font-medium text-white">${u.name}</span>
                    </div>
                </td>
                <td class="px-5 py-3 text-sm text-slate-400">${u.email}</td>
                <td class="px-5 py-3">
                    <span class="px-2 py-1 rounded-full text-xs ${
                        u.role === 'admin' ? 'bg-purple-900/50 text-purple-400' :
                        u.role === 'manager' ? 'bg-blue-900/50 text-blue-400' :
                        'bg-slate-700 text-slate-300'
                    }">${u.role}</span>
                </td>
                <td class="px-5 py-3 text-center">
                    <span class="px-2 py-1 rounded-full text-xs ${u.is_active ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'}">${u.is_active ? 'Active' : 'Inactive'}</span>
                </td>
                <td class="px-5 py-3 text-center">
                    <button onclick='Pages.users.showEditModal(${JSON.stringify(u).replace(/'/g, "&#39;")})' class="text-blue-400 hover:text-blue-300 text-sm mr-2">Edit</button>
                    <button onclick="Pages.users.toggleActive(${u.id}, ${u.is_active})" class="text-sm ${u.is_active ? 'text-red-400 hover:text-red-300' : 'text-green-400 hover:text-green-300'}">${u.is_active ? 'Deactivate' : 'Activate'}</button>
                </td>
            </tr>
        `).join('');
    },

    showAddModal() {
        showModal(`
            <div class="p-6 space-y-4">
                <h2 class="text-xl font-bold text-white">Add User</h2>
                <form id="user-form" class="space-y-3">
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Name *</label>
                        <input type="text" name="name" required class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                    </div>
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Email *</label>
                        <input type="email" name="email" required class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                    </div>
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Password *</label>
                        <input type="password" name="password" required minlength="6" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                    </div>
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Role</label>
                        <select name="role" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                            <option value="cashier">Cashier</option>
                            <option value="manager">Manager</option>
                            <option value="admin">Admin</option>
                        </select>
                    </div>
                    <div class="flex gap-3 pt-2">
                        <button type="button" onclick="hideModal()" class="flex-1 py-2.5 bg-slate-600 hover:bg-slate-500 text-white rounded-xl text-sm transition">Cancel</button>
                        <button type="submit" class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm transition">Add User</button>
                    </div>
                </form>
            </div>
        `);

        document.getElementById('user-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData(e.target);
            const data = Object.fromEntries(fd);
            const res = await API.post('/api/users', data);
            if (res?.ok) {
                hideModal();
                toast('User added');
                await this.load();
            } else {
                toast(res?.data?.error || 'Failed', 'error');
            }
        });
    },

    showEditModal(user) {
        showModal(`
            <div class="p-6 space-y-4">
                <h2 class="text-xl font-bold text-white">Edit User</h2>
                <form id="user-edit-form" class="space-y-3">
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Name *</label>
                        <input type="text" name="name" value="${user.name}" required class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                    </div>
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Email *</label>
                        <input type="email" name="email" value="${user.email}" required class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                    </div>
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">New Password (leave blank to keep)</label>
                        <input type="password" name="password" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                    </div>
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Role</label>
                        <select name="role" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                            <option value="cashier" ${user.role === 'cashier' ? 'selected' : ''}>Cashier</option>
                            <option value="manager" ${user.role === 'manager' ? 'selected' : ''}>Manager</option>
                            <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Admin</option>
                        </select>
                    </div>
                    <div class="flex gap-3 pt-2">
                        <button type="button" onclick="hideModal()" class="flex-1 py-2.5 bg-slate-600 hover:bg-slate-500 text-white rounded-xl text-sm transition">Cancel</button>
                        <button type="submit" class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm transition">Save Changes</button>
                    </div>
                </form>
            </div>
        `);

        document.getElementById('user-edit-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData(e.target);
            const data = Object.fromEntries(fd);
            if (!data.password) delete data.password;
            const res = await API.put(`/api/users/${user.id}`, data);
            if (res?.ok) {
                hideModal();
                toast('User updated');
                await this.load();
            } else {
                toast(res?.data?.error || 'Failed', 'error');
            }
        });
    },

    async toggleActive(id, isActive) {
        const res = await API.put(`/api/users/${id}`, { is_active: !isActive });
        if (res?.ok) {
            toast(isActive ? 'User deactivated' : 'User activated');
            await this.load();
        }
    },
};
