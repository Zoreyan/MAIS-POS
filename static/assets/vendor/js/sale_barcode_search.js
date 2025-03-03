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


function getNoBarcodeProducts() {
    $.ajax(`{% url 'search-product' %}?filter=true`, {
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
                  <td>${product.bar_code ? product.bar_code != 'null' : 'Без штрих-кода'}</td>
                  
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

}
