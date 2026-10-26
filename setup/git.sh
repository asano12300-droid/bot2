#!/bin/bash
user=$(whoami)

if [ ! -e /home/$user/.config ]; then
	echo -n "あなたのgithubのユーザ名: "
	read name

	echo -n "あなたのgithubアカウントのメールアドレス: "
	read email

	git config --global user.name $name
	git config --global user.name $email
else
	echo -n "githubのユーザー名: "
	read name
fi

echo -n "こちらは、作業フォルダですか,[Y/N]: "
read qa

if [[ "$qa" == "y" || "$qa" == "Y" ]]; then
	git init

	echo -n "どのレポジトリーを使用しますか?: "
	read repo

	git remote add origin https://github.com/$name/$repo.git
	echo -n "`git push`の際にパスワードを求められないようにする? [Y/N]: "
	read qb
	if [[ "$qb" == "y" || "$qa" == "Y" ]]; then
		echo -n "パスワード: "
		read password
		git remote set-url origin https://$password@github.com/$name/$repo.git
		git branch -M main
	elif [[ "$qb" == "n" || "$qb" == "N" ]]; then
		git branch -M main
	fi
elif [[ "$qa" == "n" || "$qa" == "N" ]]; then
	echo "作業フォルダに入ってから、再度お願いします。"
else
	echo "再度お願いします"
fi




