#!/usr/bin/python
#-coding: UTF-8 -*-

"""
Addon for NVDA that Provides a tool to enable or disable energy saving and keep the computer awake.

This file is covered by the GNU General Public License.
See the file COPYING.txt for more details.
Copyright  (c) 2025 Javi Dominguez <fjavids@gmail.com>
 """
import tones
import addonHandler
import globalPluginHandler
import globalVars
import gui
import wx
import speech
import ctypes
from threading import Thread, enumerate
from time import sleep

addonHandler.initTranslation()

# Translators: Labels of the Menu in Tools to toggle the keep Awake mode.
POWER_OPTIONS = _("Po&wer options...")
KEEP_AWAKE = _("Keep computer awake")
ALLOW_SLEEP = _("Allow Computer to Sleep")

# Constants of the Windows API
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	speechOnDemand = {"speakOnDemand": True} if hasattr(speech.SpeechMode, "onDemand") else {}

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)

		# The Windows API does not expose a method to query the current state of this setting.
		# A flag is used for tracking purposes. The variable is stored in globalVars to preserve synchronization across addon reloads.
		if not hasattr(globalVars, "keepAwake"):
			globalVars.keepAwake = False

		# If it doesn't exist, instantiate and start a thread to ensure persistence of the always-awake mode.
		if "KeepAwake" not in [th.name for th in enumerate()]:
			thKeepAwake(seconds=1800).start()

		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		self.powerMenu = wx.Menu()
		self.keepAwakeItem = self.powerMenu.Append(wx.ID_ANY, KEEP_AWAKE, kind=wx.ITEM_RADIO)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onMenuItemAwake, self.keepAwakeItem)
		self.allowSleepItem = self.powerMenu.Append(wx.ID_ANY, ALLOW_SLEEP, kind=wx.ITEM_RADIO)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onMenuItemSleep, self.allowSleepItem)
		if globalVars.keepAwake:
			self.keepAwakeItem.Check(True)
		else:
			self.allowSleepItem.Check(True)
		self.power_submenu = self.toolsMenu .AppendSubMenu(self.powerMenu, POWER_OPTIONS)

	def terminate(self):
		try:
			gui.mainFrame.sysTrayIcon.toolsMenu.Remove(self.power_submenu)
		except Exception:
			pass

	def keepAwake (self):
		# Combine flags to avoid screening and screen off
		ctypes.windll.kernel32.SetThreadExecutionState(
			ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
		)

	def allowSleep(self):
		# Restore system default behavior
		ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

	def onMenuItemAwake(self, event):
		self.keepAwake()
		globalVars.keepAwake = True
		wx.MessageBox(_("The computer will remain awake while NVDA is running or until the power option is changed."), KEEP_AWAKE)

	def onMenuItemSleep(self, event):
		self.allowSleep()
		globalVars.keepAwake = False
		wx.MessageBox(_("Power-saving settings have been restored, and the computer can now sleep."), ALLOW_SLEEP)

class thKeepAwake(Thread):
	def __init__(self, seconds=1800):
		super().__init__(daemon=True)
		self.seconds = seconds
		self.name = "KeepAwake"

	def run(self):
		while(True):
			sleep(self.seconds)
			try:
				if globalVars.keepAwake:
					ctypes.windll.kernel32.SetThreadExecutionState(
						ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
					)
			except AttributeError:
				break
