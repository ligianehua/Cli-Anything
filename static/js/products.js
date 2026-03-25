/* ===== Products Page ===== */

Pages.products = {
    products: [],
    categories: [],

    render() {
        return `
        <div class="p-6 space-y-6">
            <div class="flex items-center justify-between">
                <h1 class="text-2xl font-bold text-white">Products</h1>
                <div class="flex gap-3">
                    <button onclick="Pages.products.showCategoryModal()" class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-xl text-sm transition">
                        Categories
                    </button>
                    <button onclick="Pages.products.showAddModal()" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm transition flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                        Add Product
                    </button>
                </div>
            </div>

            <!-- Search -->
            <div class="flex gap-3">
                <div class="flex-1 relative">
                    <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                    <input type="text" id="prod-search" placeholder="Search products..."
                           class="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 text-sm">
                </div>
                <select id="prod-cat-filter" class="px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm">
                    <option value="">All Categories</option>
                </select>
            </div>

            <!-- Table -->
            <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full">
                        <thead>
                            <tr class="border-b border-slate-700">
                                <th class="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Product</th>
                                <th class="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">SKU</th>
                                <th class="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Category</th>
                                <th class="text-right px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Cost</th>
                                <th class="text-right px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Price</th>
                                <th class="text-right px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Stock</th>
                                <th class="text-center px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Status</th>
                                <th class="text-center px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="prod-tbody">
                            <tr><td colspan="8" class="text-center py-8 text-slate-500 text-sm">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>`;
    },

    async init() {
        await this.loadData();

        document.getElementById('prod-search').addEventListener('input', () => this.renderTable());
        document.getElementById('prod-cat-filter').addEventListener('change', () => this.renderTable());
    },

    async loadData() {
        const [products, categories] = await Promise.all([
            API.get('/api/products'),
            API.get('/api/categories'),
        ]);
        this.products = products || [];
        this.categories = categories || [];

        // Populate category filter
        const select = document.getElementById('prod-cat-filter');
        if (select) {
            select.innerHTML = '<option value="">All Categories</option>' +
                this.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        }

        this.renderTable();
    },

    renderTable() {
        const q = (document.getElementById('prod-search')?.value || '').toLowerCase();
        const catId = document.getElementById('prod-cat-filter')?.value;

        let filtered = this.products;
        if (q) filtered = filtered.filter(p => p.name.toLowerCase().includes(q) || (p.sku && p.sku.toLowerCase().includes(q)));
        if (catId) filtered = filtered.filter(p => p.category_id == catId);

        const tbody = document.getElementById('prod-tbody');
        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center py-8 text-slate-500 text-sm">No products found</td></tr>';
            return;
        }

        tbody.innerHTML = filtered.map(p => `
            <tr class="border-b border-slate-700/50 hover:bg-slate-700/30 transition">
                <td class="px-5 py-3">
                    <div class="text-sm font-medium text-white">${p.name}</div>
                    ${p.barcode ? `<div class="text-xs text-slate-500">${p.barcode}</div>` : ''}
                </td>
                <td class="px-5 py-3 text-sm text-slate-400">${p.sku || '-'}</td>
                <td class="px-5 py-3 text-sm text-slate-400">${p.category_name || '-'}</td>
                <td class="px-5 py-3 text-sm text-slate-400 text-right">${money(p.cost)}</td>
                <td class="px-5 py-3 text-sm text-green-400 text-right font-medium">${money(p.price)}</td>
                <td class="px-5 py-3 text-right">
                    <span class="text-sm ${p.stock <= 10 ? 'text-yellow-400' : 'text-white'} ${p.stock <= 0 ? 'text-red-400' : ''}">${p.stock}</span>
                </td>
                <td class="px-5 py-3 text-center">
                    <span class="px-2 py-1 rounded-full text-xs ${p.is_active ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'}">${p.is_active ? 'Active' : 'Inactive'}</span>
                </td>
                <td class="px-5 py-3 text-center">
                    <button onclick='Pages.products.showEditModal(${JSON.stringify(p).replace(/'/g, "&#39;")})' class="text-blue-400 hover:text-blue-300 text-sm mr-2">Edit</button>
                    <button onclick="Pages.products.toggleActive(${p.id}, ${p.is_active})" class="text-slate-400 hover:text-red-400 text-sm">${p.is_active ? 'Disable' : 'Enable'}</button>
                </td>
            </tr>
        `).join('');
    },

    showAddModal() {
        showModal(`
            <div class="p-6 space-y-4">
                <h2 class="text-xl font-bold text-white">Add Product</h2>
                <form id="prod-form" class="space-y-3">
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Name *</label>
                        <input type="text" name="name" required class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-sm text-slate-400 mb-1">SKU</label>
                            <input type="text" name="sku" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                        </div>
                        <div>
                            <label class="block text-sm text-slate-400 mb-1">Barcode</label>
                            <input type="text" name="barcode" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Category</label>
                        <select name="category_id" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                            <option value="">None</option>
                            ${this.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="grid grid-cols-3 gap-3">
                        <div>
                            <label class="block text-sm text-slate-400 mb-1">Cost</label>
                            <input type="number" name="cost" value="0" min="0" step="0.01" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                        </div>
                        <div>
                            <label class="block text-sm text-slate-400 mb-1">Price *</label>
                            <input type="number" name="price" value="0" min="0" step="0.01" required class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                        </div>
                        <div>
                            <label class="block text-sm text-slate-400 mb-1">Stock</label>
                            <input type="number" name="stock" value="0" min="0" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                        </div>
                    </div>
                    <div class="flex gap-3 pt-2">
                        <button type="button" onclick="hideModal()" class="flex-1 py-2.5 bg-slate-600 hover:bg-slate-500 text-white rounded-xl text-sm transition">Cancel</button>
                        <button type="submit" class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm transition">Add Product</button>
                    </div>
                </form>
            </div>
        `);

        document.getElementById('prod-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData(e.target);
            const data = Object.fromEntries(fd);
            data.category_id = data.category_id ? parseInt(data.category_id) : null;
            data.price = parseFloat(data.price);
            data.cost = parseFloat(data.cost);
            data.stock = parseInt(data.stock);

            const res = await API.post('/api/products', data);
            if (res?.ok) {
                hideModal();
                toast('Product added');
                await this.loadData();
            } else {
                toast(res?.data?.error || 'Failed', 'error');
            }
        });
    },

    showEditModal(product) {
        showModal(`
            <div class="p-6 space-y-4">
                <h2 class="text-xl font-bold text-white">Edit Product</h2>
                <form id="prod-edit-form" class="space-y-3">
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Name *</label>
                        <input type="text" name="name" value="${product.name}" required class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-sm text-slate-400 mb-1">SKU</label>
                            <input type="text" name="sku" value="${product.sku || ''}" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                        </div>
                        <div>
                            <label class="block text-sm text-slate-400 mb-1">Barcode</label>
                            <input type="text" name="barcode" value="${product.barcode || ''}" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                        </div>
                    </div>
                    <div>
                        <label class="block text-sm text-slate-400 mb-1">Category</label>
                        <select name="category_id" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                            <option value="">None</option>
                            ${this.categories.map(c => `<option value="${c.id}" ${c.id === product.category_id ? 'selected' : ''}>${c.name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="grid grid-cols-3 gap-3">
                        <div>
                            <label class="block text-sm text-slate-400 mb-1">Cost</label>
                            <input type="number" name="cost" value="${product.cost}" min="0" step="0.01" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                        </div>
                        <div>
                            <label class="block text-sm text-slate-400 mb-1">Price *</label>
                            <input type="number" name="price" value="${product.price}" min="0" step="0.01" required class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                        </div>
                        <div>
                            <label class="block text-sm text-slate-400 mb-1">Stock</label>
                            <input type="number" name="stock" value="${product.stock}" min="0" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                        </div>
                    </div>
                    <div class="flex gap-3 pt-2">
                        <button type="button" onclick="hideModal()" class="flex-1 py-2.5 bg-slate-600 hover:bg-slate-500 text-white rounded-xl text-sm transition">Cancel</button>
                        <button type="submit" class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm transition">Save Changes</button>
                    </div>
                </form>
            </div>
        `);

        document.getElementById('prod-edit-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData(e.target);
            const data = Object.fromEntries(fd);
            data.category_id = data.category_id ? parseInt(data.category_id) : null;
            data.price = parseFloat(data.price);
            data.cost = parseFloat(data.cost);
            data.stock = parseInt(data.stock);

            const res = await API.put(`/api/products/${product.id}`, data);
            if (res?.ok) {
                hideModal();
                toast('Product updated');
                await this.loadData();
            } else {
                toast(res?.data?.error || 'Failed', 'error');
            }
        });
    },

    async toggleActive(id, isActive) {
        const res = await API.put(`/api/products/${id}`, { is_active: !isActive });
        if (res?.ok) {
            toast(isActive ? 'Product disabled' : 'Product enabled');
            await this.loadData();
        }
    },

    showCategoryModal() {
        const renderCats = () => {
            return this.categories.map(c => `
                <div class="flex items-center justify-between py-2 border-b border-slate-700/50 last:border-0">
                    <span class="text-sm text-white">${c.name}</span>
                    <button onclick="Pages.products.deleteCategory(${c.id})" class="text-xs text-slate-400 hover:text-red-400">Delete</button>
                </div>
            `).join('') || '<div class="text-sm text-slate-500 text-center py-4">No categories</div>';
        };

        showModal(`
            <div class="p-6 space-y-4">
                <h2 class="text-xl font-bold text-white">Categories</h2>
                <div id="cat-list">${renderCats()}</div>
                <div class="flex gap-2">
                    <input type="text" id="new-cat-name" placeholder="New category name"
                           class="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm placeholder-slate-500">
                    <button onclick="Pages.products.addCategory()" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition">Add</button>
                </div>
            </div>
        `);
    },

    async addCategory() {
        const input = document.getElementById('new-cat-name');
        const name = input.value.trim();
        if (!name) return;
        const res = await API.post('/api/categories', { name });
        if (res?.ok) {
            toast('Category added');
            await this.loadData();
            this.showCategoryModal();
        }
    },

    async deleteCategory(id) {
        if (!confirm('Delete this category?')) return;
        const res = await API.del(`/api/categories/${id}`);
        if (res?.ok) {
            toast('Category deleted');
            await this.loadData();
            this.showCategoryModal();
        }
    },
};
