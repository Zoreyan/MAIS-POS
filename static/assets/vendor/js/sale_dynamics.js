function updateTotal() {
    totalSum = productList.reduce((sum, product) => sum + product.price * product.quantity, 0);
    $('.amount').text(totalSum.toFixed(2));
    applyDiscount();
    updateDisplay();
}

function applyDiscount() {
    const discount = parseFloat(discountInput.val()) || 0;
    discountedSum = Math.max(totalSum - discount, 0);
}

function updateDisplay() {
    $('#total-sum').text(discountedSum.toFixed(2));
    updateChange();
}

function updateChange() {
    let amount = parseFloat(amountInput.val()) || 0;
    $('.change').text((amount - discountedSum).toFixed(2));
}

function updateTable() {
    $('#product-table-body').empty();
    for (let product of productList) {
        $('#product-table-body').append(`
            <tr>
                <td>${product.name.slice(0, 22)}</td>
                <td>${product.bar_code}</td>
                <td class="product-quantity d-flex align-items-center gap-2">
                    ${product.quantity}/${product.stock}
                    <div class="d-flex flex-column">
                        <span class="text-muted increment" data-id="${product.id}">
                            <i class='bx bx-chevron-up'></i>
                        </span>
                        <span class="text-muted decrement" data-id="${product.id}">
                            <i class='bx bx-chevron-down'></i>
                        </span>
                    </div>
                </td>
                <td>${product.price}</td>
                <td><button class="btn btn-sm btn-danger delete-product" data-id="${product.id}">Удалить</button></td>
            </tr>
        `);
    }
    updateTotal();
}

