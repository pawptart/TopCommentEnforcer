CONFIG_FILE=config.ini
MESSAGE_FILE=removal_message.txt

if test -f "$CONFIG_FILE"; then
    echo "WARNING: $CONFIG_FILE already exists. This will DELETE your existing configuration."
    read -p "Are you sure you want to overwrite it? (y/n)" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) echo "Aborting..."; exit;;
        * ) echo "Unknown response. Aborting..."; exit;;
    esac
fi

echo 'Copying config.ini.example to config.ini!'
cp config.ini.example config.ini
echo 'Done!'

echo 'Copying removal_message.txt.example to removal_message.txt!'
if test -f "$MESSAGE_FILE"; then
    echo "$MESSAGE_FILE already exists! Skipping..."
else
    cp removal_message.txt.example removal_message.txt
fi

echo 'Done!'
