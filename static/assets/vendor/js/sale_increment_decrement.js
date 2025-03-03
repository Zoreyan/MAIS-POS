

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
