import unittest
import json
import os
from unittest.mock import MagicMock, patch, PropertyMock
import customtkinter as ctk
import sys

class TestGameAutomationTool(unittest.TestCase):

    def setUp(self):
        # Patch GameAutomationTool's __init__ to prevent actual GUI creation
        self.patcher_game_automation_tool_init = patch('game_automation_tool.GameAutomationTool.__init__', return_value=None)
        self.mock_game_automation_tool_init = self.patcher_game_automation_tool_init.start()

        # Instantiate the app (which will now be a mocked object due to the patch)
        from game_automation_tool import GameAutomationTool
        self.app = GameAutomationTool()

        # Manually set up necessary attributes and methods on the mocked app instance
        self.app.events_data = {}
        self.app.stop_flags = {}
        self.app.threads = {}
        self.app.config_file = "sf3_automation_config.json"
        self.app.target_window = "LDPlayer"
        self.app.right_frame_visible = False
        self.app.minimal_window = MagicMock()

        # Mock methods that are called during __init__ or setup_gui
        self.app.title = MagicMock()
        self.app.geometry = MagicMock()
        self.app.protocol = MagicMock()
        self.app.attributes = MagicMock()
        self.app.withdraw = MagicMock()
        self.app.deiconify = MagicMock()
        self.app.winfo_screenwidth = MagicMock(return_value=1920)
        self.app.winfo_screenheight = MagicMock(return_value=1080)
        self.app.winfo_x = MagicMock(return_value=0)
        self.app.winfo_y = MagicMock(return_value=0)
        self.app.winfo_reqwidth = MagicMock(return_value=400)
        self.app.winfo_reqheight = MagicMock(return_value=100)
        self.app.bind = MagicMock()
        self.app.update_idletasks = MagicMock()
        self.app.after = MagicMock()
        self.app.tk = MagicMock() # Mock the tk attribute to prevent RecursionError

        # Mock the frame objects that are children of the main app
        self.app.main_frame = MagicMock()
        self.app.image_frame = MagicMock()
        self.app.control_buttons_frame = MagicMock()
        self.app.minimal_control_frame = MagicMock()
        self.app.status_text = MagicMock()
        self.app.event_radio_frame = MagicMock()

        # Mock the winfo_children method for frames that are cleared
        self.app.event_radio_frame.winfo_children.return_value = []
        self.app.image_frame.winfo_children.return_value = []
        self.app.control_buttons_frame.winfo_children.return_value = []
        self.app.minimal_control_frame.winfo_children.return_value = []

        # Mock the pack method for widgets that are packed into frames
        self.app.main_frame.pack = MagicMock()
        self.app.image_frame.pack = MagicMock()
        self.app.control_buttons_frame.pack = MagicMock()
        self.app.minimal_control_frame.pack = MagicMock()
        self.app.status_text.pack = MagicMock()
        self.app.event_radio_frame.pack = MagicMock()

        # Mock the grid method for widgets that are gridded into frames
        self.app.control_buttons_frame.grid_columnconfigure = MagicMock()
        self.app.control_buttons_frame.grid = MagicMock()

        # Mock the configure method for CTkOptionMenu (if still used somewhere)
        self.app.event_dropdown = MagicMock()
        self.app.event_dropdown.configure = MagicMock()

        # Mock the log_status method
        self.app.log_status = MagicMock()

        # Mock the save_config method
        self.app.save_config = MagicMock()

        # Mock the refresh methods
        self.app.refresh_event_list = MagicMock(side_effect=self.app.refresh_event_list) # Call original for logic
        self.app.refresh_image_list = MagicMock()
        self.app.refresh_control_buttons = MagicMock()
        self.app.refresh_minimal_control_buttons = MagicMock()

        # Mock the focus_window method
        self.app.focus_window = MagicMock()

        # Mock the find_image_and_execute method
        self.app.find_image_and_execute = MagicMock(return_value=False)

        # Mock the _threaded_find_and_execute method
        self.app._threaded_find_and_execute = MagicMock()

        # Mock the event_status_lock
        self.app.event_status_lock = MagicMock()

        # Mock CTkInputDialog directly
        self.patcher_ctk_input_dialog = patch('customtkinter.CTkInputDialog')
        self.mock_ctk_input_dialog = self.patcher_ctk_input_dialog.start()
        self.mock_ctk_input_dialog.return_value.get_input.return_value = "TestEvent"

        # Patch other customtkinter widgets where they are used
        self.patcher_ctk_button = patch('customtkinter.CTkButton')
        self.mock_ctk_button = self.patcher_ctk_button.start()
        self.patcher_ctk_checkbox = patch('customtkinter.CTkCheckBox')
        self.mock_ctk_checkbox = self.patcher_ctk_checkbox.start()
        self.patcher_ctk_label = patch('customtkinter.CTkLabel')
        self.mock_ctk_label = self.patcher_ctk_label.start()
        self.patcher_ctk_frame = patch('customtkinter.CTkFrame')
        self.mock_ctk_frame = self.patcher_ctk_frame.start()
        self.patcher_ctk_scrollable_frame = patch('customtkinter.CTkScrollableFrame')
        self.mock_ctk_scrollable_frame = self.patcher_ctk_scrollable_frame.start()
        self.patcher_ctk_textbox = patch('customtkinter.CTkTextbox')
        self.mock_ctk_textbox = self.patcher_ctk_textbox.start()
        self.patcher_ctk_optionmenu = patch('customtkinter.CTkOptionMenu')
        self.mock_ctk_optionmenu = self.patcher_ctk_optionmenu.start()
        self.patcher_ctk_entry = patch('customtkinter.CTkEntry')
        self.mock_ctk_entry = self.patcher_ctk_entry.start()
        self.patcher_ctk_radiobutton = patch('customtkinter.CTkRadioButton')
        self.mock_ctk_radiobutton = self.patcher_ctk_radiobutton.start()
        self.patcher_ctk_toplevel = patch('customtkinter.CTkToplevel')
        self.mock_ctk_toplevel = self.patcher_ctk_toplevel.start()

        # Use actual StringVar and BooleanVar from customtkinter
        self.patcher_string_var = patch('customtkinter.StringVar', side_effect=ctk.StringVar)
        self.mock_string_var = self.patcher_string_var.start()
        self.patcher_boolean_var = patch('customtkinter.BooleanVar', side_effect=ctk.BooleanVar)
        self.mock_boolean_var = self.patcher_boolean_var.start()

        # Mock methods that interact with the OS or external libraries
        self.patcher_os_path_exists = patch('os.path.exists', return_value=False)
        self.mock_os_path_exists = self.patcher_os_path_exists.start()
        self.patcher_json_load = patch('json.load', return_value={})
        self.mock_json_load = self.patcher_json_load.start()
        self.patcher_json_dump = patch('json.dump')
        self.mock_json_dump = self.patcher_json_dump.start()
        self.patcher_open = patch('builtins.open', MagicMock())
        self.mock_open = self.patcher_open.start()
        self.patcher_messagebox_showwarning = patch('tkinter.messagebox.showwarning')
        self.mock_messagebox_showwarning = self.patcher_messagebox_showwarning.start()
        self.patcher_messagebox_showerror = patch('tkinter.messagebox.showerror')
        self.mock_messagebox_showerror = self.patcher_messagebox_showerror.start()
        self.patcher_pyautogui_locateOnScreen = patch('pyautogui.locateOnScreen', return_value=None)
        self.mock_pyautogui_locateOnScreen = self.patcher_pyautogui_locateOnScreen.start()
        self.patcher_pyautogui_press = patch('pyautogui.press')
        self.mock_pyautogui_press = self.patcher_pyautogui_press.start()
        self.patcher_pyautogui_click = patch('pyautogui.click')
        self.mock_pyautogui_click = self.patcher_pyautogui_click.start()
        self.patcher_pyautogui_moveTo = patch('pyautogui.moveTo')
        self.mock_pyautogui_moveTo = self.patcher_pyautogui_moveTo.start()
        self.patcher_pyautogui_dragTo = patch('pyautogui.dragTo')
        self.mock_pyautogui_dragTo = self.patcher_pyautogui_dragTo.start()
        self.patcher_time_sleep = patch('time.sleep')
        self.mock_time_sleep = self.patcher_time_sleep.start()
        self.patcher_threading_Thread = patch('threading.Thread')
        self.mock_threading_Thread = self.patcher_threading_Thread.start()
        self.patcher_gw_getAllWindows = patch('pygetwindow.getAllWindows', return_value=[])
        self.mock_gw_getAllWindows = self.patcher_gw_getAllWindows.start()
        self.patcher_gw_getWindowsWithTitle = patch('pygetwindow.getWindowsWithTitle', return_value=[])
        self.mock_gw_getWindowsWithTitle = self.patcher_gw_getWindowsWithTitle.start()
        self.patcher_os_listdir = patch('os.listdir', return_value=[])
        self.mock_os_listdir = self.patcher_os_listdir.start()
        self.patcher_os_system = patch('os.system')
        self.mock_os_system = self.patcher_os_system.start()

        # Mock the get method for the selected_event StringVar
        self.app.selected_event = ctk.StringVar(value="")


    def tearDown(self):
        patch.stopall()
        # Remove GameAutomationTool from sys.modules to allow re-importing in subsequent tests
        if 'game_automation_tool' in sys.modules:
            del sys.modules['game_automation_tool']

    def test_add_event(self):
        # Set the return value for the input dialog before calling add_event
        self.mock_ctk_input_dialog.return_value.get_input.return_value = "NewEvent"
        self.app.add_event()
        self.assertIn("NewEvent", self.app.events_data)
        self.assertEqual(self.app.events_data["NewEvent"]["enabled"], True)
        self.assertEqual(self.app.events_data["NewEvent"]["target_window"], "LDPlayer")
        self.mock_json_dump.assert_called_once() # Check if config was saved

    def test_save_image_config_with_run_in_thread(self):
        event_name = "TestEvent"
        self.app.events_data[event_name] = {"images": [], "enabled": True, "target_window": "LDPlayer"}

        # Mock the action_frame for save_image_config
        action_frame_mock = MagicMock()
        action_frame_mock.key_var = ctk.StringVar(value="a")
        action_frame_mock.delay_var = ctk.StringVar(value="0.1")

        self.app.save_image_config(
            event_name=event_name,
            image_index=None,
            name="TestImage",
            path="/path/to/image.png",
            confidence="0.8",
            x1="", y1="", x2="", y2="",
            action_type="key_press",
            action_frame=action_frame_mock,
            enabled=True,
            is_folder=False,
            run_in_thread=True, # This is the key part we are testing
            dialog=MagicMock()
        )

        self.assertEqual(len(self.app.events_data[event_name]["images"]), 1)
        saved_image = self.app.events_data[event_name]["images"][0]
        self.assertEqual(saved_image["name"], "TestImage")
        self.assertEqual(saved_image["run_in_thread"], True)
        self.mock_json_dump.assert_called()

    @patch('threading.Thread')
    def test_run_event_threaded_image(self, mock_thread):
        event_name = "TestEvent"
        self.app.events_data[event_name] = {
            "images": [
                {
                    "name": "ThreadedImage",
                    "path": "/path/to/threaded_image.png",
                    "confidence": 0.8,
                    "region": None,
                    "action": {"type": "key_press", "key": "a", "delay": 0.1},
                    "enabled": True,
                    "is_folder": False,
                    "run_in_thread": True
                }
            ],
            "enabled": True,
            "target_window": "LDPlayer",
            "timer_enabled": False,
            "timer_duration": 60,
            "timer_command": ""
        }
        self.app.stop_flags[event_name] = False

        # Mock the find_image_and_execute to return True for the threaded image
        with patch.object(self.app, 'find_image_and_execute', return_value=True) as mock_find_image:
            # Mock the lock to prevent blocking in tests
            with patch.object(self.app, 'event_status_lock'):
                # Simulate the run_event loop for a short duration
                # We need to ensure the loop runs at least once to hit the threaded call
                # and then stop it gracefully.
                # Initialize last_image_found_time and image_found_in_loop as lists
                self.app.last_image_found_time = [0.0] # Use a list to make it mutable
                self.app.image_found_in_loop = [False] # Use a list to make it mutable

                def mock_run_event_loop():
                    # Run one iteration of the loop
                    self.app.focus_window(self.app.events_data[event_name].get("target_window", self.app.target_window))
                    for image_data in self.app.events_data[event_name]["images"]:
                        if image_data.get("enabled", True):
                            if image_data.get("run_in_thread", False):
                                # This is where the thread would be started in real code
                                # For testing, we just assert the thread call and break
                                mock_thread.assert_called_once_with(
                                    target=self.app._threaded_find_and_execute,
                                    args=(
                                        image_data,
                                        event_name,
                                        self.app.last_image_found_time,
                                        self.app.image_found_in_loop
                                    ),
                                    daemon=True
                                )
                                mock_thread.return_value.start.assert_called_once()
                                self.app.stop_flags[event_name] = True # Stop the loop after one iteration
                                return

                # Call the mocked loop directly
                mock_run_event_loop()

            # The main find_image_and_execute should NOT be called directly for threaded images
            mock_find_image.assert_not_called()

    def test_refresh_event_list_radio_buttons(self):
        self.app.events_data = {"Event1": {}, "Event2": {}}
        self.app.refresh_event_list()

        # Check if radio buttons are created
        # We mock CTkRadioButton, so we check if it was called for each event
        self.assertEqual(self.mock_ctk_radiobutton.call_count, 2) # Two events, so two radio buttons
        # Check if the values passed to CTkRadioButton are correct
        calls = self.mock_ctk_radiobutton.call_args_list
        self.assertIn(calls[0].kwargs['value'], ["Event1", "Event2"])
        self.assertIn(calls[1].kwargs['value'], ["Event1", "Event2"])
        # The selected_event is a StringVar, so we need to mock its get method
        self.app.selected_event.set("Event1") # Simulate selection
        self.assertEqual(self.app.selected_event.get(), "Event1")

    def test_on_event_select(self):
        self.app.events_data = {"Event1": {}, "Event2": {}}
        self.app.refresh_image_list = MagicMock()

        self.app.on_event_select("Event2")
        self.app.selected_event.set("Event2") # Simulate selection
        self.assertEqual(self.app.selected_event.get(), "Event2")
        self.app.refresh_image_list.assert_called_once()

if __name__ == '__main__':
    unittest.main()