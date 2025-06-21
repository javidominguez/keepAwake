#!/usr/bin/python
#-coding: UTF-8 -*-

import tones
import addonHandler
import globalPluginHandler
import globalVars
import gui
import wx
import speech
import ctypes

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
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		self.powerMenu = wx.Menu()
		keepAwakeItem = self.powerMenu.Append(wx.ID_ANY, KEEP_AWAKE)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onMenuItemAwake, keepAwakeItem)
		allowSleepItem = self.powerMenu.Append(wx.ID_ANY, ALLOW_SLEEP)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onMenuItemSleep, allowSleepItem)
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
		wx.MessageBox(_("The computer will remain awake while NVDA is running or until the power option is changed."), KEEP_AWAKE)

	def onMenuItemSleep(self, event):
		self.allowSleep()
		wx.MessageBox(_("Power-saving settings have been restored, and the computer can now sleep."), ALLOW_SLEEP)
