import pycdlib

iso = pycdlib.PyCdlib()
iso.open("D:\\jmkdrvbak\\Storage\\PaRappa the Rapper 2\\PTR2EDIT.iso")

for child in iso.list_children(iso_path='/'):
    print(child.file_identifier())

iso.add_file("")