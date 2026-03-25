/* ===== Dashboard Page ===== */

Pages.dashboard = {
    render() {
        return `
        <div class="p-6 space-y-6">
            <div class="flex items-center justify-between">
                <h1 class="text-2xl font-bold text-white">Dashboard</h1>
                <div class="text-sm text-slate-400" id="dash-date"></div>
            </div>

            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" id="dash-stats">
                ${[1,2,3,4].map(() => `
                    <div class="bg-slate-800 rounded-xl p-5 border border-slate-700 animate-pulse">
                        <div class="h-4 bg-slate-700 rounded w-24 mb-3"></div>
                        <div class="h-8 bg-slate-700 rounded w-32"></div>
                    </div>
                `).join('')}
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Recent Sales -->
                <div class="bg-slate-800 rounded-xl border border-slate-700">
                    <div class="px-5 py-4 border-b border-slate-700">
                        <h2 class="font-semibold text-white">Recent Sales</h2>
                    </div>
                    <div id="dash-recent" class="p-5">
                        <div class="text-slate-500 text-sm">Loading...</div>
                    </div>
                </div>

                <!-- Top Products -->
                <div class="bg-slate-800 rounded-xl border border-slate-700">
                    <div class="px-5 py-4 border-b border-slate-700">
                        <h2 class="font-semibold text-white">Top Products</h2>
                    </div>
                    <div id="dash-top" class="p-5">
                        <div class="text-slate-500 text-sm">Loading...</div>
                    </div>
                </div>
            </div>
        </div>`;
    },

    async init() {
        document.getElementById('dash-date').textContent = new Date().toLocaleDateString('en-PH', {
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
        });

        const data = await API.get('/api/dashboard/stats');
        if (!data) return;

        document.getElementById('dash-stats').innerHTML = `
            <div class="stat-card bg-slate-800 rounded-xl p-5 border border-slate-700">
                <div class="text-sm text-slate-400 mb-1">Today's Revenue</div>
                <div class="text-2xl font-bold text-green-400">${money(data.revenue_today)}</div>
                <div class="text-xs text-slate-500 mt-1">${data.sales_today} transactions</div>
            </div>
            <div class="stat-card bg-slate-800 rounded-xl p-5 border border-slate-700">
                <div class="text-sm text-slate-400 mb-1">This Week</div>
                <div class="text-2xl font-bold text-blue-400">${money(data.revenue_week)}</div>
                <div class="text-xs text-slate-500 mt-1">Last 7 days</div>
            </div>
            <div class="stat-card bg-slate-800 rounded-xl p-5 border border-slate-700">
                <div class="text-sm text-slate-400 mb-1">Total Products</div>
                <div class="text-2xl font-bold text-white">${data.total_products}</div>
                <div class="text-xs ${data.low_stock > 0 ? 'text-yellow-400' : 'text-slate-500'} mt-1">${data.low_stock} low stock</div>
            </div>
            <div class="stat-card bg-slate-800 rounded-xl p-5 border border-slate-700">
                <div class="text-sm text-slate-400 mb-1">All-time Revenue</div>
                <div class="text-2xl font-bold text-purple-400">${money(data.revenue_all)}</div>
                <div class="text-xs text-slate-500 mt-1">${data.total_sales} total sales</div>
            </div>
        `;

        // Recent sales
        if (data.recent_sales.length === 0) {
            document.getElementById('dash-recent').innerHTML = '<div class="text-slate-500 text-sm text-center py-4">No sales yet</div>';
        } else {
            document.getElementById('dash-recent').innerHTML = `
                <div class="space-y-3">
                    ${data.recent_sales.slice(0, 8).map(s => `
                        <div class="flex items-center justify-between py-2 border-b border-slate-700/50 last:border-0">
                            <div>
                                <div class="text-sm font-medium text-white">${s.reference}</div>
                                <div class="text-xs text-slate-400">${s.cashier_name} &middot; ${fmtDate(s.created_at)}</div>
                            </div>
                            <div class="text-sm font-semibold text-green-400">${money(s.total)}</div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        // Top products
        if (data.top_products.length === 0) {
            document.getElementById('dash-top').innerHTML = '<div class="text-slate-500 text-sm text-center py-4">No data yet</div>';
        } else {
            document.getElementById('dash-top').innerHTML = `
                <div class="space-y-3">
                    ${data.top_products.map((p, i) => `
                        <div class="flex items-center justify-between py-2 border-b border-slate-700/50 last:border-0">
                            <div class="flex items-center gap-3">
                                <span class="w-6 h-6 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center text-xs font-bold">${i + 1}</span>
                                <div>
                                    <div class="text-sm font-medium text-white">${p.name}</div>
                                    <div class="text-xs text-slate-400">${p.quantity} sold</div>
                                </div>
                            </div>
                            <div class="text-sm text-slate-300">${money(p.revenue)}</div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
    },
};
