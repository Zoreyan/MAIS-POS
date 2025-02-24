$(document).ready(function () {

    let barcodeInput = $('.barcode');
    let amountInput = $('.amount');
    let discountInput = $('.discount');
    let productList = [];
    let totalSum = 0;
    let searchField = $('.search');
    let discountedSum = 0;

    $(searchField).on('input', function () {
        let searchQuery = this.value.trim();
        if (searchQuery.length >= 2) {
            $.ajax(`{% url 'search-product' %}?query=${encodeURIComponent(searchQuery)}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                success: function (response) {
                    const searchResultsContainer = document.getElementById('search-results');
                    searchResultsContainer.innerHTML = ''; // Очищаем предыдущие результаты
                    document.querySelector('.product-search-results').style.display = 'block';

                    if (response.products && response.products.length > 0) {
                        response.products.forEach(product => {
                            searchResultsContainer.insertAdjacentHTML('beforeend', `
                            <tr>
                      <td>${product.name.slice(0, 20)}</td>
                      <td>${product.bar_code}</td>
                      
                      <td>${product.sale_price}</td>
                      <td>
                        ${product.quantity}
                      </td>
                      <td>
                        <button class="add-product btn btn-primary btn-sm" data-id="${product.id}">+</button>
                      </td>
                    </tr>
                            `);
                        });
                    } else {
                        searchResultsContainer.innerHTML = '<div class="text-center">Товары не найдены.</div>';
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Ошибка поиска:', error);
                    $('#search-results').innerHTML = '<div class="text-center">Ошибка поиска товара.</div>';
                }
            })

        } else {
            document.querySelector('.product-search-results').style.display = 'none';
        }
    });


    // Обработчик события для ввода штрих-кода
    barcodeInput.on('keypress', function (e) {
        if (e.which === 13) {
        let barcode = $(this).val();
            $.ajax({
                url: "{% url 'get-product' %}",
                type: "GET",
                data: { bar_code: barcode },
                success: function (data) {
                    if (data.quantity <= 0) {
                        showNoAccessMessage('Недостаточно товара на складе!', '#dc3545');
                        return;
                    }

                    // Добавляем продукт в список, если его нет, или увеличиваем количество, если он уже есть
                    let existingProduct = productList.find(product => product.bar_code === data.bar_code);
                    let productName = data.name.length > 20 ? data.name.substring(0, 17) + '...' : data.name;

                    if (existingProduct) {
                        if (existingProduct.quantity < data.quantity) {
                            existingProduct.quantity++;
                            showNoAccessMessage(`+1 ${productName}!`, '#0b863f');
                        } else {
                            showNoAccessMessage('Недостаточно товара на складе!', '#dc3545');
                        }
                    } else {
                        productList.unshift({
                            id: data.id,
                            name: data.name,
                            bar_code: data.bar_code,
                            quantity: 1,
                            price: data.d_sale_price,
                            stock: data.quantity,
                            image: data.image
                        });
                        showNoAccessMessage(`Товар ${productName} добавлен!`, '#0b863f');
                    }

                    updateTable();
                },
                error: function () {
                    showNoAccessMessage('Товар не найден!', '#ffa500');
                }
            });
            $(this).val(''); // очищаем поле штрих-кода после поиска
        }
    });

    // Обработчик клика по кнопке "Добавить продукт"
    $(document).on('click', '.add-product', function () {
        let productId = $(this).data('id'); // Получаем id продукта

        // Отправляем GET-запрос на сервер с id продукта
        $.ajax({
            url: "{% url 'get-product' %}",
            type: "GET",
            data: { id: productId },
            success: function (data) {
                if (data.quantity <= 0) {
                    showNoAccessMessage('Недостаточно товара на складе!', '#dc3545');
                    return;
                }

                // Добавляем продукт в список
                let existingProduct = productList.find(product => product.bar_code === data.bar_code);
                let productName = data.name.length > 20 ? data.name.substring(0, 17) + '...' : data.name;

                if (existingProduct) {
                    if (existingProduct.quantity < data.quantity) {
                        existingProduct.quantity++;
                        showNoAccessMessage(`+1 ${productName}!`, '#0b863f');
                    } else {
                        showNoAccessMessage('Недостаточно товара на складе!', '#dc3545');
                    }
                } else {
                    productList.push({
                        id: data.id,
                        name: data.name,
                        bar_code: data.bar_code,
                        quantity: 1,
                        price: data.d_sale_price,
                        stock: data.quantity,
                        image: data.image
                    });
                    showNoAccessMessage(`Товар ${productName} добавлен!`, '#0b863f');
                }

                updateTable();
            },
            error: function () {
                showNoAccessMessage('Товар не найден!', '#ffa500');
            }
        });
    });

    

    $(document).on('click', '.increment', function () {
        let productId = $(this).data('id');
        const product = productList.find(product => product.id == productId);

        $('.product-info').empty();

        if (product && product.quantity < product.stock) {
            product.quantity++;
            updateTable();
        } else {
            showNoAccessMessage('Недостаточно товара на складе!', '#dc3545');
        }
    });

    $(document).on('click', '.decrement', function () {
        let productId = $(this).data('id');
        const product = productList.find(product => product.id == productId);
        if (product && product.quantity > 1) {
            product.quantity--;
            updateTable();
        }
    });

    function updateTotal() {
        totalSum = productList.reduce((sum, product) => sum + product.price * product.quantity, 0);
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

    amountInput.on('input', updateChange);
    discountInput.on('input', updateTotal);

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

    $(document).on('click', '.delete-product', function () {
        let productId = $(this).data('id');
        productList = productList.filter(product => product.id !== productId);

        let product = productList.find(product => product.id == productId);

        $(this).closest('tr').fadeOut(300, function () {
            $(this).remove();
            totalSum -= product.price * product.quantity;
            
        });
        updateTotal();
        updateChange();
    });

    $('.sell').on('click', function () {
        if (amountInput.val() < discountedSum) {
            showNoAccessMessage('Недостаточно средств!', '#ffa500');
            return false;
        }
        if (productList.length === 0) {
            showNoAccessMessage('Введите хотя бы один товар!', '#ffa500');
            return false;
        }

        let products = productList.map(product => ({
            id: product.id,
            quantity: product.quantity
        }));

        $.ajax({
            url: "{% url 'create-sell-history' %}",
            type: "POST",
            data: {
                products: JSON.stringify(products),
                csrfmiddlewaretoken: '{{ csrf_token }}',
                amount: amountInput.val(),
                change: amountInput.val() - discountedSum,
                discount: discountInput.val()
            },
            success: function () {
                showNoAccessMessage('Продажа успешна!', '#0b863f');
                productList = [];
                $('#product-table-body').empty();
                updateTotal();
                updateChange();
                
            },
            error: function (xhr, status, error) {
                console.log(error);
            }
        });
    });
});
