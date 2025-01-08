import pygame
import time

# Initialize pygame and the joystick
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected. Please connect your 8BitDo controller.")
else:
    controller = pygame.joystick.Joystick(0)
    controller.init()
    print(f"Controller detected: {controller.get_name()}")

    # List of axes to ignore (Ghost Axes)
    IGNORED_AXES = [4, 5]

    try:
        print("\nPress buttons, move sticks, and use the D-Pad.\nPress Ctrl+C to exit.\n")

        while True:
            pygame.event.pump()

            # 🕹️ Handle Buttons
            for i in range(controller.get_numbuttons()):
                if controller.get_button(i):
                    print(f"Button {i} pressed")
                    time.sleep(0.2)  # Prevent button spam

            # 🎮 Handle Axes (Analog Sticks)
            for i in range(controller.get_numaxes()):
                if i in IGNORED_AXES:
                    continue  # Skip ghost axes
                
                axis_value = controller.get_axis(i)
                if abs(axis_value) > 0.1:  # Deadzone filtering
                    print(f"Axis {i} moved: {axis_value:.2f}")
                    time.sleep(0.2)

            # ➡️ Handle Hat (D-Pad)
            for i in range(controller.get_numhats()):
                hat_value = controller.get_hat(i)
                if hat_value != (0, 0):
                    direction = ""
                    if hat_value == (0, 1):
                        direction = "Up"
                    elif hat_value == (0, -1):
                        direction = "Down"
                    elif hat_value == (1, 0):
                        direction = "Right"
                    elif hat_value == (-1, 0):
                        direction = "Left"
                    elif hat_value == (1, 1):
                        direction = "Up-Right"
                    elif hat_value == (-1, 1):
                        direction = "Up-Left"
                    elif hat_value == (1, -1):
                        direction = "Down-Right"
                    elif hat_value == (-1, -1):
                        direction = "Down-Left"

                    print(f"D-Pad moved: {direction}")
                    time.sleep(0.2)  # Prevent spam

    except KeyboardInterrupt:
        print("\nController test stopped by user.")
    finally:
        pygame.quit()
