PLUGINNAME = lockzoom
PLUGINS = "$(HOME)"/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/$(PLUGINNAME)
PY_FILES = __init__.py lockZoom.py 
EXTRAS = metadata.txt

deploy:
	mkdir -p $(PLUGINS)
	cp -vf $(PY_FILES) $(PLUGINS)
	cp -vf $(EXTRAS) $(PLUGINS)
	cp -vfr images $(PLUGINS)
	cp -vfr doc $(PLUGINS)
	cp -vf helphead.html $(PLUGINS)/index.html
	python -m markdown -x extra readme.md >> $(PLUGINS)/index.html
	echo '</body>' >> $(PLUGINS)/index.html

