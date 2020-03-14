.PHONY: setup

setup:
	test -f config/files/channels.json || cp config/files/example/channels_example.json config/files/channels.json
	test -f config/files/whitelist.json || cp config/files/example/whitelist_example.json config/files/whitelist.json
	test -f config/files/message.txt || cp config/files/example/message_example.txt config/files/message.txt
	test -f .env || cp .env.example .env
