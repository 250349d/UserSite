window.onload = function() {
	addOrderField();
}

let orderRowCount = 0;
function addOrderField() {
	const productFields = document.getElementById('order-fields');
	const newRow = document.createElement('tr');
	newRow.id = `order-row-${orderRowCount++}`;
	newRow.innerHTML = `
		<td><input type="text" name="product_name" required></td>
		<td><input type="number" id="price" name="price" min="0" required></td>
		<td><input type="number" id="quantity" name="quantity" min="1" required></td>
		<td><input type="number" id="subtotal-price" min="0" value="0" readonly></td>
		<td><input type="text" name="notes" required></td>
	`;

	const priceInput = newRow.querySelector('#price');
	priceInput.addEventListener('change', () => {
		calculateSubTotalPrice(newRow.id);
	});

	const quantityInput = newRow.querySelector('#quantity');
	quantityInput.addEventListener('change', () => {
		calculateSubTotalPrice(newRow.id);
	});

	productFields.appendChild(newRow);
}

function calculateSubTotalPrice(orderRowId) {
	const row = document.getElementById(orderRowId);
	const priceCell = row.querySelector('#price');
	const quantityCell = row.querySelector('#quantity');
	const subtotalPriceCell = row.querySelector('#subtotal-price');

	const price = parseInt(priceCell.value) || 0;
	const quantity = parseInt(quantityCell.value) || 0;
	const subtotalPrice = price * quantity;
	subtotalPriceCell.value = subtotalPrice;

	calculateTotalPrice();
}

function calculateTotalPrice() {
	const subtotalPriceCells = document.querySelectorAll('#subtotal-price');

	let totalPrice = 0;
	subtotalPriceCells.forEach(cell => {
		totalPrice += parseInt(cell.value) || 0;
	});

	const totalPriceElement = document.getElementById('total-price');
	totalPriceElement.value = totalPrice;
}

function submitOrder() {
	if (!confirm("注文を確定します\nよろしいですか？")) {
		return;
	}

	// 依頼情報
	const title = document.getElementsByName('title')[0].value;
	const limitOfTime = document.getElementsByName('limit_of_time')[0].value;
	const shopName = document.getElementsByName('shop_name')[0].value;
	const shopPostCode = document.getElementsByName('shop_post_code')[0].value;
	const shopAddress = document.getElementsByName('shop_address')[0].value;
	const shopStreetAddress = document.getElementsByName('shop_street_address')[0].value;

	// 注文情報
	const productNameList = Array.from(document.getElementsByName('product_name')).map(input => input.value);
	const priceList = Array.from(document.getElementsByName('price')).map(input => input.value);
	const quantityList = Array.from(document.getElementsByName('quantity')).map(input => input.value);
	const notesList = Array.from(document.getElementsByName('notes')).map(input => input.value);

	const csrftoken = Cookies.get('csrftoken');

	fetch(submitOrderUrl, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrftoken,
		},
		mode: 'same-origin',
		body: JSON.stringify({
			title: title,
			limit_of_time: limitOfTime,
			shop_name: shopName,
			shop_post_code: shopPostCode,
			shop_address: shopAddress,
			shop_street_address: shopStreetAddress,
			product_name_list: productNameList,
			price_list: priceList,
			quantity_list: quantityList,
			notes_list: notesList,
		}),
	})
	.then(response => {
		if (!response.ok) {
			throw new Error("Network response was not ok");
		}
		return response.json();
	})
	.then(data => {
		if (data.success) {
			alert("注文が完了しました")
			window.location.href = checkOrderUrl;
		} else {
			alert(data.error_message);
		}
	})
	.catch(error => {
		console.error("There was a problem with the fetch operation:", error);
	});
}