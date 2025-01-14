function cancelOrder(taskId) {
	if (!confirm("注文をキャンセルしますか？")) {
		return;
	}

	const csrftoken = Cookies.get('csrftoken');
	const url = `${cancelOrderUrl}${taskId}/`;

	fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrftoken,
		},
		mode: 'same-origin',
	})
	.then(response => {
		if (!response.ok) {
			throw new Error("Network response was not ok");
		}
		return response.json();
	})
	.then(data => {
		if (data.success) {
			alert("注文をキャンセルしました")
			location.reload();
		} else {
			alert("注文をキャンセルできませんでした\n" + data.error_message);
		}
	})
	.catch(error => {
		console.error("There was a problem with the fetch operation:", error);
	});
}

function confirmRequest(taskId) {
	const csrftoken = Cookies.get('csrftoken');
	const url = `${confirmRequestUrl}${taskId}/`;

	fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrftoken,
		},
		mode: 'same-origin',
	})
	.then(response => {
		if (!response.ok) {
			throw new Error("Network response was not ok");
		}
		return response.json();
	})
	.then(data => {
		if (data.success) {
			if (confirm("申請を承認しますか？\n" + data.request_price + "円")) {
				acceptRequest(data.request_id);
			} else {
				rejectRequest(data.request_id);
			}
		} else {
			alert(data.error_message);
		}
	})
	.catch(error => {
		console.error("There was a problem with the fetch operation:", error);
	});
}

function acceptRequest(requestId) {
	const csrftoken = Cookies.get('csrftoken');

	fetch(acceptRequestUrl, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrftoken,
		},
		mode: 'same-origin',
		body: JSON.stringify({
			'request_id': requestId,
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
			alert("承認しました")
		} else {
			alert(data.error_message);
		}
	})
	.catch(error => {
		console.error("There was a problem with the fetch operation:", error);
	});
}

function rejectRequest(requestId) {
	const csrftoken = Cookies.get('csrftoken');

	fetch(rejectRequestUrl, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrftoken,
		},
		mode: 'same-origin',
		body: JSON.stringify({
			'request_id': requestId,
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
			alert("非承認しました\n再申請をお待ちください")
		} else {
			alert(data.error_message);
		}
	})
	.catch(error => {
		console.error("There was a problem with the fetch operation:", error);
	});
}