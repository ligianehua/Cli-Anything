/* ===== Sales History Page ===== */

Pages.sales = {
    render() {
        return `
        <div class="p-6 space-y-6">
            <div class="flex items-center justify-between">
                <h1 class="text-2xl font-bold text-white">Sales History</h1>
            </div>

            <!-- Filters -->
            <div class="flex gap-3 flex-wrap">
                <input type="date" id="sales-from" class="px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm">
                <input type="date" id="sales-to" class="px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm">
                <button onclick="Pages.sales.load()" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm transition">Filter</button>
                <button onclick="Pages.sales.clearFilter()" class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-xl text-sm transition">Clear</button>
            </div>

            <!-- Table -->
            <div class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="w-full">
                        <thead>
                            <tr class="border-b border-slate-700">
                                <th class="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Reference</th>
                                <th class="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Cashier</th>
                                <th class="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Customer</th>
                                <th class="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Payment</th>
                                <th class="text-right px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Total</th>
                                <th class="text-left px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Date</th>
                                <th class="text-center px-5 py-3 text-xs font-semibold text-slate-400 uppercase">Details</th>
                            </tr>
                        </thead>
                        <tbody id="sales-tbody">
                            <tr><td colspan="7" class="text-center py-8 text-slate-500 text-sm">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Pagination -->
            <div class="flex items-center justify-between" id="sales-pagination"></div>
        </div>`;
    },

    currentPage: 1,

    async init() {
        await this.load();
    },

    clearFilter() {
        document.getElementById('sales-from').value = '';
        document.getElementById('sales-to').value = '';
        this.currentPage = 1;
        this.load();
    },

    async load() {
        let url = `/api/sales?page=${this.currentPage}&per_page=15`;
        const from = document.getElementById('sales-from')?.value;
        const to = document.getElementById('sales-to')?.value;
        if (from) url += `&from=${from}`;
        if (to) url += `&to=${to}`;

        const data = await API.get(url);
        if (!data) return;

        const tbody = document.getElementById('sales-tbody');
        if (data.sales.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-slate-500 text-sm">No sales found</td></tr>';
            document.getElementById('sales-pagination').innerHTML = '';
            return;
        }

        tbody.innerHTML = data.sales.map(s => `
            <tr class="border-b border-slate-700/50 hover:bg-slate-700/30 transition">
                <td class="px-5 py-3 text-sm font-mono text-blue-400">${s.reference}</td>
                <td class="px-5 py-3 text-sm text-slate-300">${s.cashier_name || '-'}</td>
                <td class="px-5 py-3 text-sm text-slate-400">${s.customer_name}</td>
                <td class="px-5 py-3">
                    <span class="px-2 py-1 rounded-full text-xs ${
                        s.payment_method === 'cash' ? 'bg-green-900/50 text-green-400' :
                        s.payment_method === 'gcash' ? 'bg-blue-900/50 text-blue-400' :
                        'bg-purple-900/50 text-purple-400'
                    }">${s.payment_method}</span>
                </td>
                <td class="px-5 py-3 text-sm text-green-400 text-right font-medium">${money(s.total)}</td>
                <td class="px-5 py-3 text-sm text-slate-400">${fmtDate(s.created_at)}</td>
                <td class="px-5 py-3 text-center">
                    <button onclick="Pages.sales.showDetail(${s.id})" class="text-blue-400 hover:text-blue-300 text-sm">View</button>
                </td>
            </tr>
        `).join('');

        // Pagination
        document.getElementById('sales-pagination').innerHTML = `
            <div class="text-sm text-slate-400">Page ${data.page} of ${data.pages} (${data.total} total)</div>
            <div class="flex gap-2">
                <button onclick="Pages.sales.goPage(${data.page - 1})" class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition ${data.page <= 1 ? 'opacity-50 cursor-not-allowed' : ''}" ${data.page <= 1 ? 'disabled' : ''}>Prev</button>
                <button onclick="Pages.sales.goPage(${data.page + 1})" class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm transition ${data.page >= data.pages ? 'opacity-50 cursor-not-allowed' : ''}" ${data.page >= data.pages ? 'disabled' : ''}>Next</button>
            </div>
        `;
    },

    goPage(page) {
        this.currentPage = page;
        this.load();
    },

    async showDetail(saleId) {
        const sale = await API.get(`/api/sales/${saleId}`);
        if (!sale) return;

        showModal(`
            <div class="p-6 space-y-4">
                <div class="flex items-center justify-between">
                    <h2 class="text-xl font-bold text-white">Sale Details</h2>
                    <span class="text-sm font-mono text-blue-400">${sale.reference}</span>
                </div>

                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span class="text-slate-400">Cashier</span>
                        <div class="text-white">${sale.cashier_name || '-'}</div>
                    </div>
                    <div>
                        <span class="text-slate-400">Customer</span>
                        <div class="text-white">${sale.customer_name}</div>
                    </div>
                    <div>
                        <span class="text-slate-400">Payment</span>
                        <div class="text-white capitalize">${sale.payment_method}</div>
                    </div>
                    <div>
                        <span class="text-slate-400">Date</span>
                        <div class="text-white">${fmtDate(sale.created_at)}</div>
                    </div>
                </div>

                <div class="bg-slate-700/50 rounded-xl overflow-hidden">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="border-b border-slate-600">
                                <th class="text-left px-4 py-2 text-slate-400">Item</th>
                                <th class="text-right px-4 py-2 text-slate-400">Price</th>
                                <th class="text-right px-4 py-2 text-slate-400">Qty</th>
                                <th class="text-right px-4 py-2 text-slate-400">Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${sale.items.map(i => `
                                <tr class="border-b border-slate-600/50">
                                    <td class="px-4 py-2 text-white">${i.product_name}</td>
                                    <td class="px-4 py-2 text-right text-slate-300">${money(i.price)}</td>
                                    <td class="px-4 py-2 text-right text-slate-300">${i.quantity}</td>
                                    <td class="px-4 py-2 text-right text-white">${money(i.subtotal)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>

                <div class="space-y-1 text-sm">
                    <div class="flex justify-between"><span class="text-slate-400">Subtotal</span><span class="text-white">${money(sale.subtotal)}</span></div>
                    ${sale.discount > 0 ? `<div class="flex justify-between"><span class="text-slate-400">Discount</span><span class="text-red-400">-${money(sale.discount)}</span></div>` : ''}
                    <div class="flex justify-between text-lg font-bold border-t border-slate-600 pt-2"><span class="text-white">Total</span><span class="text-green-400">${money(sale.total)}</span></div>
                    ${sale.payment_method === 'cash' ? `
                        <div class="flex justify-between"><span class="text-slate-400">Paid</span><span class="text-white">${money(sale.amount_paid)}</span></div>
                        <div class="flex justify-between"><span class="text-slate-400">Change</span><span class="text-yellow-400">${money(sale.change_amount)}</span></div>
                    ` : ''}
                </div>

                <button onclick="hideModal()" class="w-full py-2.5 bg-slate-600 hover:bg-slate-500 text-white rounded-xl text-sm transition">Close</button>
            </div>
        `);
    },
};
