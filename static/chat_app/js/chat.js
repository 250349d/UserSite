let messageContainer;
let messageInput;

window.onload = function () {
	messageContainer = document.getElementById('messageContainer');
	messageInput = document.getElementById('messageInput');

	// サーバーからのイベントを受け取る
	const evtSource = new EventSource(eventStreamUrl);
	evtSource.onmessage = function (event) {
		const data = JSON.parse(event.data);

		const senderGroup = data.sender_group;
		const sendTime = data.send_time;
		const text = data.text;
		const readFlag = data.read_flag;
		const index = data.index;

		const type = data.type;
		if (type === 'create') {
			// メッセージ要素を作成
			const messageElement = document.createElement('div');
			messageElement.id = 'message' + index;
			messageElement.classList.add('message');

			// 送信者属性とログインユーザー属性によってクラスを変更
			if (senderGroup == userRole) {
				messageElement.classList.add('right-message');
			} else {
				messageElement.classList.add('left-message');
			}

			// 送信時間情報を取得
			const sendDate = new Date(sendTime);
			const dateString = sendDate.toLocaleDateString([], { month: '2-digit', day: '2-digit' });
			const timeString = sendDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

			// メッセージの日付が変わった場合は日付要素を作成
			const dateDividerElement = document.createElement('div');
			dateDividerElement.classList.add('date-divider');
			dateDividerElement.textContent = dateString;

			if (messageContainer.lastChild) {
				// 直前の日付を取得
				const lastMessageElement = messageContainer.lastChild;
				const lastSendTimeElement = lastMessageElement.querySelector('.send-time-container');
				const lastDateString = lastSendTimeElement.querySelector('.message-date').textContent;

				if (lastDateString !== dateString) {
					// 日付が変わった場合は日付要素を追加
					messageContainer.appendChild(dateDividerElement);
				}
			} else {
				// 最初のメッセージの場合は日付要素を追加
				messageContainer.appendChild(dateDividerElement);
			}

			// 送信時間要素を作成
			const sendTimeElement = document.createElement('div');
			sendTimeElement.classList.add('send-time-container');

			const dateElement = document.createElement('span');
			dateElement.hidden = true;
			dateElement.classList.add('message-date');
			dateElement.textContent = dateString;
			sendTimeElement.appendChild(dateElement);

			const timeElement = document.createElement('span');
			timeElement.classList.add('message-time');
			timeElement.textContent = timeString;
			sendTimeElement.appendChild(timeElement);

			messageElement.appendChild(sendTimeElement);

			// テキスト要素を作成
			const textElement = document.createElement('span');
			textElement.classList.add('message-text');
			textElement.textContent = text;
			messageElement.appendChild(textElement);

			// readFlagが存在する場合は既読フラグ要素を作成
			if (readFlag !== undefined) {
				const readFlagElement = document.createElement('span');
				readFlagElement.classList.add('message-read-flag');
				readFlagElement.textContent = readFlag ? '既読' : '未読';
				messageElement.appendChild(readFlagElement);
			}

			// メッセージコンテナにメッセージ要素を追加
			messageContainer.appendChild(messageElement);
			// メッセージコンテナを一番下までスクロール
			messageContainer.scrollTop = messageContainer.scrollHeight;

			// メッセージ受信処理
			receiveMessage(index);
		} else if (type === 'update') {
			// メッセージ要素を取得
			const messageElement = document.getElementById('message' + index);

			// テキスト要素を更新
			const textElement = messageElement.getElementsByClassName('message-text')[0];
			textElement.textContent = text;

			// readFlagが存在する場合は既読フラグ要素を更新
			if (readFlag !== undefined) {
				const readFlagElement = messageElement.getElementsByClassName('message-read-flag')[0];
				readFlagElement.textContent = readFlag ? '既読' : '未読';
			}
		} else if (type === 'delete') {
			// メッセージコンテナをクリア
			messageContainer.innerHTML = '';
		}
	}
}

// メッセージ受信処理
function receiveMessage(messageIndex) {
	const csrftoken = Cookies.get('csrftoken');

	// メッセージ受信処理
	fetch(updateMessageUrl, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrftoken,
		},
		mode: 'same-origin',
		body: JSON.stringify({
			task_id: taskId,
			message_index: messageIndex
		}),
	})
	.then(response => {
		if (!response.ok) {
			throw new Error("Network response was not ok");
		}
		return response.json();
	})
	.then(data => {
		if (!data.success) {
			alert('メッセージの受信処理に失敗しました');
		}
	})
	.catch(error => {
		console.error("There was a problem with the fetch operation:", error);
	});
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
		body: JSON.stringify({
			task_id: taskId,
			message: message
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
			messageInput.value = ''; // メッセージ入力欄をクリア
		} else {
			alert('メッセージの送信に失敗しました');
		}
	})
	.catch(error => {
		console.error("There was a problem with the fetch operation:", error);
	});
}
