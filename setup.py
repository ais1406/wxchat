from setuptools import setup

setup(
	name="wxchat",
	version ="1.0",
	py_modules=["wxchat","chatnetworking","chatserverStub","rendezvous"],
	data_files = [
    	('images', ['images/conn.jpg', 'images/exit.jpg', 'images/info.jpg'])
	],
	app=['wxchat.py'],
	options = {'py2app': {'argv_emulation': True}},
	setup_requires = ['py2app'],
)
