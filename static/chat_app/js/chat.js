let messageContainer;
let messageInput;

window.onload = function () {
	messageContainer = document.getElementById('messageContainer');
	messageInput = document.getElementById('messageInput');

	// サーバーからのイベントを受け取る
	const evtSource = new EventSource(eventStreamUrl);
	evtSource.onmessage = function (event) {
		const data = JSON.parse(event.data);

		const sender_group = data.sender_group;
		const send_time = data.send_time;
		const text = data.text;
		const read_flag = data.read_flag;

		// メッセージ要素を作成
		const messageElement = document.createElement('div');
		messageElement.classList.add('message');
		// TODO: 送信者グループによってクラスを変更
		switch (sender_group) {
			case '0':
				messageElement.classList.add('client-message');
				break;
			case '1':
				messageElement.classList.add('worker-message');
				break;
		}

		// 送信時間要素を作成
		const send_date = new Date(send_time);
		const dateString = send_date.toLocaleDateString([], { month: '2-digit', day: '2-digit' });
		const timeString = send_date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

		const timeElement = document.createElement('span');
		timeElement.classList.add('message-time');
		timeElement.textContent = dateString + ' ' + timeString;
		messageElement.appendChild(timeElement);

		// テキスト要素を作成
		const textElement = document.createElement('span');
		textElement.classList.add('message-text');
		textElement.textContent = text;
		messageElement.appendChild(textElement);

		// read_flagが存在する場合は既読フラグ要素を作成
		if (read_flag !== undefined) {
			const readFlagElement = document.createElement('span');
			readFlagElement.classList.add('message-read-flag');
			readFlagElement.textContent = read_flag ? '既読' : '未読';
			messageElement.appendChild(readFlagElement);
		}

		// メッセージコンテナにメッセージ要素を追加
		messageContainer.appendChild(messageElement);
	}
}

// メッセージを送信する
function sendMessage() {
	const message = document.getElementsByName('message')[0].value;
	if (!message) {
		return; // メッセージが空の場合は送信しない
	}

	const csrftoken = Cookies.get('csrftoken');

	// メッセージ送信処理
	fetch(sendMessageUrl, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrftoken,
		},
		mode: 'same-origin',
		body: JSON.stringify({ message: message }),
	})
	.then(response => {
		if (!response.ok) {
			throw new Error("Network response was not ok");
		}
		return response.json();
	})
	.then(data => {
		if (data.success) {
			messageInput.value = ''; // メッセージ入力欄をクリア
		} else {
			throw new Error("Failed to send message");
		}
	})
	.catch(error => {
		console.error("There was a problem with the fetch operation:", error);
	});
}
