/* ===== POS Page ===== */

Pages.pos = {
    cart: [],
    products: [],
    categories: [],

    render() {
        return `
        <div class="flex h-full">
            <!-- Left: Products -->
            <div class="flex-1 flex flex-col border-r border-slate-700">
                <!-- Search bar -->
                <div class="p-4 border-b border-slate-700 space-y-3">
                    <div class="flex gap-3">
                        <div class="flex-1 relative">
                            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                            <input type="text" id="pos-search" placeholder="Search products or scan barcode..."
                                   class="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-600 rounded-xl text-white placeholder-slate-500 text-sm">
                        </div>
                    </div>
                    <div class="flex gap-2 overflow-x-auto pb-1" id="pos-categories">
                        <button onclick="Pages.pos.filterCategory(null)" class="cat-btn active px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 text-white whitespace-nowrap">All</button>
                    </div>
                </div>

                <!-- Product Grid -->
                <div class="flex-1 overflow-y-auto p-4">
                    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3" id="pos-products">
                        <div class="text-slate-500 text-sm col-span-full text-center py-8">Loading products...</div>
                    </div>
                </div>
            </div>

            <!-- Right: Cart -->
            <div class="w-96 flex flex-col bg-slate-800/50 flex-shrink-0">
                <div class="p-4 border-b border-slate-700">
                    <div class="flex items-center justify-between">
                        <h2 class="font-semibold text-white text-lg">Cart</h2>
                        <button onclick="Pages.pos.clearCart()" class="text-xs text-slate-400 hover:text-red-400 transition">Clear All</button>
                    </div>
                </div>

                <!-- Cart Items -->
                <div class="flex-1 overflow-y-auto" id="pos-cart">
                    <div class="text-slate-500 text-sm text-center py-8">Cart is empty</div>
                </div>

                <!-- Cart Summary -->
                <div class="border-t border-slate-700 p-4 space-y-3">
                    <div class="space-y-2">
                        <div class="flex justify-between text-sm">
                            <span class="text-slate-400">Subtotal</span>
                            <span class="text-white" id="pos-subtotal">${money(0)}</span>
                        </div>
                        <div class="flex items-center justify-between text-sm">
                            <span class="text-slate-400">Discount</span>
                            <input type="number" id="pos-discount" value="0" min="0" step="0.01"
                                   onchange="Pages.pos.updateTotals()"
                                   class="w-24 text-right bg-slate-700 border border-slate-600 rounded-lg px-2 py-1 text-white text-sm">
                        </div>
                        <div class="flex justify-between text-lg font-bold border-t border-slate-600 pt-2">
                            <span class="text-white">Total</span>
                            <span class="text-green-400" id="pos-total">${money(0)}</span>
                        </div>
                    </div>

                    <div>
                        <input type="text" id="pos-customer" placeholder="Customer name (optional)"
                               class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm placeholder-slate-500 mb-3">
                        <button onclick="Pages.pos.checkout()"
                                class="w-full py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl transition text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                                id="pos-checkout-btn" disabled>
                            Charge
                        </button>
                    </div>
                </div>
            </div>
        </div>`;
    },

    async init() {
        this.cart = [];
        const [products, categories] = await Promise.all([
            API.get('/api/products?active=1'),
            API.get('/api/categories'),
        ]);
        this.products = products || [];
        this.categories = categories || [];

        // Render categories
        const catContainer = document.getElementById('pos-categories');
        catContainer.innerHTML = `
            <button onclick="Pages.pos.filterCategory(null)" class="cat-btn active px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 text-white whitespace-nowrap">All</button>
            ${this.categories.map(c => `
                <button onclick="Pages.pos.filterCategory(${c.id})" class="cat-btn px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-700 text-slate-300 hover:bg-slate-600 whitespace-nowrap">${c.name}</button>
            `).join('')}
        `;

        this.renderProducts(this.products);

        // Search
        document.getElementById('pos-search').addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase();
            const filtered = this.products.filter(p =>
                p.name.toLowerCase().includes(q) ||
                (p.sku && p.sku.toLowerCase().includes(q)) ||
                (p.barcode && p.barcode.toLowerCase().includes(q))
            );
            this.renderProducts(filtered);
        });
    },

    filterCategory(catId) {
        document.querySelectorAll('.cat-btn').forEach(b => {
            b.className = 'cat-btn px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-700 text-slate-300 hover:bg-slate-600 whitespace-nowrap';
        });
        event.target.className = 'cat-btn active px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 text-white whitespace-nowrap';

        const filtered = catId ? this.products.filter(p => p.category_id === catId) : this.products;
        const q = document.getElementById('pos-search').value.toLowerCase();
        const final = q ? filtered.filter(p => p.name.toLowerCase().includes(q)) : filtered;
        this.renderProducts(final);
    },

    renderProducts(products) {
        const container = document.getElementById('pos-products');
        if (products.length === 0) {
            container.innerHTML = '<div class="text-slate-500 text-sm col-span-full text-center py-8">No products found</div>';
            return;
        }
        container.innerHTML = products.map(p => `
            <div class="product-card bg-slate-800 rounded-xl border border-slate-700 p-4 cursor-pointer select-none ${p.stock <= 0 ? 'opacity-40' : ''}"
                 onclick="${p.stock > 0 ? `Pages.pos.addToCart(${p.id})` : ''}">
                <div class="w-full h-16 bg-slate-700/50 rounded-lg flex items-center justify-center mb-3">
                    <svg class="w-8 h-8 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
                </div>
                <div class="text-sm font-medium text-white truncate">${p.name}</div>
                <div class="text-xs text-slate-400 mt-0.5">${p.category_name || 'Uncategorized'}</div>
                <div class="flex items-center justify-between mt-2">
                    <span class="text-sm font-bold text-green-400">${money(p.price)}</span>
                    <span class="text-xs ${p.stock <= 10 ? 'text-yellow-400' : 'text-slate-500'}">${p.stock} left</span>
                </div>
            </div>
        `).join('');
    },

    addToCart(productId) {
        const product = this.products.find(p => p.id === productId);
        if (!product) return;

        const existing = this.cart.find(c => c.product_id === productId);
        if (existing) {
            if (existing.quantity >= product.stock) {
                toast('Not enough stock', 'error');
                return;
            }
            existing.quantity++;
        } else {
            this.cart.push({
                product_id: product.id,
                name: product.name,
                price: product.price,
                quantity: 1,
                max_stock: product.stock,
            });
        }
        this.renderCart();
    },

    removeFromCart(index) {
        this.cart.splice(index, 1);
        this.renderCart();
    },

    updateQty(index, delta) {
        const item = this.cart[index];
        const newQty = item.quantity + delta;
        if (newQty <= 0) {
            this.cart.splice(index, 1);
        } else if (newQty > item.max_stock) {
            toast('Not enough stock', 'error');
            return;
        } else {
            item.quantity = newQty;
        }
        this.renderCart();
    },

    clearCart() {
        this.cart = [];
        this.renderCart();
    },

    renderCart() {
        const container = document.getElementById('pos-cart');
        if (this.cart.length === 0) {
            container.innerHTML = '<div class="text-slate-500 text-sm text-center py-8">Cart is empty</div>';
            document.getElementById('pos-checkout-btn').disabled = true;
        } else {
            container.innerHTML = `
                <div class="divide-y divide-slate-700/50">
                    ${this.cart.map((item, i) => `
                        <div class="cart-item px-4 py-3">
                            <div class="flex justify-between items-start mb-2">
                                <div class="text-sm font-medium text-white flex-1">${item.name}</div>
                                <button onclick="Pages.pos.removeFromCart(${i})" class="ml-2 text-slate-500 hover:text-red-400">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                                </button>
                            </div>
                            <div class="flex items-center justify-between">
                                <div class="flex items-center gap-2">
                                    <button onclick="Pages.pos.updateQty(${i}, -1)" class="w-7 h-7 rounded-lg bg-slate-700 hover:bg-slate-600 flex items-center justify-center text-white text-sm">-</button>
                                    <span class="text-sm text-white w-8 text-center">${item.quantity}</span>
                                    <button onclick="Pages.pos.updateQty(${i}, 1)" class="w-7 h-7 rounded-lg bg-slate-700 hover:bg-slate-600 flex items-center justify-center text-white text-sm">+</button>
                                </div>
                                <span class="text-sm font-medium text-white">${money(item.price * item.quantity)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            document.getElementById('pos-checkout-btn').disabled = false;
        }
        this.updateTotals();
    },

    updateTotals() {
        const subtotal = this.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
        const discount = parseFloat(document.getElementById('pos-discount').value) || 0;
        const total = Math.max(0, subtotal - discount);
        document.getElementById('pos-subtotal').textContent = money(subtotal);
        document.getElementById('pos-total').textContent = money(total);
    },

    checkout() {
        if (this.cart.length === 0) return;
        const subtotal = this.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
        const discount = parseFloat(document.getElementById('pos-discount').value) || 0;
        const total = Math.max(0, subtotal - discount);

        showModal(`
            <div class="p-6 space-y-4">
                <h2 class="text-xl font-bold text-white">Payment</h2>
                <div class="bg-slate-700/50 rounded-xl p-4 space-y-2">
                    <div class="flex justify-between text-sm">
                        <span class="text-slate-400">Items</span>
                        <span class="text-white">${this.cart.reduce((s, i) => s + i.quantity, 0)}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-slate-400">Subtotal</span>
                        <span class="text-white">${money(subtotal)}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-slate-400">Discount</span>
                        <span class="text-white">-${money(discount)}</span>
                    </div>
                    <div class="flex justify-between text-lg font-bold border-t border-slate-600 pt-2">
                        <span class="text-white">Total</span>
                        <span class="text-green-400">${money(total)}</span>
                    </div>
                </div>

                <div>
                    <label class="block text-sm text-slate-400 mb-1">Payment Method</label>
                    <select id="pay-method" class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                        <option value="cash">Cash</option>
                        <option value="gcash">GCash</option>
                        <option value="card">Card</option>
                    </select>
                </div>

                <div id="cash-section">
                    <label class="block text-sm text-slate-400 mb-1">Amount Received</label>
                    <input type="number" id="pay-amount" value="${total}" min="${total}" step="0.01"
                           oninput="Pages.pos.calcChange()"
                           class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm">
                    <div class="flex justify-between mt-2 text-sm">
                        <span class="text-slate-400">Change</span>
                        <span class="text-green-400 font-bold" id="pay-change">${money(0)}</span>
                    </div>

                    <div class="flex gap-2 mt-2">
                        ${[20, 50, 100, 200, 500, 1000].map(v => `
                            <button onclick="document.getElementById('pay-amount').value=${v};Pages.pos.calcChange()"
                                    class="flex-1 py-1.5 bg-slate-600 hover:bg-slate-500 rounded-lg text-xs text-white">${v}</button>
                        `).join('')}
                    </div>
                </div>

                <button onclick="Pages.pos.completeSale()"
                        class="w-full py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-xl transition">
                    Complete Sale
                </button>
            </div>
        `);

        document.getElementById('pay-method').addEventListener('change', (e) => {
            document.getElementById('cash-section').style.display = e.target.value === 'cash' ? 'block' : 'none';
        });
    },

    calcChange() {
        const subtotal = this.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
        const discount = parseFloat(document.getElementById('pos-discount').value) || 0;
        const total = Math.max(0, subtotal - discount);
        const paid = parseFloat(document.getElementById('pay-amount').value) || 0;
        document.getElementById('pay-change').textContent = money(Math.max(0, paid - total));
    },

    async completeSale() {
        const subtotal = this.cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
        const discount = parseFloat(document.getElementById('pos-discount').value) || 0;
        const total = Math.max(0, subtotal - discount);
        const method = document.getElementById('pay-method').value;
        const paid = method === 'cash' ? (parseFloat(document.getElementById('pay-amount').value) || total) : total;
        const customer = document.getElementById('pos-customer').value.trim();

        const res = await API.post('/api/sales', {
            items: this.cart.map(i => ({ product_id: i.product_id, quantity: i.quantity })),
            discount,
            payment_method: method,
            amount_paid: paid,
            customer_name: customer || 'Walk-in',
        });

        if (!res || !res.ok) {
            toast(res?.data?.error || 'Sale failed', 'error');
            return;
        }

        hideModal();
        const sale = res.data;

        // Show receipt
        showModal(`
            <div class="p-6 space-y-4">
                <div class="text-center">
                    <svg class="w-12 h-12 mx-auto text-green-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    <h2 class="text-xl font-bold text-white">Sale Complete!</h2>
                    <p class="text-slate-400 text-sm mt-1">${sale.reference}</p>
                </div>

                <div class="bg-slate-700/50 rounded-xl p-4 space-y-1 text-sm">
                    ${sale.items.map(i => `
                        <div class="flex justify-between">
                            <span class="text-slate-300">${i.product_name} x${i.quantity}</span>
                            <span class="text-white">${money(i.subtotal)}</span>
                        </div>
                    `).join('')}
                    <div class="border-t border-slate-600 mt-2 pt-2 flex justify-between font-bold">
                        <span class="text-white">Total</span>
                        <span class="text-green-400">${money(sale.total)}</span>
                    </div>
                    ${sale.payment_method === 'cash' ? `
                        <div class="flex justify-between">
                            <span class="text-slate-400">Paid</span>
                            <span class="text-white">${money(sale.amount_paid)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-slate-400">Change</span>
                            <span class="text-yellow-400 font-bold">${money(sale.change_amount)}</span>
                        </div>
                    ` : ''}
                </div>

                <div class="flex gap-3">
                    <button onclick="hideModal()" class="flex-1 py-2.5 bg-slate-600 hover:bg-slate-500 text-white rounded-xl transition text-sm">Close</button>
                    <button onclick="Pages.pos.printReceipt(${sale.id})" class="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition text-sm">Print Receipt</button>
                </div>
            </div>
        `);

        // Reset cart & reload products
        this.cart = [];
        const products = await API.get('/api/products?active=1');
        this.products = products || [];
        this.renderCart();
        this.renderProducts(this.products);
    },

    printReceipt(saleId) {
        // Simple receipt printing
        const content = document.getElementById('modal-content').innerHTML;
        const w = window.open('', '_blank', 'width=300,height=600');
        w.document.write(`
            <html><head><title>Receipt</title>
            <style>body{font-family:monospace;padding:20px;max-width:280px;margin:0 auto}
            .line{border-top:1px dashed #000;margin:8px 0}</style></head>
            <body>${content}</body></html>
        `);
        w.print();
    },
};
