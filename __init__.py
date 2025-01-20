def classFactory(iface):
    from .plugin_main import CsvViewerPlugin
    return CsvViewerPlugin(iface)
