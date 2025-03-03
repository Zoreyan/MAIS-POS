
$(searchField).on('input', function () {
    console.log("Input value:", paymentMethod);
    let searchQuery = this.value.trim();
    
    if (searchQuery.length >= 2) {
        $.ajax(`{% url 'search-product' %}?query=${encodeURIComponent(searchQuery ? searchQuery : null)}`, {
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

    } else {
        getNoBarcodeProducts();
        document.querySelector('.product-search-results').style.display = 'none';
    }
});
