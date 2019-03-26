USER_DATA=`base64 user_data_script.sh -b0`
sed -i '' "s|base64_encoded_bash_script|$USER_DATA|g" $1
