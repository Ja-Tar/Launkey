![LAUNKEY BANNER](https://raw.githubusercontent.com/Ja-Tar/Launkey/refs/heads/main/bannerSmall.png)

> [!CAUTION]
> This project is in early development. Some features may not work as expected or may be missing.
> Please report any issues you encounter. THX :)

Launkey is a desktop application that allows you to create custom templates that then can be dragged and dropped on a table that represents a Launchpad device. When you press a button on the Launchpad, the app will trigger the keyboard shortcut that you assigned to that button in the template.


https://github.com/user-attachments/assets/a2fe8498-8232-4c6c-9928-d236b9c0e06e


## Features (mainly planed ones)

- [x] Test mode
- [ ] Lot of template types (like switch, slider)
- [ ] Launchpad compatibility *(for now it works only with LaunchPad Mini MK1)*
- [ ] And more...

# Important Info

## Test mode
If you don't have a Launchpad connected, you can still use the app in test mode. For example, to test the app or test if your template layout works.

You can find it in `Configuration` tab under `Test mode`. Click to enable or disable.

<img width="163" height="202" alt="obraz" src="https://github.com/user-attachments/assets/b55960fc-54f0-40fa-ba58-8add87de6ae5" />

Now you can see that new window opened. It's a shortcut display. It shows you shortcuts that are mapped to clicked buttons (blue) and side of the virtual launchpad (orange).

<img width="402" height="132" alt="obraz" src="https://github.com/user-attachments/assets/695ed428-e5dc-4708-8b2d-c70779f68b25" />

Now you can start testing with `Run` button.

![exampleTestMode](https://github.com/user-attachments/assets/fa350a2d-ebf1-4ba8-bddc-b49af97d32bb)

### Keyboard Layout

<img width="1235" height="371" alt="keyboard-layout(3)" src="https://github.com/user-attachments/assets/02e62839-cc09-4f92-ad1f-4de497e17322" />

In RED are the keys that are used for launchpad buttons (1-8, Q-I, A-L, Z-M).

In BLUE is a button that is used for changing the side of the launchpad (top 4 rows / bottom 4 rows).

## Troubleshooting launchpad connection

### Windows

On windows sometimes launchpad is not detected. First try to restart the PC with the launchpad connected. If it doesn't help, try to connect the launchpad to another USB port. You can also try to reinstall the drivers from [Novation's website](https://downloads.novationmusic.com/novation/). 

### Linux

For Linux you need to install `pygame` library for your distribution. For example on Ubuntu you can do it with:
```bash
sudo apt install python3-pygame
```

# Licenses and libraries

## keyboard (for shortcuts)
[Link](https://github.com/boppreh/keyboard?tab=MIT-1-ov-file)

[MIT License](https://github.com/boppreh/keyboard/blob/master/LICENSE.txt)

## launchpad.py
Author: [FMMT666](https://github.com/FMMT666)

[Link](https://github.com/FMMT666/launchpad.py)

[CC BY 4.0](https://github.com/FMMT666/launchpad.py/blob/master/LICENSE.txt)

## briefcase
[Link](https://github.com/beeware/briefcase)

[BSD 3-Clause "New" or "Revised" License](https://github.com/beeware/briefcase/blob/main/LICENSE)

# Thx HACKCLUB

This project was created during [HackClub](https://hackclub.com/) event [`Summer of Making`](https://summer.hackclub.com/). Thx for big motivation boost :)
