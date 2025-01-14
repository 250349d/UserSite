function payment(taskId) {
	if (!confirm("請求金額:" + totalCost + "円" + "\n" + "本当に支払いますか？")) {
		return;
	}

	const name = document.getElementsByName('name')[0].value;
	const cardNumber = document.getElementsByName('card_number')[0].value;
	const cvc = document.getElementsByName('cvc')[0].value;
	const expiryDate = document.getElementsByName('expiry_date')[0].value;

	const csrftoken = Cookies.get('csrftoken');
	const url = `${paymentUrl}${taskId}/`;

	fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrftoken,
		},
		mode: 'same-origin',
		body: JSON.stringify({
			task_id: taskId,
			name: name,
			card_number: cardNumber,
			cvc: cvc,
			expiry_date: expiryDate,
		}),
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		if (data.success) {
			alert("お支払いが完了しました");
			window.location.href = checkPaymentUrl;
		} else {
			alert(data.error_message);
		}
	})
	.catch(error => {
		console.error("Error:", error);
	});
}