const POS = {
    init: function () {
        this.cacheElements();
        this.bindEvents();
        this.getProducts();
    },

    cacheElements: function () {
        this.$barcodeInput = $('.barcode');
        this.$amountInput = $('.amount');
        this.$discountInput = $('.discount');
        this.$searchField = $('.search');
        this.$sellButton = $('.sell');
        this.$sellButtonOnline = $('#sell-online');
        this.$searchResults = $('#search-results');
        this.$productSearchResults = $('#product-search-results');
        this.$productTableBody = $('#product-table-body');
        this.productList = [];
        this.totalSum = 0;
        this.discountedSum = 0;
    },

    bindEvents: function () {
        $(document).on('keydown', this.handleKeydown.bind(this));
        this.$searchField.on('input', this.handleSearchInput.bind(this));
        $(document).on('click', '.add-product', this.handleAddProduct.bind(this));
        this.$barcodeInput.on('keypress', this.handleBarcodeInput.bind(this));
        $(document).on('click', '.increment', this.handleIncrement.bind(this));
        $(document).on('click', '.decrement', this.handleDecrement.bind(this));
        $(document).on('click', '.delete-product', this.handleDeleteProduct.bind(this));
        this.$amountInput.on('input', this.updateData.bind(this));
        this.$discountInput.on('input', this.updateData.bind(this));
        $('.sell').on('click', this.handleSell.bind(this));
    },

    handleKeydown: function (event) {
        if (document.activeElement.tagName === "INPUT") return;

        switch (event.key.toLowerCase()) {
            case 'q':
            case 'й':
                this.$barcodeInput.focus();
                break;
            case 'w':
            case 'ц':
                $('#search_btn').click();
                break;
            case 'a':
            case 'ф':
                this.$amountInput.focus();
                break;
            case 's':
            case 'ы':
                this.$discountInput.focus();
                break;
            case 'x':
            case 'ч':
                this.$sellButton.click();
                break;
        }
    },

    handleSearchInput: function () {
        const searchQuery = this.$searchField.val().trim();

        if (searchQuery.length >= 2) {
            this.searchProducts(searchQuery);
        } else {
            this.getNoBarcodeProducts();
            this.$productSearchResults.hide();
        }
    },

    searchProducts: function (query) {
        $.ajax({
            url: `{% url 'search-product' %}?query=${encodeURIComponent(query)}`,
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: (response) => this.displaySearchResults(response),
            error: (xhr, status, error) => this.handleSearchError(error)
        });
    },

    displaySearchResults: function (response) {
        this.$searchResults.empty();
        this.$productSearchResults.show();

        if (response.products && response.products.length > 0) {
            response.products.forEach(product => {
                this.$searchResults.append(`
                    <tr>
                        <td>${product.name.slice(0, 20)}</td>
                        <td>${product.bar_code || 'Без штрих-кода'}</td>
                        <td>${product.sale_price}</td>
                        <td>${product.quantity}</td>
                        <td><button class="add-product btn btn-primary btn-sm" data-id="${product.id}">+</button></td>
                    </tr>
                `);
            });
        } else {
            this.$searchResults.html('<div class="text-center">Товары не найдены.</div>');
        }
    },

    handleSearchError: function (error) {
        console.error('Ошибка поиска:', error);
        this.$searchResults.html('<div class="text-center">Ошибка поиска товара.</div>');
    },

    handleAddProduct: function (event) {
        const productId = $(event.target).data('id');
        this.fetchProduct(productId, this.addProductToList.bind(this));
    },

    fetchProduct: function (id, callback) {
        $.ajax({
            url: "{% url 'get-product' %}",
            type: "GET",
            data: { product_id: id },
            success: callback,
            error: (e) => this.showNoAccessMessage('Товар не найден!', '#ffa500')
        });
    },

    addProductToList: function (data) {
        if (data.quantity <= 0) {
            this.showNoAccessMessage('Недостаточно товара на складе!', '#dc3545');
            return;
        }

        const existingProduct = this.productList.find(product => product.bar_code === data.bar_code);
        const productName = data.name.length > 20 ? data.name.substring(0, 17) + '...' : data.name;

        if (existingProduct) {
            if (existingProduct.quantity < data.quantity) {
                existingProduct.quantity++;
                this.showNoAccessMessage(`+1 ${productName}!`, '#0b863f');
            } else {
                this.showNoAccessMessage('Недостаточно товара на складе!', '#dc3545');
            }
        } else {
            this.productList.unshift({
                id: data.id,
                name: data.name,
                bar_code: data.bar_code,
                quantity: 1,
                price: data.d_sale_price,
                stock: data.quantity,
                image: data.image
            });
            this.showNoAccessMessage(`Товар ${productName} добавлен!`, '#0b863f');
        }

        this.updateData();
    },

    handleBarcodeInput: function (event) {
        if (event.which === 13) {
            const barcode = this.$barcodeInput.val();
            this.fetchProductByBarcode(barcode, this.addProductToList.bind(this));
            this.$barcodeInput.val('');
        }
    },

    fetchProductByBarcode: function (barcode, callback) {
        $.ajax({
            url: "{% url 'get-product' %}",
            type: "GET",
            data: { bar_code: barcode },
            success: callback,
            error: () => this.showNoAccessMessage('Товар не найден!', '#ffa500')
        });
    },

    handleIncrement: function (event) {
        const productId = $(event.target).data('id');
        const product = this.productList.find(product => product.id == productId);

        if (product && product.quantity < product.stock) {
            product.quantity++;
            this.updateData();
        } else {
            this.showNoAccessMessage('Недостаточно товара на складе!', '#dc3545');
        }
    },

    handleDecrement: function (event) {
        const productId = $(event.target).data('id');
        const product = this.productList.find(product => product.id == productId);

        if (product && product.quantity > 1) {
            product.quantity--;
            this.updateData();
        }
    },

    handleDeleteProduct: function (event) {
        const productId = $(event.target).data('id');
        this.productList = this.productList.filter(product => product.id !== productId);
        $(event.target).closest('tr').fadeOut(300, () => this.updateData());
    },

    updateData: function () {
        this.calculateTotalSum();
        this.applyDiscount();
        this.updateDisplay();
        this.updateTable();
    },

    calculateTotalSum: function () {
        this.totalSum = this.productList.reduce((sum, product) => sum + product.price * product.quantity, 0);
    },

    applyDiscount: function () {
        const discount = parseFloat(this.$discountInput.val()) || 0;
        this.discountedSum = Math.max(this.totalSum - discount, 0);
    },

    updateDisplay: function () {
        this.$amountInput.text(this.totalSum.toFixed(2));
        this.updateChange();
        $('.total-sum').text(this.discountedSum.toFixed(2));
    },

    updateChange: function () {
        const amount = parseFloat(this.$amountInput.val()) || 0;
        $('.change').text((amount - this.discountedSum).toFixed(2));
    },

    updateTable: function () {
        this.$productTableBody.empty();
        this.productList.forEach(product => {
            this.$productTableBody.append(`
                <tr>
                    <td>${product.name.slice(0, 22)}</td>
                    <td>${product.bar_code}</td>
                    <td class="">
                        <input type="number" class="form-control form-control-sm product-quantity" value="${product.quantity}" min="1" max="${product.stock}" data-id="${product.id}"/>
                    </td>
                    <td>${product.price}</td>
                    <td><button class="text-danger fs-4 btn delete-product" data-id="${product.id}">
                        <i class='bx bx-x-circle'></i>
                        </button></td>
                </tr>
            `);
        });
    },

    handleSell: function () {
        if (this.$amountInput.val() < this.discountedSum) {
            this.showNoAccessMessage('Недостаточно средств!', '#ffa500');
            return false;
        }

        if (this.productList.length === 0) {
            this.showNoAccessMessage('Введите хотя бы один товар!', '#ffa500');
            return false;
        }

        const paymentMethod = this.determinePaymentMethod();
        const products = this.productList.map(product => ({
            id: product.id,
            quantity: product.quantity
        }));

        this.createSellHistory(paymentMethod, products);
    },

    determinePaymentMethod: function () {
        if (this.$amountInput.length > 0) {
            return 'cash';
        } else if ($('#online-card').length > 0 && this.$amountInput.length > 0) {
            return 'split';
        } else {
            return 'online';
        }
    },

    createSellHistory: function (paymentMethod, products) {
        $.ajax({
            url: "{% url 'create-sell-history' %}",
            type: "POST",
            data: {
                products: JSON.stringify(products),
                csrfmiddlewaretoken: '{{ csrf_token }}',
                amount: this.$amountInput.val(),
                change: this.$amountInput.val() - this.discountedSum,
                discount: this.$discountInput.val(),
                payment_method: paymentMethod,
            },
            success: () => {
                this.showNoAccessMessage('Продажа успешна!', '#0b863f');
                this.resetPOS();
            },
            error: (xhr, status, error) => console.log(error)
        });
    },

    resetPOS: function () {
        this.$productTableBody.empty();
        this.productList = [];
        this.totalSum = 0;
        this.discountedSum = 0;
        this.$amountInput.val('');
        this.$discountInput.val('');
        this.updateData();
    },

    showNoAccessMessage: function (message, color) {
        // Реализация показа сообщения
    },

    getProducts: function () {
        $.ajax(`{% url 'search-product' %}?filter=true`, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            success: (response) => this.displaySearchResults(response),
            error: (xhr, status, error) => this.handleSearchError(error)
        });
    },

    getNoBarcodeProducts: function () {
        // Реализация получения товаров без штрих-кода
    }
};

POS.init();