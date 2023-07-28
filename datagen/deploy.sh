chmod +x ~/datagencdk/menu-welcome-message.sh
chmod +x ~/datagencdk/menu-script.sh

cd /Users/soniyag/datagencdk/
python3 -m venv .env
source .env/bin/activate

~/datagencdk/menu-welcome-message.sh
~/datagencdk/menu-script.sh

