$('.sale').on('click', function () {
    let paymentMethod = $('input[name="formValidationPlan"]:checked').val();

    if (amountInput.val() < discountedSum) {
        showNoAccessMessage('Недостаточно средств!', '#ffa500');
        return false;
    }
    if (productList.length === 0) {
        showNoAccessMessage('Введите хотя бы один товар!', '#ffa500');
        return false;
    }

    if (paymentMethod === undefined) {
        showNoAccessMessage('Выберите способ оплаты!', '#ffa500');
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
            discount: discountInput.val(),
            payment_method: paymentMethod,
        },
        success: function () {
            showNoAccessMessage('Продажа успешна!', '#0b863f');
            productList = [];
            $('#product-table-body').empty();
            productList = [];
            totalSum = 0;
            discountedSum = 0;
            updateTable();
            amountInput.val('');
            discountInput.val('');
            updateChange();
        },
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
});

