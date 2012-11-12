from distutils.core import setup
setup(
	name="wxchat",
	version ="1.0",
	py_modules=["wxchat","chatnetworking","chatserverStub","rendezvous"],
	data_files = [
    	('images', ['images/conn.jpg', 'images/exit.jpg', 'images/info.jpg'])
	]
)
