import nuke
import open_recent

addToMenu = nuke.menu("Nuke").findItem("File/Open Recent Comp")
addToMenu.addCommand("Show in GUI mode", "open_recent.show_panel()", "alt+o")