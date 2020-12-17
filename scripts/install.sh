FILE=config.ini

if test -f "$FILE"; then
    echo "WARNING: $FILE already exists. This will DELETE your existing configuration."
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